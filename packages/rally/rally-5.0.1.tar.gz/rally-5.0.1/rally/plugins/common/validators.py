# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from __future__ import annotations

import inspect
import os
import typing as t

import jsonschema

from rally.common import logging
from rally.common import validation
from rally import exceptions
from rally.task import context as context_lib

if t.TYPE_CHECKING:  # pragma: no cover
    from rally.common.plugin import plugin
    from rally.task import scenario

    import jsonschema.protocols

LOG = logging.getLogger(__name__)


@validation.configure(name="jsonschema")
class JsonSchemaValidator(validation.Validator):
    """JSON schema validator"""

    def validate(
        self,
        context: dict[str, t.Any],
        config: dict[str, t.Any] | None,
        plugin_cls: type[plugin.Plugin],
        plugin_cfg: dict[str, t.Any] | None
    ) -> None:
        schema = getattr(plugin_cls, "CONFIG_SCHEMA", {"type": "null"})

        validator = jsonschema.validators.validator_for(
            schema,
            default=t.cast(
                type[jsonschema.protocols.Validator],
                jsonschema.Draft7Validator
            )
        )
        try:
            jsonschema.validate(
                plugin_cfg, schema,
                cls=validator  # type: ignore[arg-type]
            )
        except jsonschema.ValidationError as err:
            self.fail(str(err))


@validation.configure(name="args-spec")
class ArgsValidator(validation.Validator):
    """Scenario arguments validator"""

    def validate(
        self,
        context: dict[str, t.Any],
        config: dict[str, t.Any] | None,
        plugin_cls: type[scenario.Scenario],  # type: ignore[override]
        plugin_cfg: dict[str, t.Any] | None
    ) -> None:
        scenario_cls = plugin_cls
        name = scenario_cls.get_name()
        platform = scenario_cls.get_platform()

        args_spec = inspect.signature(scenario_cls.run).parameters
        missed_args = [
            p.name
            for i, p in enumerate(args_spec.values())
            if (i != 0  # first argument is self-argument, i.e instance of cls
                and p.default == inspect.Parameter.empty
                and p.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD)
        ]

        hint_msg = (" Use `rally plugin show --name %s --platform %s` "
                    "to display scenario description." % (name, platform))

        if config is not None and "args" in config:
            missed_args = sorted(set(missed_args) - set(config["args"]))
        if missed_args:
            msg = ("Argument(s) '%(args)s' should be specified in task config."
                   "%(hint)s" % {"args": "', '".join(missed_args),
                                 "hint": hint_msg})
            self.fail(msg)

        support_kwargs = any(
            p for p in args_spec.values()
            if p.kind == inspect.Parameter.VAR_KEYWORD
        )

        if not support_kwargs and config is not None and "args" in config:
            redundant_args = [p for p in config["args"] if p not in args_spec]
            if redundant_args:
                msg = ("Unexpected argument(s) found ['%(args)s'].%(hint)s" %
                       {"args": "', '".join(redundant_args),
                        "hint": hint_msg})
                self.fail(msg)


@validation.configure(name="required_params")
class RequiredParameterValidator(validation.Validator):
    """Scenario required parameter validator.

    This allows us to search required parameters in subdict of config.

    :param subdict: sub-dict of "config" to search. if
                    not defined - will search in "config"
    :param params: list of required parameters. If item is list/tuple,
        the nested items will be treated as oneOf options.
    """

    def __init__(
        self,
        params: list[str | tuple[str, ...] | list[str]] | None = None,
        subdict: str | None = None
    ) -> None:
        super(RequiredParameterValidator, self).__init__()
        self.subdict = subdict
        self.params = params or []

    def validate(
        self,
        context: dict[str, t.Any],
        config: dict[str, t.Any] | None,
        plugin_cls: type[plugin.Plugin],
        plugin_cfg: dict[str, t.Any] | None
    ) -> None:
        missing: list[str] = []
        args: dict[str, t.Any] = config.get("args", {}) if config else {}

        if self.subdict:
            args = args.get(self.subdict, {})
        for arg in self.params:
            if isinstance(arg, (tuple, list)):
                for case in arg:
                    if case in args:
                        break
                else:
                    arg_str = "'/'".join(arg)
                    missing.append("'%s' (at least one parameter should be "
                                   "specified)" % arg_str)
            else:
                if arg not in args:
                    missing.append("'%s'" % arg)

        if missing:
            msg = ("%s parameter(s) are not defined in "
                   "the input task file") % ", ".join(missing)
            self.fail(msg)


