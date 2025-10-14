# Copyright 2015: Mirantis Inc.
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

import functools
import os
import typing as t
import typing_extensions as te

from rally.common.plugin import discover

if t.TYPE_CHECKING:
    P = te.ParamSpec("P")
    R = t.TypeVar("R")


PLUGINS_LOADED = False


def load() -> None:
    global PLUGINS_LOADED

    if not PLUGINS_LOADED:
        from rally.common import opts

        opts.register()

        # NOTE(andreykurilin): `rally.plugins.common` includes deprecated
        #   modules. As soon as they will be removed the direct import of
        #   validators should be replaced by
        #
        #       discover.import_modules_from_package("rally.plugins.common")
        from rally.plugins.common import validators  # noqa: F401

        discover.import_modules_from_package("rally.plugins.task")
        discover.import_modules_from_package("rally.plugins.verification")

        packages = discover.find_packages_by_entry_point()
        for package in packages:
            if "options" in package:
                opts.register_options_from_path(package["options"])
        discover.import_modules_by_entry_point(_packages=packages)

        discover.load_plugins("/opt/rally/plugins/")
        discover.load_plugins(os.path.expanduser("~/.rally/plugins/"))

    PLUGINS_LOADED = True


def ensure_plugins_are_loaded(func: t.Callable[P, R]) -> t.Callable[P, R]:
    @functools.wraps(func)
    def wrapper(*args: t.Any, **kwargs: t.Any) -> R:
        load()
        return func(*args, **kwargs)
    return wrapper
