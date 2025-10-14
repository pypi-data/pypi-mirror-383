# Copyright 2016: Mirantis Inc.
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

import abc
import collections
import threading
import typing as t
import typing_extensions as te

from rally.common import logging
from rally.common.plugin import plugin
from rally.common import utils as rutils
from rally.common import validation
from rally import consts
from rally import exceptions
from rally.task.processing import charts
from rally.task import scenario
from rally.task import utils

if t.TYPE_CHECKING:  # pragma: no cover
    from rally.common import objects

    A = t.TypeVar("A", bound="HookAction")
    T = t.TypeVar("T", bound="HookTrigger")


LOG = logging.getLogger(__name__)


configure = plugin.configure


class HookResult(t.TypedDict):
    """Structure for hook execution result."""
    status: str
    started_at: float
    finished_at: float
    triggered_by: dict[str, t.Any]
    error: te.NotRequired[dict[str, str]]
    output: te.NotRequired[scenario._Output]


class TriggerResults(t.TypedDict):
    """Structure for trigger results collection."""
    config: dict[str, t.Any]
    results: list[HookResult]
    summary: dict[str, int]


class HookExecutor:
    """Runs hooks and collects results from them."""

    def __init__(self, config: dict[str, t.Any], task: objects.Task) -> None:
        self.config = config
        self.task = task

        self.triggers: collections.defaultdict[str, list[HookTrigger]] = (
            collections.defaultdict(list))
        for hook_cfg in config.get("hooks", []):
            action_name = hook_cfg["action"][0]
            trigger_name = hook_cfg["trigger"][0]
            action_cls = HookAction.get(action_name)
            trigger_obj = HookTrigger.get(
                trigger_name)(hook_cfg, self.task, action_cls)
            event_type = trigger_obj.get_listening_event()
            self.triggers[event_type].append(trigger_obj)

        if "time" in self.triggers:
            self._timer_thread = threading.Thread(target=self._timer_method)
            self._timer_stop_event = threading.Event()

    def _timer_method(self) -> None:
        """Timer thread method.

        It generates events with type "time" to inform HookExecutor
        about how many time passed since beginning of the first iteration.
        """
        stopwatch = rutils.Stopwatch(stop_event=self._timer_stop_event)
        stopwatch.start()
        seconds_since_start = 0
        while not self._timer_stop_event.is_set():
            self.on_event(event_type="time", value=seconds_since_start)
            seconds_since_start += 1
            stopwatch.sleep(seconds_since_start)

    def _start_timer(self) -> None:
        self._timer_thread.start()

    def _stop_timer(self) -> None:
        self._timer_stop_event.set()
        if self._timer_thread.ident is not None:
            self._timer_thread.join()

    def on_event(self, event_type: str, value: t.Any) -> None:
        """Notify about event.

        This method should be called to inform HookExecutor that
        particular event occurred.
        It runs hooks configured for event.
        """
        if "time" in self.triggers:
            # start timer on first iteration
            if event_type == "iteration" and value == 1:
                self._start_timer()

        for trigger_obj in self.triggers[event_type]:
            started = trigger_obj.on_event(event_type, value)
            if started:
                LOG.info("Hook %s is trigged for Task %s by %s=%s"
                         % (trigger_obj.hook_cls.__name__, self.task["uuid"],
                            event_type, value))

    def results(self) -> list[TriggerResults]:
        """Returns list of dicts with hook results."""
        if "time" in self.triggers:
            self._stop_timer()
        results = []
        for triggers_group in self.triggers.values():
            for trigger_obj in triggers_group:
                results.append(trigger_obj.get_results())
        return results