@validation.configure(name="number")
class NumberValidator(validation.Validator):
    """Checks that parameter is a number that pass specified condition.

    Ensure a parameter is within the range [minval, maxval]. This is a
    closed interval so the end points are included.

    :param param_name: Name of parameter to validate
    :param minval: Lower endpoint of valid interval
    :param maxval: Upper endpoint of valid interval
    :param nullable: Allow parameter not specified, or parameter=None
    :param integer_only: Only accept integers
    """

    def __init__(
        self,
        param_name: str,
        minval: int | float | None = None,
        maxval: int | float | None = None,
        nullable: bool = False,
        integer_only: bool = False
    ) -> None:
        self.param_name = param_name
        self.minval = minval
        self.maxval = maxval
        self.nullable = nullable
        self.integer_only = integer_only

    def validate(
        self,
        context: dict[str, t.Any],
        config: dict[str, t.Any] | None,
        plugin_cls: type[plugin.Plugin],
        plugin_cfg: dict[str, t.Any] | None
    ) -> None:
        value: t.Any = None
        if config is not None:
            value = config.get("args", {}).get(self.param_name)

        num_func: type[int] | type[float] = float
        if self.integer_only:
            # NOTE(boris-42): Force check that passed value is not float, this
            #   is important cause int(float_numb) won't raise exception
            if isinstance(value, float):
                self.fail("%(name)s is %(val)s which hasn't int type"
                          % {"name": self.param_name, "val": value})
            num_func = int

        # None may be valid if the scenario sets a sensible default.
        if self.nullable and value is None:
            return

        try:
            number = num_func(value)
            if self.minval is not None and number < self.minval:
                self.fail("%(name)s is %(val)s which is less than the minimum "
                          "(%(min)s)" % {"name": self.param_name,
                                         "val": number,
                                         "min": self.minval})
            if self.maxval is not None and number > self.maxval:
                self.fail("%(name)s is %(val)s which is greater than the "
                          "maximum (%(max)s)" % {"name": self.param_name,
                                                 "val": number,
                                                 "max": self.maxval})
        except (ValueError, TypeError):
            self.fail("%(name)s is %(val)s which is not a valid %(type)s" %
                      {"name": self.param_name, "val": value,
                       "type": num_func.__name__})


@validation.configure(name="enum")
class EnumValidator(validation.Validator):
    """Checks that parameter is in a list.

    Ensure a parameter has the right value. This value need to be defined
    in a list.

    :param param_name: Name of parameter to validate
    :param values: List of values accepted
    :param missed: Allow to accept optional parameter
    :param case_insensitive: Ignore case in enum values
    """

    def __init__(
        self,
        param_name: str,
        values: list[t.Any],
        missed: bool = False,
        case_insensitive: bool = False
    ) -> None:
        self.param_name = param_name
        self.missed = missed
        self.case_insensitive = case_insensitive
        if self.case_insensitive:
            self.values: list[t.Any] = []
            for value in values:
                if isinstance(value, str):
                    value = value.lower()
                self.values.append(value)
        else:
            self.values = values

    def validate(
        self,
        context: dict[str, t.Any],
        config: dict[str, t.Any] | None,
        plugin_cls: type[plugin.Plugin],
        plugin_cfg: dict[str, t.Any] | None
    ) -> None:
        value = None
        if config is not None:
            value = config.get("args", {}).get(self.param_name)
        if value:
            if self.case_insensitive:
                if isinstance(value, str):
                    value = value.lower()

            if value not in self.values:
                self.fail("%(name)s is %(val)s which is not a valid value "
                          "from %(list)s" % {"name": self.param_name,
                                             "val": value,
                                             "list": self.values})
        else:
            if not self.missed:
                self.fail("%s parameter is not defined in the task config file"
                          % self.param_name)


