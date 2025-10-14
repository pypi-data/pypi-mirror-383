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
#

from __future__ import annotations

import typing as t
import typing_extensions as te

if t.TYPE_CHECKING:  # pragma: no cover
    import datetime as dt

from subunit import v2  # type: ignore[import-untyped]

from rally.common import logging
from rally.utils import encodeutils


class TestResult(t.TypedDict):
    status: str
    name: str
    duration: str
    tags: list[str]
    timestamp: te.NotRequired[str]
    reason: te.NotRequired[str | bytes]
    traceback: te.NotRequired[str | bytes]


class UnknownEntity(t.TypedDict):
    name: str
    status: te.NotRequired[str]
    reason: te.NotRequired[str | bytes]
    traceback: te.NotRequired[str | bytes]


class TotalsDict(t.TypedDict):
    tests_count: int
    tests_duration: str
    failures: int
    skipped: int
    success: int
    unexpected_success: int
    expected_failures: int


_IGNORE_LIST = [
    "subunit.parser"
]


class TestID(str):

    @staticmethod
    def __new__(cls, value: str) -> TestID:
        if (value.startswith("setUpClass (")
                or value.startswith("tearDown (")):
            value = value[value.find("(") + 1:-1]
        return super(TestID, cls).__new__(cls, value)

    def __init__(self, value: str) -> None:
        if self.find("[") > -1:
            self.name, tags = self.split("[", 1)
            self.tags = tags[:-1].split(",")
        else:
            self.name = value
            self.tags = []