@validation.add_default("jsonschema")
@plugin.base()
class HookAction(plugin.Plugin, validation.ValidatablePluginMixin,
                 metaclass=abc.ABCMeta):
    """Factory for hook classes."""

    CONFIG_SCHEMA: dict = {"type": "null"}

    def __init__(
        self,
        task: objects.Task,
        config: t.Any,
        triggered_by: dict[str, t.Any]
    ) -> None:
        self.task = task
        self.config = config
        self._triggered_by = triggered_by
        self._thread = threading.Thread(target=self._thread_method)
        self._started_at = 0.0
        self._finished_at = 0.0
        self._result: HookResult = {
            "status": consts.HookStatus.SUCCESS,
            "started_at": self._started_at,
            "finished_at": self._finished_at,
            "triggered_by": self._triggered_by,
        }

    def _thread_method(self) -> None:
        # Run hook synchronously
        self.run_sync()

    def set_error(
        self, exception_name: str, description: str, details: str
    ) -> None:
        """Set error related information to result.

        :param exception_name: name of exception as string
        :param description: short description as string
        :param details: any details as string
        """
        self.set_status(consts.HookStatus.FAILED)
        self._result["error"] = {"etype": exception_name,
                                 "msg": description, "details": details}

    def set_status(self, status: str) -> None:
        """Set status to result."""
        self._result["status"] = status

    def add_output(
        self,
        additive: dict[str, t.Any] | None = None,
        complete: dict[str, t.Any] | None = None
    ) -> None:
        """Save custom output.

        :param additive: dict with additive output
        :param complete: dict with complete output
        :raises RallyException: if output has wrong format
        """
        if "output" not in self._result:
            self._result["output"] = {"additive": [], "complete": []}
        for key, value in (("additive", additive), ("complete", complete)):
            if value:
                message = charts.validate_output(key, value)
                if message:
                    raise exceptions.RallyException(message)
                self._result["output"][
                    key  # type: ignore[literal-required]
                ].append(value)

    def run_async(self) -> None:
        """Run hook asynchronously."""
        self._thread.start()

    def run_sync(self) -> None:
        """Run hook synchronously."""
        try:
            with rutils.Timer() as timer:
                self.run()
        except Exception as exc:
            LOG.exception("Hook %s failed during run." % self.get_name())
            self.set_error(*utils.format_exc(exc))

        self._started_at = timer.timestamp()
        self._result["started_at"] = self._started_at
        self._finished_at = timer.finish_timestamp()
        self._result["finished_at"] = self._finished_at

    @abc.abstractmethod
    def run(self) -> None:
        """Run method.

        This method should be implemented in plugin.

        Hook plugin should call following methods to set result:
            set_status - to set hook execution status
        Optionally the following methods should be called:
            set_error - to indicate that there was an error;
                        automatically sets hook execution status to 'failed'
            add_output - provide data for report
        """

    def result(self) -> HookResult:
        """Wait and return result of hook."""
        if self._thread.ident is not None:
            # hook is still running, wait for result
            self._thread.join()
        return t.cast(HookResult, self._result)


@validation.add_default("jsonschema")
@plugin.base()
class HookTrigger(plugin.Plugin, validation.ValidatablePluginMixin,
                  metaclass=abc.ABCMeta):
    """Factory for hook trigger classes."""

    CONFIG_SCHEMA: dict = {"type": "null"}

    def __init__(
        self,
        hook_cfg: dict[str, t.Any],
        task: objects.Task,
        hook_cls: type[HookAction]
    ) -> None:
        self.hook_cfg = hook_cfg
        self.config = self.hook_cfg["trigger"][1]
        self.task = task
        self.hook_cls = hook_cls
        self._runs: list[HookAction] = []

    @abc.abstractmethod
    def get_listening_event(self) -> str:
        """Returns event type to listen."""

    def on_event(self, event_type: str, value: t.Any = None) -> bool:
        """Launch hook on specified event."""
        LOG.info("Hook action %s is triggered for Task %s by %s=%s"
                 % (self.hook_cls.get_name(), self.task["uuid"],
                    event_type, value))
        action_cfg = self.hook_cfg["action"][1]
        action = self.hook_cls(self.task, action_cfg,
                               {"event_type": event_type, "value": value})
        action.run_async()
        self._runs.append(action)
        return True

    def get_results(self) -> TriggerResults:
        results: TriggerResults = {
            "config": self.hook_cfg,
            "results": [],
            "summary": {}
        }
        for action in self._runs:
            action_result = action.result()
            results["results"].append(action_result)
            results["summary"].setdefault(action_result["status"], 0)
            results["summary"][action_result["status"]] += 1
        return results