@validation.configure(name="map_keys")
class MapKeysParameterValidator(validation.Validator):
    """Check that parameter contains specified keys.

    :param param_name: Name of parameter to validate
    :param required: List of all required keys
    :param allowed: List of all allowed keys
    :param additional: Whether additional keys are allowed. If list of allowed
           keys are specified, defaults to False, otherwise defaults to True
    :param missed: Allow to accept optional parameter
    """

    def __init__(
        self,
        param_name: str,
        required: list[str] | None = None,
        allowed: list[str] | None = None,
        additional: bool = True,
        missed: bool = False
    ) -> None:
        super(MapKeysParameterValidator, self).__init__()
        self.param_name = param_name
        self.required = required or []
        self.allowed = allowed or []
        self.additional = additional
        self.missed = missed

    def validate(
        self,
        context: dict[str, t.Any],
        config: dict[str, t.Any] | None,
        plugin_cls: type[plugin.Plugin],
        plugin_cfg: dict[str, t.Any] | None
    ) -> None:
        parameter = None
        if config is not None:
            parameter = config.get("args", {}).get(self.param_name)

        if parameter:
            required_diff = set(self.required) - set(parameter.keys())
            if required_diff:
                self.fail(
                    "Required keys is missing in '%(name)s' parameter: "
                    "%(key)s" % {"name": self.param_name,
                                 "key": ", ".join(sorted(list(required_diff)))}
                )

            if self.allowed:
                allowed_diff = set(parameter.keys()) - set(self.allowed)
                if allowed_diff:
                    self.fail(
                        "Parameter '%(name)s' contains unallowed keys: "
                        "%(key)s" % {
                            "name": self.param_name,
                            "key": ", ".join(sorted(list(allowed_diff)))}
                    )
            elif not self.additional:
                diff = set(parameter.keys()) - set(self.required)
                if diff:
                    self.fail(
                        "Parameter '%(name)s' contains unallowed keys: "
                        "%(key)s" % {
                            "name": self.param_name,
                            "key": ", ".join(sorted(list(diff)))}
                    )
        elif not self.missed:
            self.fail("'%s' parameter is not defined in the task config file"
                      % self.param_name)


@validation.configure(name="restricted_parameters")
class RestrictedParametersValidator(validation.Validator):

    def __init__(
        self, param_names: str | list[str] | tuple[str, ...],
        subdict: str | None = None
    ) -> None:
        """Validates that parameters is not set.

        :param param_names: parameter or parameters list to be validated.
        :param subdict: sub-dict of "config" to search for param_names. if
                        not defined - will search in "config"
        """
        super(RestrictedParametersValidator, self).__init__()
        if isinstance(param_names, (list, tuple)):
            self.params = param_names
        else:
            self.params = [param_names]
        self.subdict = subdict

    def validate(
        self,
        context: dict[str, t.Any],
        config: dict[str, t.Any] | None,
        plugin_cls: type[plugin.Plugin],
        plugin_cfg: dict[str, t.Any] | None
    ) -> None:
        restricted_params: list[str] = []
        args: dict[str, t.Any] = config.get("args", {}) if config else {}
        for param_name in self.params:
            source = (args.get(self.subdict) or {}) if self.subdict else args
            if param_name in source:
                restricted_params.append(param_name)
        if restricted_params:
            self.fail("You can't specify parameters '%s' in '%s'" % (
                ", ".join(restricted_params),
                self.subdict if self.subdict else "args"))