class SubunitV2StreamResult(object):

    def __init__(
        self,
        expected_failures: dict[str, str] | None = None,
        skipped_tests: dict[str, str] | None = None,
        live: bool = False,
        logger_name: str | None = None,
    ) -> None:
        self._tests: dict[TestID, TestResult] = {}
        self._expected_failures = expected_failures or {}
        self._skipped_tests = skipped_tests or {}

        self._live = live
        self._logger = logging.getLogger(logger_name or __name__)

        self._timestamps: dict[TestID, dt.datetime] = {}
        # NOTE(andreykurilin): _first_timestamp and _last_timestamp variables
        # are designed to calculate the total time of tests execution.
        self._first_timestamp: dt.datetime | None = None
        self._last_timestamp: dt.datetime | None = None

        # Store unknown entities and process them later.
        self._unknown_entities: dict[TestID, UnknownEntity] = {}
        self._is_parsed = False

    def _check_expected_failure(self, test_id: TestID) -> None:
        if (test_id in self._expected_failures
                or test_id.name in self._expected_failures):
            if self._tests[test_id]["status"] == "fail":
                self._tests[test_id]["status"] = "xfail"
                if self._expected_failures[test_id]:
                    self._tests[test_id]["reason"] = (
                        self._expected_failures[test_id])
            elif self._tests[test_id]["status"] == "success":
                self._tests[test_id]["status"] = "uxsuccess"

    def _process_skipped_tests(self) -> None:
        for t_id in self._skipped_tests.copy():
            if t_id not in self._tests:
                status = "skip"
                t_id = TestID(t_id)
                self._tests[t_id] = {"status": status,
                                     "name": t_id.name,
                                     "duration": "%.3f" % 0,
                                     "tags": t_id.tags}
                if self._skipped_tests[t_id]:
                    self._tests[t_id]["reason"] = self._skipped_tests[t_id]
                    status += ": %s" % encodeutils.safe_decode(
                        self._tests[t_id]["reason"]
                    )
                if self._live:
                    self._logger.info("{-} %s ... %s" % (t_id.name, status))

            self._skipped_tests.pop(t_id)

    def _parse(self) -> None:
        # NOTE(andreykurilin): When whole test class is marked as skipped or
        # failed, there is only one event with reason and status. So we should
        # modify all tests of test class manually.
        for test_id in self._unknown_entities:
            known_test_ids = filter(
                lambda t: t == test_id or t.startswith("%s." % test_id),
                self._tests)
            for t_id in known_test_ids:
                if self._tests[t_id]["status"] == "init":
                    self._tests[t_id]["status"] = (
                        self._unknown_entities[test_id]["status"])

                if self._unknown_entities[test_id].get("reason"):
                    self._tests[t_id]["reason"] = (
                        self._unknown_entities[test_id]["reason"])
                elif self._unknown_entities[test_id].get("traceback"):
                    self._tests[t_id]["traceback"] = (
                        self._unknown_entities[test_id]["traceback"])

        # decode data
        for test_id in self._tests:
            for file_name in ["traceback", "reason"]:
                if file_name not in self._tests[test_id]:
                    continue
                # TODO(andreykurilin): decode fields based on mime_type
                self._tests[test_id][
                    file_name  # type: ignore[literal-required]
                ] = encodeutils.safe_decode(
                    self._tests[test_id][
                        file_name  # type: ignore[literal-required]
                    ]
                )

        self._is_parsed = True

    @property
    def tests(self) -> dict[TestID, TestResult]:
        if not self._is_parsed:
            self._parse()
        return self._tests

    @property
    def totals(self) -> TotalsDict:
        td = 0.0
        if self._first_timestamp and self._last_timestamp:
            td = (self._last_timestamp - self._first_timestamp).total_seconds()

        return {"tests_count": len(self.tests),
                "tests_duration": "%.3f" % td,
                "failures": len(self.filter_tests("fail")),
                "skipped": len(self.filter_tests("skip")),
                "success": len(self.filter_tests("success")),
                "unexpected_success": len(self.filter_tests("uxsuccess")),
                "expected_failures": len(self.filter_tests("xfail"))}

    def status(
        self,
        test_id: str | None = None,
        test_status: str | None = None,
        timestamp: dt.datetime | None = None,
        file_name: str | None = None,
        file_bytes: bytes | memoryview | None = None,
        mime_type: str | None = None,
        test_tags: list[str] | None = None,
        runnable: bool = True,
        eof: bool = False,
        route_code: str | None = None,
    ) -> None:

        if not test_id or test_id in _IGNORE_LIST:
            return

        test_id = TestID(test_id)
        if isinstance(file_bytes, memoryview):
            file_bytes = file_bytes.tobytes()

        if timestamp:
            if not self._first_timestamp:
                self._first_timestamp = timestamp
            self._last_timestamp = timestamp

        if test_status == "exists":
            self._tests[test_id] = {"status": "init",
                                    "name": test_id.name,
                                    "duration": "%.3f" % 0,
                                    "tags": test_id.tags}
        elif test_id in self._tests:
            if test_status == "inprogress":
                # timestamp of test start
                if timestamp:
                    self._timestamps[test_id] = timestamp
                    self._tests[test_id]["timestamp"] = timestamp.strftime(
                        "%Y-%m-%dT%H:%M:%S%z")
            elif test_status:
                if timestamp:
                    self._tests[test_id]["duration"] = "%.3f" % (
                        timestamp - self._timestamps[test_id]).total_seconds()
                self._tests[test_id]["status"] = test_status

                self._check_expected_failure(test_id)
            else:
                if file_name in ["traceback", "reason"]:
                    if file_name not in self._tests[test_id]:
                        self._tests[test_id][
                            file_name  # type: ignore[literal-required]
                        ] = file_bytes
                    else:
                        self._tests[test_id][
                            file_name  # type: ignore[literal-required]
                        ] += file_bytes
        else:
            self._unknown_entities.setdefault(test_id, {"name": test_id})

            if test_status is not None:
                self._unknown_entities[test_id]["status"] = test_status
            if file_name in ["traceback", "reason"]:
                if file_name not in self._unknown_entities[test_id]:
                    self._unknown_entities[test_id][
                        file_name  # type: ignore[literal-required]
                    ] = file_bytes
                else:
                    self._unknown_entities[test_id][
                        file_name  # type: ignore[literal-required]
                    ] += file_bytes

        if self._skipped_tests:
            self._process_skipped_tests()

        if self._live and test_status not in (None, "exists", "inprogress"):
            duration = ""
            if test_id in self._tests:
                status = self._tests[test_id]["status"]
                duration = " [%ss]" % self._tests[test_id]["duration"]
            else:
                status = test_status or ""

            status += duration

            if "xfail" in status or "skip" in status:
                if test_id in self._tests:
                    reason = self._tests[test_id].get("reason")
                else:
                    reason = self._unknown_entities[test_id].get("reason")
                if reason:
                    status += ": %s" % encodeutils.safe_decode(reason)

            w = "{%s} " % test_tags.pop().split("-")[1] if test_tags else "-"
            self._logger.info(f"{w}{test_id.name} ... {status}")

    def filter_tests(self, status: str) -> dict[TestID, TestResult]:
        """Filter tests by given status."""
        filtered_tests = {}
        for test in self.tests:
            if self.tests[test]["status"] == status:
                filtered_tests[test] = self.tests[test]

        return filtered_tests


def parse(
    stream: t.IO[bytes] | t.IO[str],
    expected_failures: dict[str, str] | None = None,
    skipped_tests: dict[str, str] | None = None,
    live: bool = False,
    logger_name: str | None = None,
) -> SubunitV2StreamResult:
    results = SubunitV2StreamResult(expected_failures, skipped_tests, live,
                                    logger_name)
    v2.ByteStreamToStreamResult(stream, "non-subunit").run(results)

    return results


def parse_file(
    filename: str,
    expected_failures: dict[str, str] | None = None,
    skipped_tests: dict[str, str] | None = None,
    live: bool = False,
    logger_name: str | None = None,
) -> SubunitV2StreamResult:
    with open(filename, "rb") as stream:
        return parse(stream, expected_failures, skipped_tests, live,
                     logger_name)