@validation.configure(name="required_contexts")
class RequiredContextsValidator(validation.Validator):

    def __init__(
        self, *args: str,
        contexts: t.Iterable[str | tuple[str, ...]] | None = None
    ) -> None:
        """Validator checks if required contexts are specified.

        :param contexts: list of strings and tuples with context names that
                         should be specified. Tuple represent 'at least one
                         of the'.
        """
        super(RequiredContextsValidator, self).__init__()
        if isinstance(contexts, (list, tuple)):
            # services argument is a list, so it is a new way of validators
            #  usage, args in this case should not be provided
            self.contexts: list[str | tuple[str, ...]] = list(contexts)
            if args:
                LOG.warning("Positional argument is not what "
                            "'required_context' decorator expects. "
                            "Use only `contexts` argument instead")
        else:
            # it is an old way validator
            self.contexts = []
            if contexts:
                self.contexts.append(t.cast(tuple[str, ...], contexts))
            self.contexts.extend(args)

    @staticmethod
    def _match(
        requested_ctx_name: str, input_contexts: dict[str, t.Any]
    ) -> bool:
        requested_ctx_name_extended = f"{requested_ctx_name}@"
        for input_ctx_name in input_contexts:
            if (requested_ctx_name == input_ctx_name
                    or input_ctx_name.startswith(requested_ctx_name_extended)):
                return True

        if "@" in requested_ctx_name:
            platform_aware_name, platform = requested_ctx_name.split("@")
            if platform_aware_name in input_contexts:
                try:
                    ctx_cls = context_lib.Context.get(requested_ctx_name)
                except (exceptions.PluginNotFound,
                        exceptions.MultiplePluginsFound):
                    return False
                return ctx_cls.get_platform() == platform

        return False

    def validate(
        self,
        context: dict[str, t.Any],
        config: dict[str, t.Any] | None,
        plugin_cls: type[plugin.Plugin],
        plugin_cfg: dict[str, t.Any] | None
    ) -> None:
        missing_contexts: list[str] = []
        input_contexts: dict[str, t.Any] = {}
        if config is not None:
            input_contexts = config.get("contexts", {})

        for required_ctx in self.contexts:
            if isinstance(required_ctx, tuple):
                if not any(self._match(r_ctx, input_contexts)
                           for r_ctx in required_ctx):
                    # formatted string like: 'foo or bar or baz'
                    formatted_names = "'%s'" % " or ".join(required_ctx)
                    missing_contexts.append(formatted_names)
            else:
                if not self._match(required_ctx, input_contexts):
                    missing_contexts.append(required_ctx)

        if missing_contexts:
            self.fail("The following context(s) are required but missing from "
                      "the input task file: %s" % ", ".join(missing_contexts))


@validation.configure(name="required_param_or_context")
class RequiredParamOrContextValidator(validation.Validator):

    def __init__(self, param_name: str, ctx_name: str) -> None:
        """Validator checks if required image is specified.

        :param param_name: name of parameter
        :param ctx_name: name of context
        """
        super(RequiredParamOrContextValidator, self).__init__()
        self.param_name = param_name
        self.ctx_name = ctx_name

    def validate(
        self,
        context: dict[str, t.Any],
        config: dict[str, t.Any] | None,
        plugin_cls: type[plugin.Plugin],
        plugin_cfg: dict[str, t.Any] | None
    ) -> None:
        msg = ("You should specify either scenario argument %s or"
               " use context %s." % (self.param_name, self.ctx_name))

        if config is not None:
            if self.ctx_name in config.get("contexts", {}):
                return
            if self.param_name in config.get("args", {}):
                return
        self.fail(msg)


@validation.configure(name="file_exists")
class FileExistsValidator(validation.Validator):

    def __init__(
        self, param_name: str, mode: int = os.R_OK, required: bool = True
    ) -> None:
        """Validator checks parameter is proper path to file with proper mode.

        Ensure a file exists and can be accessed with the specified mode.
        Note that path to file will be expanded before access checking.

        :param param_name: Name of parameter to validate
        :param mode: Access mode to test for. This should be one of:
            * os.F_OK (file exists)
            * os.R_OK (file is readable)
            * os.W_OK (file is writable)
            * os.X_OK (file is executable)

            If multiple modes are required they can be added, eg:
                mode=os.R_OK+os.W_OK
        :param required: Boolean indicating whether this argument is required.
        """
        super(FileExistsValidator, self).__init__()

        self.param_name = param_name
        self.mode = mode
        self.required = required

    def _file_access_ok(
        self, filename: str | None, mode: int, param_name: str,
        required: bool = True
    ) -> None:
        if not filename:
            if not required:
                return
            self.fail("Parameter %s required" % param_name)
        if not os.access(os.path.expanduser(filename), mode):
            self.fail("Could not open %(filename)s with mode %(mode)s for "
                      "parameter %(param_name)s" % {"filename": filename,
                                                    "mode": mode,
                                                    "param_name": param_name})

    def validate(
        self,
        context: dict[str, t.Any],
        config: dict[str, t.Any] | None,
        plugin_cls: type[plugin.Plugin],
        plugin_cfg: dict[str, t.Any] | None
    ) -> None:
        filename = None
        if config is not None:
            filename = config.get("args", {}).get(self.param_name)

        self._file_access_ok(filename, self.mode, self.param_name,
                             self.required)
