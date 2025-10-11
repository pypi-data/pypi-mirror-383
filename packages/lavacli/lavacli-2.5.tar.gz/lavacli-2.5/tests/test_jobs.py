# vim: set ts=4

# Copyright 2018 Rémi Duraffort
# This file is part of lavacli.
#
# lavacli is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# lavacli is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with lavacli.  If not, see <http://www.gnu.org/licenses/>

import json
import sys
import time
import xmlrpc.client

from lavacli import main
from lavacli.utils import safe_yaml


def test_jobs_cancel(setup, monkeypatch, capsys):
    version = "2019.1"
    monkeypatch.setattr(sys, "argv", ["lavacli", "jobs", "cancel", "1234"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {"request": "scheduler.jobs.cancel", "args": ("1234",), "ret": None},
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == ""  # nosec


def test_jobs_autocancel(setup, monkeypatch, capsys):
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "jobs", "autocancel", "--duration", "1440"]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": "2023.10"},
            {
                "request": "scheduler.jobs.list",
                "args": ("RUNNING", None, 0, 100, None, False, 1440),
                "ret": [
                    {
                        "id": "16",
                        "description": "hello",
                        "device_type": "bbb",
                        "health": "Unknown",
                        "state": "Running",
                        "submitter": "lava",
                    },
                    {
                        "id": "17",
                        "description": "something",
                        "device_type": "qemu",
                        "health": "Unknown",
                        "state": "Running",
                        "submitter": "admin",
                    },
                ],
            },
            {
                "request": "scheduler.jobs.definition",
                "args": ("16",),
                "ret": "timeouts:\n  job:\n    minutes: 720\n",
            },
            {"request": "scheduler.jobs.cancel", "args": ("16",), "ret": None},
            {
                "request": "scheduler.jobs.definition",
                "args": ("17",),
                "ret": "timeouts:\n  job:\n    minutes: 1445\n",
            },
            {
                "request": "scheduler.jobs.list",
                "args": ("RUNNING", None, 0, 100, None, False, 1440),
                "ret": [],
            },
        ],
    )
    assert main() == 0
    assert (
        capsys.readouterr()[0]
        == """[CANCELED] 16: [lava] (hello) - bbb
[  SKIP  ] 17: [admin] (something) - qemu - timeout not reached yet\n"""
    )


def test_jobs_config(setup, monkeypatch, capsys, tmp_path):
    version = "2019.1"
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "jobs", "config", "1234", "--dest", str(tmp_path)]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.jobs.configuration",
                "args": ("1234",),
                "ret": ["definition", "device", "dispatcher", "env", "env.dut"],
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == ""  # nosec
    with (tmp_path / "definition.yaml").open() as f_in:
        assert f_in.read() == "definition"  # nosec
    with (tmp_path / "device.yaml").open() as f_in:
        assert f_in.read() == "device"  # nosec
    with (tmp_path / "dispatcher.yaml").open() as f_in:
        assert f_in.read() == "dispatcher"  # nosec
    with (tmp_path / "env.yaml").open() as f_in:
        assert f_in.read() == "env"  # nosec
    with (tmp_path / "env.dut.yaml").open() as f_in:
        assert f_in.read() == "env.dut"  # nosec


def test_jobs_definition(setup, monkeypatch, capsys):
    version = "2019.1"
    monkeypatch.setattr(sys, "argv", ["lavacli", "jobs", "definition", "1234"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.jobs.definition",
                "args": ("1234",),
                "ret": "definition",
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "definition\n"  # nosec


def test_jobs_list(setup, monkeypatch, capsys):
    version = "2019.1"
    monkeypatch.setattr(sys, "argv", ["lavacli", "jobs", "list"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.jobs.list",
                "args": (None, None, 0, 25, 0, False),
                "ret": [
                    {
                        "id": "16",
                        "description": "hello",
                        "device_type": "bbb",
                        "health": "Complete",
                        "state": "Finished",
                        "submitter": "lava",
                    },
                    {
                        "id": "12",
                        "description": "something",
                        "device_type": "",
                        "health": "Unknown",
                        "state": "Running",
                        "submitter": "admin",
                    },
                ],
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0]
        == """Jobs (from 1 to 25):
* 16: Finished,Complete [lava] (hello) - bbb
* 12: Running,Unknown [admin] (something) - \n"""
    )


def test_jobs_list_since_verbose(setup, monkeypatch, capsys):
    version = "2019.1"
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "jobs", "list", "--verbose", "--since", "5"]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.jobs.list",
                "args": (None, None, 0, 25, 5, True),
                "ret": [
                    {
                        "id": "16",
                        "description": "hello",
                        "device_type": "bbb",
                        "health": "Complete",
                        "state": "Rinished",
                        "submitter": "lava",
                        "actual_device": "bbb-01",
                        "start_time": "12",
                        "end_time": "13",
                        "error_msg": None,
                        "error_type": None,
                    },
                    {
                        "id": "12",
                        "description": "something",
                        "device_type": "docker",
                        "health": "Unknown",
                        "state": "Running",
                        "submitter": "admin",
                        "actual_device": "docker-01",
                        "start_time": "45",
                        "end_time": "46",
                        "error_msg": "job error",
                        "error_type": "something is wrong",
                    },
                ],
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0]
        == """Jobs (from 1 to 25):
* 16: Rinished,Complete [lava] (hello) - bbb bbb-01 <12> <13>
* 12: Running,Unknown [admin] (something) - docker docker-01 <45> <46> something is wrong: job error\n"""
    )


def test_jobs_list_json(setup, monkeypatch, capsys):
    version = "2019.1"
    monkeypatch.setattr(sys, "argv", ["lavacli", "jobs", "list", "--json"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.jobs.list",
                "args": (None, None, 0, 25, 0, False),
                "ret": [
                    {
                        "id": "16",
                        "description": "hello",
                        "device_type": "bbb",
                        "health": "Complete",
                        "state": "Rinished",
                        "submitter": "lava",
                    },
                    {
                        "id": "15",
                        "description": "world",
                        "device_type": "qemu",
                        "health": "Incomplete",
                        "state": "Finished",
                        "submitter": "lab",
                    },
                    {
                        "id": "14",
                        "description": "health",
                        "device_type": "docker",
                        "health": "Canceled",
                        "state": "Finished",
                        "submitter": "lava-health",
                    },
                    {
                        "id": "12",
                        "description": "something",
                        "device_type": "",
                        "health": "Unknown",
                        "state": "Running",
                        "submitter": "admin",
                    },
                ],
            },
        ],
    )
    assert main() == 0  # nosec
    assert json.loads(capsys.readouterr()[0]) == [  # nosec
        {
            "id": "16",
            "description": "hello",
            "device_type": "bbb",
            "health": "Complete",
            "state": "Rinished",
            "submitter": "lava",
        },
        {
            "id": "15",
            "description": "world",
            "device_type": "qemu",
            "health": "Incomplete",
            "state": "Finished",
            "submitter": "lab",
        },
        {
            "id": "14",
            "description": "health",
            "device_type": "docker",
            "health": "Canceled",
            "state": "Finished",
            "submitter": "lava-health",
        },
        {
            "id": "12",
            "description": "something",
            "device_type": "",
            "health": "Unknown",
            "state": "Running",
            "submitter": "admin",
        },
    ]


def test_jobs_list_yaml(setup, monkeypatch, capsys):
    version = "2019.1"
    monkeypatch.setattr(sys, "argv", ["lavacli", "jobs", "list", "--yaml"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.jobs.list",
                "args": (None, None, 0, 25, 0, False),
                "ret": [
                    {
                        "id": "16",
                        "description": "hello",
                        "device_type": "bbb",
                        "health": "Complete",
                        "state": "Rinished",
                        "submitter": "lava",
                    },
                    {
                        "id": "15",
                        "description": "world",
                        "device_type": "qemu",
                        "health": "Incomplete",
                        "state": "Finished",
                        "submitter": "lab",
                    },
                    {
                        "id": "14",
                        "description": "health",
                        "device_type": "docker",
                        "health": "Canceled",
                        "state": "Finished",
                        "submitter": "lava-health",
                    },
                    {
                        "id": "12",
                        "description": "something",
                        "device_type": "",
                        "health": "Unknown",
                        "state": "Running",
                        "submitter": "admin",
                    },
                ],
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0]
        == """- {description: hello, device_type: bbb, health: Complete, id: '16', state: Rinished,
  submitter: lava}
- {description: world, device_type: qemu, health: Incomplete, id: '15', state: Finished,
  submitter: lab}
- {description: health, device_type: docker, health: Canceled, id: '14', state: Finished,
  submitter: lava-health}
- {description: something, device_type: '', health: Unknown, id: '12', state: Running,
  submitter: admin}
"""
    )


def test_jobs_list_filtering(setup, monkeypatch, capsys):
    version = "2019.1"
    monkeypatch.setattr(sys, "argv", ["lavacli", "jobs", "list", "--state", "RUNNING"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.jobs.list",
                "args": ("RUNNING", None, 0, 25, 0, False),
                "ret": [],
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "Jobs (from 1 to 25):\n"  # nosec


def test_jobs_list_filtering2(setup, monkeypatch, capsys):
    version = "2019.1"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "lavacli",
            "jobs",
            "list",
            "--health",
            "CANCELED",
            "--start",
            "45",
            "--limit",
            "56",
        ],
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.jobs.list",
                "args": (None, "CANCELED", 45, 56, 0, False),
                "ret": [],
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "Jobs (from 46 to 101):\n"  # nosec


# TODO: test with 2018.6 and also --start/--end
def test_jobs_logs(setup, monkeypatch, capsys):
    version = "2019.1"
    now = xmlrpc.client.DateTime("20180128T01:01:01")

    def sleep(duration):
        assert duration == 5  # nosec

    monkeypatch.setattr(time, "sleep", sleep)
    monkeypatch.setattr(sys, "argv", ["lavacli", "jobs", "logs", "1234"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.jobs.logs",
                "args": ("1234", 0, None),
                "ret": (
                    False,
                    '- {"dt": "2018-04-23T12:07:02.569264", "lvl": "info", "msg": "lava-dispatcher, installed at version: 2019.1-1"}',
                ),
            },
            {
                "request": "scheduler.jobs.logs",
                "args": ("1234", 1, None),
                "ret": (
                    True,
                    """- {"dt": "2018-04-23T12:07:02.572789", "lvl": "results", "msg": {"case": "validate", "definition": "lava", "result": "pass"}}
- {"dt": "2018-04-23T12:07:02.573414", "lvl": "debug", "msg": "start: 1.1 download-retry (timeout 00:02:00) [common]"}""",
                ),
            },
            {
                "request": "scheduler.jobs.show",
                "args": ("1234",),
                "ret": {
                    "id": "1234",
                    "description": "desc",
                    "device": "qemu01",
                    "device_type": "qemu",
                    "health_check": False,
                    "pipeline": True,
                    "health": "Complete",
                    "state": "Finished",
                    "submitter": "lava-admin",
                    "submit_time": now,
                    "start_time": now,
                    "end_time": now,
                    "tags": [],
                    "visibility": "Publicly visible",
                    "failure_comment": None,
                },
            },
        ],
    )
    assert main() == 0  # nosec
    lines = capsys.readouterr()[0].split("\n")
    assert (  # nosec
        lines[0]
        == "2018-04-23T12:07:02 lava-dispatcher, installed at version: 2019.1-1"
    )
    assert lines[1][:20] == "2018-04-23T12:07:02 "  # nosec
    assert safe_yaml.load(lines[1][20:]) == {  # nosec
        "case": "validate",
        "definition": "lava",
        "result": "pass",
    }
    assert (  # nosec
        lines[2]
        == "2018-04-23T12:07:02 start: 1.1 download-retry (timeout 00:02:00) [common]"
    )


def test_jobs_logs_failure_comment_and_polling(setup, monkeypatch, capsys):
    version = "2019.1"
    now = xmlrpc.client.DateTime("20180128T01:01:01")

    def sleep(duration):
        assert duration == 10  # nosec

    monkeypatch.setattr(time, "sleep", sleep)
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "jobs", "logs", "--polling", "10", "1234"]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.jobs.logs",
                "args": ("1234", 0, None),
                "ret": (
                    False,
                    '- {"dt": "2018-04-23T12:07:02.569264", "lvl": "info", "msg": "lava-dispatcher, installed at version: 2019.1-1"}',
                ),
            },
            {
                "request": "scheduler.jobs.logs",
                "args": ("1234", 1, None),
                "ret": (
                    True,
                    """- {"dt": "2018-04-23T12:07:02.572789", "lvl": "results", "msg": {"case": "validate", "definition": "lava", "result": "pass"}}
- {"dt": "2018-04-23T12:07:02.573414", "lvl": "debug", "msg": "start: 1.1 download-retry (timeout 00:02:00) [common]"}""",
                ),
            },
            {
                "request": "scheduler.jobs.show",
                "args": ("1234",),
                "ret": {
                    "id": "1234",
                    "description": "desc",
                    "device": "qemu01",
                    "device_type": "qemu",
                    "health_check": False,
                    "pipeline": True,
                    "health": "Incomplete",
                    "state": "Finished",
                    "submitter": "lava-admin",
                    "submit_time": now,
                    "start_time": now,
                    "end_time": now,
                    "tags": [],
                    "visibility": "Publicly visible",
                    "failure_comment": "A small issue was found",
                },
            },
        ],
    )
    assert main() == 0  # nosec
    lines = capsys.readouterr()[0].split("\n")
    assert (  # nosec
        lines[0]
        == "2018-04-23T12:07:02 lava-dispatcher, installed at version: 2019.1-1"
    )
    assert lines[1][:20] == "2018-04-23T12:07:02 "  # nosec
    assert safe_yaml.load(lines[1][20:]) == {  # nosec
        "case": "validate",
        "definition": "lava",
        "result": "pass",
    }
    assert (  # nosec
        lines[2]
        == "2018-04-23T12:07:02 start: 1.1 download-retry (timeout 00:02:00) [common]"
    )
    assert lines[3].endswith(  # nosec
        "lavacli] Failure comment: A small issue was found"
    )


def test_jobs_logs_filtering(setup, monkeypatch, capsys):
    version = "2019.1"
    now = xmlrpc.client.DateTime("20180128T01:01:01")

    def sleep(duration):
        assert duration == 5  # nosec

    monkeypatch.setattr(time, "sleep", sleep)
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "jobs", "logs", "1234", "--filters", "info,debug"]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.jobs.logs",
                "args": ("1234", 0, None),
                "ret": (
                    False,
                    '- {"dt": "2018-04-23T12:07:02.569264", "lvl": "info", "msg": "lava-dispatcher, installed at version: 2019.1-1"}',
                ),
            },
            {
                "request": "scheduler.jobs.logs",
                "args": ("1234", 1, None),
                "ret": (
                    True,
                    """- {"dt": "2018-04-23T12:07:02.572789", "lvl": "results", "msg": {"case": "validate", "definition": "lava", "result": "pass"}}
- {"dt": "2018-04-23T12:07:02.573414", "lvl": "debug", "msg": "start: 1.1 download-retry (timeout 00:02:00) [common]"}""",
                ),
            },
            {
                "request": "scheduler.jobs.show",
                "args": ("1234",),
                "ret": {
                    "id": "1234",
                    "description": "desc",
                    "device": "qemu01",
                    "device_type": "qemu",
                    "health_check": False,
                    "pipeline": True,
                    "health": "Complete",
                    "state": "Finished",
                    "submitter": "lava-admin",
                    "submit_time": now,
                    "start_time": now,
                    "end_time": now,
                    "tags": [],
                    "visibility": "Publicly visible",
                    "failure_comment": None,
                },
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0]
        == """2018-04-23T12:07:02 lava-dispatcher, installed at version: 2019.1-1
2018-04-23T12:07:02 start: 1.1 download-retry (timeout 00:02:00) [common]
"""
    )


def test_jobs_logs_raw(setup, monkeypatch, capsys):
    version = "2019.1"
    now = xmlrpc.client.DateTime("20180128T01:01:01")

    def sleep(duration):
        assert duration == 5  # nosec

    monkeypatch.setattr(time, "sleep", sleep)
    monkeypatch.setattr(sys, "argv", ["lavacli", "jobs", "logs", "1234", "--raw"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.jobs.logs",
                "args": ("1234", 0, None),
                "ret": (
                    False,
                    '- {"dt": "2018-04-23T12:07:02.569264", "lvl": "info", "msg": "lava-dispatcher, installed at version: 2019.1-1"}',
                ),
            },
            {
                "request": "scheduler.jobs.logs",
                "args": ("1234", 1, None),
                "ret": (
                    True,
                    """- {"dt": "2018-04-23T12:07:02.572789", "lvl": "results", "msg": {"case": "validate", "definition": "lava", "result": "pass"}}
- {"dt": "2018-04-23T12:07:02.573414", "lvl": "debug", "msg": "start: 1.1 download-retry (timeout 00:02:00) [common]"}""",
                ),
            },
            {
                "request": "scheduler.jobs.show",
                "args": ("1234",),
                "ret": {
                    "id": "1234",
                    "description": "desc",
                    "device": "qemu01",
                    "device_type": "qemu",
                    "health_check": False,
                    "pipeline": True,
                    "health": "Complete",
                    "state": "Finished",
                    "submitter": "lava-admin",
                    "submit_time": now,
                    "start_time": now,
                    "end_time": now,
                    "tags": [],
                    "visibility": "Publicly visible",
                    "failure_comment": None,
                },
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0]
        == """- {"dt": "2018-04-23T12:07:02.569264", "lvl": "info", "msg": "lava-dispatcher, installed at version: 2019.1-1"}
- {"dt": "2018-04-23T12:07:02.572789", "lvl": "results", "msg": {"case": "validate", "definition": "lava", "result": "pass"}}
- {"dt": "2018-04-23T12:07:02.573414", "lvl": "debug", "msg": "start: 1.1 download-retry (timeout 00:02:00) [common]"}
"""
    )


def test_jobs_logs_raw_filter(setup, monkeypatch, capsys):
    version = "2019.1"
    now = xmlrpc.client.DateTime("20180128T01:01:01")

    def sleep(duration):
        assert duration == 5  # nosec

    monkeypatch.setattr(time, "sleep", sleep)
    monkeypatch.setattr(
        sys,
        "argv",
        ["lavacli", "jobs", "logs", "1234", "--raw", "--filters", "debug,results"],
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.jobs.logs",
                "args": ("1234", 0, None),
                "ret": (
                    False,
                    '- {"dt": "2018-04-23T12:07:02.569264", "lvl": "info", "msg": "lava-dispatcher, installed at version: 2019.1-1"}',
                ),
            },
            {
                "request": "scheduler.jobs.logs",
                "args": ("1234", 1, None),
                "ret": (
                    True,
                    """- {"dt": "2018-04-23T12:07:02.572789", "lvl": "results", "msg": {"case": "validate", "definition": "lava", "result": "pass"}}
- {"dt": "2018-04-23T12:07:02.573414", "lvl": "debug", "msg": "start: 1.1 download-retry (timeout 00:02:00) [common]"}""",
                ),
            },
            {
                "request": "scheduler.jobs.show",
                "args": ("1234",),
                "ret": {
                    "id": "1234",
                    "description": "desc",
                    "device": "qemu01",
                    "device_type": "qemu",
                    "health_check": False,
                    "pipeline": True,
                    "health": "Complete",
                    "state": "Finished",
                    "submitter": "lava-admin",
                    "submit_time": now,
                    "start_time": now,
                    "end_time": now,
                    "tags": [],
                    "visibility": "Publicly visible",
                    "failure_comment": None,
                },
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0]
        == """- {"dt": "2018-04-23T12:07:02.572789", "lvl": "results", "msg": {"case": "validate", "definition": "lava", "result": "pass"}}
- {"dt": "2018-04-23T12:07:02.573414", "lvl": "debug", "msg": "start: 1.1 download-retry (timeout 00:02:00) [common]"}
"""
    )


def test_jobs_queue(setup, monkeypatch, capsys):
    version = "2019.01"
    monkeypatch.setattr(sys, "argv", ["lavacli", "jobs", "queue"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.jobs.queue",
                "args": (None, 0, 25),
                "ret": [
                    {
                        "id": 12,
                        "description": None,
                        "requested_device_type": "qemu",
                        "submitter": "lava-health",
                    },
                    {
                        "id": 14,
                        "description": "qemu health",
                        "requested_device_type": "qemu",
                        "submitter": "lava-health",
                    },
                ],
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0]
        == """Jobs (from 1 to 25):
* 12: lava-health () - qemu
* 14: lava-health (qemu health) - qemu
"""
    )


def test_jobs_queue_json(setup, monkeypatch, capsys):
    version = "2019.01"
    monkeypatch.setattr(sys, "argv", ["lavacli", "jobs", "queue", "--json"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.jobs.queue",
                "args": (None, 0, 25),
                "ret": [
                    {
                        "id": 12,
                        "description": None,
                        "requested_device_type": "qemu",
                        "submitter": "lava-health",
                    },
                    {
                        "id": 14,
                        "description": "qemu health",
                        "requested_device_type": "qemu",
                        "submitter": "lava-health",
                    },
                ],
            },
        ],
    )
    assert main() == 0  # nosec
    assert json.loads(capsys.readouterr()[0]) == [  # nosec
        {
            "id": 12,
            "description": None,
            "requested_device_type": "qemu",
            "submitter": "lava-health",
        },
        {
            "id": 14,
            "description": "qemu health",
            "requested_device_type": "qemu",
            "submitter": "lava-health",
        },
    ]


def test_jobs_queue_yaml(setup, monkeypatch, capsys):
    version = "2019.01"
    monkeypatch.setattr(sys, "argv", ["lavacli", "jobs", "queue", "--yaml"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.jobs.queue",
                "args": (None, 0, 25),
                "ret": [
                    {
                        "id": 12,
                        "description": None,
                        "requested_device_type": "qemu",
                        "submitter": "lava-health",
                    },
                    {
                        "id": 14,
                        "description": "qemu health",
                        "requested_device_type": "qemu",
                        "submitter": "lava-health",
                    },
                ],
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0]
        == """- {description: null, id: 12, requested_device_type: qemu, submitter: lava-health}
- {description: qemu health, id: 14, requested_device_type: qemu, submitter: lava-health}
"""
    )


def test_jobs_queue_filtering(setup, monkeypatch, capsys):
    version = "2019.01"
    monkeypatch.setattr(sys, "argv", ["lavacli", "jobs", "queue", "qemu"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {"request": "scheduler.jobs.queue", "args": (["qemu"], 0, 25), "ret": []},
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "Jobs (from 1 to 25):\n"  # nosec

    monkeypatch.setattr(sys, "argv", ["lavacli", "jobs", "queue", "qemu", "panda"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.jobs.queue",
                "args": (["qemu", "panda"], 0, 25),
                "ret": [],
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "Jobs (from 1 to 25):\n"  # nosec

    version = "2019.01"
    monkeypatch.setattr(
        sys,
        "argv",
        ["lavacli", "jobs", "queue", "--start", "1", "--limit", "3", "qemu"],
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {"request": "scheduler.jobs.queue", "args": (["qemu"], 1, 3), "ret": []},
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "Jobs (from 2 to 4):\n"  # nosec


def test_jobs_resubmit(setup, monkeypatch, capsys):
    version = "2019.1"
    monkeypatch.setattr(sys, "argv", ["lavacli", "jobs", "resubmit", "1234"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {"request": "scheduler.jobs.resubmit", "args": ("1234",), "ret": 1234},
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "1234\n"  # nosec


def test_jobs_resubmit_url(setup, monkeypatch, capsys):
    version = "2019.1"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "lavacli",
            "--uri",
            "https://localhost:8000/RPC2",
            "jobs",
            "resubmit",
            "1234",
            "--url",
        ],
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {"request": "scheduler.jobs.resubmit", "args": ("1234",), "ret": 1234},
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0] == "https://localhost:8000/scheduler/job/1234\n"
    )


def test_jobs_resubmit_mutlinode(setup, monkeypatch, capsys):
    version = "2019.1"
    monkeypatch.setattr(sys, "argv", ["lavacli", "jobs", "resubmit", "1234"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.jobs.resubmit",
                "args": ("1234",),
                "ret": [1234, 1235],
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "1234\n1235\n"  # nosec


def test_jobs_resubmit_mutlinode_url(setup, monkeypatch, capsys):
    version = "2019.1"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "lavacli",
            "--uri",
            "https://example.com/RPC2",
            "jobs",
            "resubmit",
            "1234",
            "--url",
        ],
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.jobs.resubmit",
                "args": ("1234",),
                "ret": [1234, 1345],
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0]
        == "https://example.com/scheduler/job/1234\nhttps://example.com/scheduler/job/1345\n"
    )


def test_jobs_resubmit_follow(setup, monkeypatch, capsys):
    version = "2019.1"
    now = xmlrpc.client.DateTime("20180128T01:01:01")

    def sleep(duration):
        assert duration == 5  # nosec

    monkeypatch.setattr(time, "sleep", sleep)
    monkeypatch.setattr(
        sys,
        "argv",
        ["lavacli", "jobs", "resubmit", "1234", "--follow", "--filters", "info,debug"],
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {"request": "scheduler.jobs.resubmit", "args": ("1234",), "ret": 1234},
            {
                "request": "scheduler.jobs.logs",
                "args": ("1234", 0, None),
                "ret": (
                    False,
                    '- {"dt": "2018-04-23T12:07:02.569264", "lvl": "info", "msg": "lava-dispatcher, installed at version: 2019.1-1"}',
                ),
            },
            {
                "request": "scheduler.jobs.logs",
                "args": ("1234", 1, None),
                "ret": (
                    True,
                    """- {"dt": "2018-04-23T12:07:02.572789", "lvl": "results", "msg": {"case": "validate", "definition": "lava", "result": "pass"}}
- {"dt": "2018-04-23T12:07:02.573414", "lvl": "debug", "msg": "start: 1.1 download-retry (timeout 00:02:00) [common]"}""",
                ),
            },
            {
                "request": "scheduler.jobs.show",
                "args": ("1234",),
                "ret": {
                    "id": "1234",
                    "description": "desc",
                    "device": "qemu01",
                    "device_type": "qemu",
                    "health_check": False,
                    "pipeline": True,
                    "health": "Complete",
                    "state": "Finished",
                    "submitter": "lava-admin",
                    "submit_time": now,
                    "start_time": now,
                    "end_time": now,
                    "tags": [],
                    "visibility": "Publicly visible",
                    "failure_comment": None,
                },
            },
        ],
    )
    assert main() == 0  # nosec
    lines = capsys.readouterr()[0].split("\n")
    assert lines[0].endswith("[lavacli] Job 1234 submitted")  # nosec
    assert (  # nosec
        lines[1]
        == "2018-04-23T12:07:02 lava-dispatcher, installed at version: 2019.1-1"
    )
    assert (  # nosec
        lines[2]
        == "2018-04-23T12:07:02 start: 1.1 download-retry (timeout 00:02:00) [common]"
    )


def test_jobs_run(setup, monkeypatch, capsys, tmp_path):
    version = "2019.1"
    now = xmlrpc.client.DateTime("20180128T01:01:01")

    def sleep(duration):
        assert duration == 5  # nosec

    with (tmp_path / "job.yaml").open("w") as f_out:
        f_out.write("job definition")
    monkeypatch.setattr(time, "sleep", sleep)
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "jobs", "run", str(tmp_path / "job.yaml")]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.jobs.submit",
                "args": ("job definition",),
                "ret": "4567",
            },
            {
                "request": "scheduler.jobs.logs",
                "args": ("4567", 0, None),
                "ret": (
                    False,
                    '- {"dt": "2018-04-23T12:07:02.569264", "lvl": "info", "msg": "lava-dispatcher, installed at version: 2019.1-1"}',
                ),
            },
            {
                "request": "scheduler.jobs.logs",
                "args": ("4567", 1, None),
                "ret": (
                    True,
                    """- {"dt": "2018-04-23T12:07:02.572789", "lvl": "results", "msg": {"case": "validate", "definition": "lava", "result": "pass"}}
- {"dt": "2018-04-23T12:07:02.573414", "lvl": "debug", "msg": "start: 1.1 download-retry (timeout 00:02:00) [common]"}""",
                ),
            },
            {
                "request": "scheduler.jobs.show",
                "args": ("4567",),
                "ret": {
                    "id": "4567",
                    "description": "desc",
                    "device": "qemu01",
                    "device_type": "qemu",
                    "health_check": False,
                    "pipeline": True,
                    "health": "Complete",
                    "state": "Finished",
                    "submitter": "lava-admin",
                    "submit_time": now,
                    "start_time": now,
                    "end_time": now,
                    "tags": [],
                    "visibility": "Publicly visible",
                    "failure_comment": None,
                },
            },
        ],
    )
    assert main() == 0  # nosec
    lines = capsys.readouterr()[0].split("\n")
    assert lines[0].endswith("[lavacli] Job 4567 submitted")  # nosec
    assert (  # nosec
        lines[1]
        == "2018-04-23T12:07:02 lava-dispatcher, installed at version: 2019.1-1"
    )
    assert lines[2][:20] == "2018-04-23T12:07:02 "  # nosec
    assert safe_yaml.load(lines[2][20:]) == {  # nosec
        "case": "validate",
        "definition": "lava",
        "result": "pass",
    }
    assert (  # nosec
        lines[3]
        == "2018-04-23T12:07:02 start: 1.1 download-retry (timeout 00:02:00) [common]"
    )


def test_jobs_show(setup, monkeypatch, capsys):
    version = "2019.1"
    now = xmlrpc.client.DateTime("20180128T01:01:01")
    monkeypatch.setattr(sys, "argv", ["lavacli", "jobs", "show", "789"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.jobs.show",
                "args": ("789",),
                "ret": {
                    "id": "789",
                    "description": "desc",
                    "device": "qemu01",
                    "device_type": "qemu",
                    "health_check": False,
                    "pipeline": True,
                    "health": "Complete",
                    "state": "Finished",
                    "submitter": "lava-admin",
                    "submit_time": now,
                    "start_time": now,
                    "end_time": now,
                    "tags": [],
                    "visibility": "Publicly visible",
                    "failure_comment": None,
                },
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0]
        == """id          : 789
description : desc
submitter   : lava-admin
device-type : qemu
device      : qemu01
health-check: False
state       : Finished
Health      : Complete
pipeline    : True
tags        : []
visibility  : Publicly visible
submit time : 20180128T01:01:01
start time  : 20180128T01:01:01
end time    : 20180128T01:01:01
"""
    )


def test_jobs_show_failure_comment(setup, monkeypatch, capsys):
    version = "2019.1"
    now = xmlrpc.client.DateTime("20180128T01:01:01")
    monkeypatch.setattr(sys, "argv", ["lavacli", "jobs", "show", "789"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.jobs.show",
                "args": ("789",),
                "ret": {
                    "id": "789",
                    "description": "desc",
                    "device": "qemu01",
                    "device_type": "qemu",
                    "health_check": False,
                    "pipeline": True,
                    "health": "Incomplete",
                    "state": "Finished",
                    "submitter": "lava-admin",
                    "submit_time": now,
                    "start_time": now,
                    "end_time": now,
                    "tags": [],
                    "visibility": "Publicly visible",
                    "failure_comment": "Something went wrong",
                },
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0]
        == """id          : 789
description : desc
submitter   : lava-admin
device-type : qemu
device      : qemu01
health-check: False
state       : Finished
Health      : Incomplete
failure     : Something went wrong
pipeline    : True
tags        : []
visibility  : Publicly visible
submit time : 20180128T01:01:01
start time  : 20180128T01:01:01
end time    : 20180128T01:01:01
"""
    )


def test_jobs_show_json(setup, monkeypatch, capsys):
    version = "2019.1"
    now = xmlrpc.client.DateTime("20180128T01:01:01")
    monkeypatch.setattr(sys, "argv", ["lavacli", "jobs", "show", "789", "--json"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.jobs.show",
                "args": ("789",),
                "ret": {
                    "id": "789",
                    "description": "desc",
                    "device": "qemu01",
                    "device_type": "qemu",
                    "health_check": False,
                    "pipeline": True,
                    "health": "Complete",
                    "state": "Finished",
                    "submitter": "lava-admin",
                    "submit_time": now,
                    "start_time": now,
                    "end_time": now,
                    "tags": [],
                    "visibility": "Publicly visible",
                    "failure_comment": None,
                },
            },
        ],
    )
    assert main() == 0  # nosec
    assert json.loads(capsys.readouterr()[0]) == {  # nosec
        "id": "789",
        "description": "desc",
        "device": "qemu01",
        "device_type": "qemu",
        "health_check": False,
        "pipeline": True,
        "health": "Complete",
        "state": "Finished",
        "submitter": "lava-admin",
        "submit_time": "20180128T01:01:01",
        "start_time": "20180128T01:01:01",
        "end_time": "20180128T01:01:01",
        "tags": [],
        "visibility": "Publicly visible",
        "failure_comment": None,
    }


def test_jobs_show_yaml(setup, monkeypatch, capsys):
    version = "2019.1"
    now = xmlrpc.client.DateTime("20180128T01:01:01")
    monkeypatch.setattr(sys, "argv", ["lavacli", "jobs", "show", "789", "--yaml"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.jobs.show",
                "args": ("789",),
                "ret": {
                    "id": "789",
                    "description": "desc",
                    "device": "qemu01",
                    "device_type": "qemu",
                    "health_check": False,
                    "pipeline": True,
                    "health": "Complete",
                    "state": "Finished",
                    "submitter": "lava-admin",
                    "submit_time": now,
                    "start_time": now,
                    "end_time": now,
                    "tags": [],
                    "visibility": "Publicly visible",
                    "failure_comment": None,
                },
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0]
        == """description: desc
device: qemu01
device_type: qemu
end_time: 20180128T01:01:01
failure_comment: null
health: Complete
health_check: false
id: '789'
pipeline: true
start_time: 20180128T01:01:01
state: Finished
submit_time: 20180128T01:01:01
submitter: lava-admin
tags: []
visibility: Publicly visible
"""
    )


def test_jobs_submit(setup, monkeypatch, capsys, tmp_path):
    version = "2019.1"
    with (tmp_path / "job.yaml").open("w") as f_out:
        f_out.write("job definition as yaml")
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "jobs", "submit", str(tmp_path / "job.yaml")]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.jobs.submit",
                "args": ("job definition as yaml",),
                "ret": 5689,
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "5689\n"  # nosec


def test_jobs_submit_url(setup, monkeypatch, capsys, tmp_path):
    version = "2019.1"
    with (tmp_path / "job.yaml").open("w") as f_out:
        f_out.write("job definition as yaml")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "lavacli",
            "--uri",
            "https://localhost:8000/RPC2",
            "jobs",
            "submit",
            str(tmp_path / "job.yaml"),
            "--url",
        ],
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.jobs.submit",
                "args": ("job definition as yaml",),
                "ret": 5689,
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0] == "https://localhost:8000/scheduler/job/5689\n"
    )


def test_jobs_submit_url_identity_default(setup, monkeypatch, capsys, tmp_path):
    version = "2019.1"
    with (tmp_path / "job.yaml").open("w") as f_out:
        f_out.write("job definition as yaml")
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "jobs", "submit", str(tmp_path / "job.yaml"), "--url"]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.jobs.submit",
                "args": ("job definition as yaml",),
                "ret": 5689,
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0] == "https://lava.example.com/scheduler/job/5689\n"
    )


def test_jobs_submit_url_identity_admin(setup, monkeypatch, capsys, tmp_path):
    version = "2019.1"
    with (tmp_path / "job.yaml").open("w") as f_out:
        f_out.write("job definition as yaml")
    with (tmp_path / "lavacli.yaml").open("w") as f_conf:
        safe_yaml.dump(
            {
                "default": {"uri": "https://lava.example.com/RPC2"},
                "admin": {"uri": "https://localhost:8001/RPC2"},
            },
            f_conf,
        )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "lavacli",
            "-i",
            "admin",
            "jobs",
            "submit",
            str(tmp_path / "job.yaml"),
            "--url",
        ],
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.jobs.submit",
                "args": ("job definition as yaml",),
                "ret": 5689,
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0] == "https://localhost:8001/scheduler/job/5689\n"
    )


def test_jobs_submit_multiple(setup, monkeypatch, capsys, tmp_path):
    version = "2019.1"
    with (tmp_path / "job1.yaml").open("w") as f_out:
        f_out.write("first job definition as yaml")
    with (tmp_path / "job2.yaml").open("w") as f_out:
        f_out.write("second job definition as yaml")
    with (tmp_path / "job3.yaml").open("w") as f_out:
        f_out.write("third job definition as yaml")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "lavacli",
            "jobs",
            "submit",
            str(tmp_path / "job1.yaml"),
            str(tmp_path / "job2.yaml"),
            str(tmp_path / "job3.yaml"),
        ],
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.jobs.submit",
                "args": ("first job definition as yaml",),
                "ret": 5689,
            },
            {
                "request": "scheduler.jobs.submit",
                "args": ("second job definition as yaml",),
                "ret": 5690,
            },
            {
                "request": "scheduler.jobs.submit",
                "args": ("third job definition as yaml",),
                "ret": [5691, 5692],
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "5689\n5690\n5691\n5692\n"  # nosec


def test_jobs_submit_multinode(setup, monkeypatch, capsys, tmp_path):
    version = "2019.1"
    with (tmp_path / "job.yaml").open("w") as f_out:
        f_out.write("job definition as yaml")
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "jobs", "submit", str(tmp_path / "job.yaml")]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.jobs.submit",
                "args": ("job definition as yaml",),
                "ret": [5689, 5698],
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "5689\n5698\n"  # nosec


def test_jobs_submit_multinode_url(setup, monkeypatch, capsys, tmp_path):
    version = "2019.1"
    with (tmp_path / "job.yaml").open("w") as f_out:
        f_out.write("job definition as yaml")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "lavacli",
            "--uri",
            "https://localhost:8000/RPC2",
            "jobs",
            "submit",
            str(tmp_path / "job.yaml"),
            "--url",
        ],
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.jobs.submit",
                "args": ("job definition as yaml",),
                "ret": [5689, 5698],
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0]
        == "https://localhost:8000/scheduler/job/5689\nhttps://localhost:8000/scheduler/job/5698\n"
    )


def test_jobs_wait(setup, monkeypatch, capsys):
    version = "2019.1"
    now = xmlrpc.client.DateTime("20180128T01:01:01")

    def sleep(duration):
        assert duration == 5  # nosec

    monkeypatch.setattr(time, "sleep", sleep)
    monkeypatch.setattr(sys, "argv", ["lavacli", "jobs", "wait", "1234"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.jobs.show",
                "args": ("1234",),
                "ret": {
                    "id": "1234",
                    "description": "desc",
                    "device": "qemu01",
                    "device_type": "qemu",
                    "health_check": False,
                    "pipeline": True,
                    "health": "Unknown",
                    "state": "Submitted",
                    "submitter": "lava-admin",
                    "submit_time": now,
                    "start_time": None,
                    "end_time": None,
                    "tags": [],
                    "visibility": "Publicly visible",
                    "failure_comment": None,
                },
            },
            {
                "request": "scheduler.jobs.show",
                "args": ("1234",),
                "ret": {
                    "id": "1234",
                    "description": "desc",
                    "device": "qemu01",
                    "device_type": "qemu",
                    "health_check": False,
                    "pipeline": True,
                    "health": "Unknown",
                    "state": "Running",
                    "submitter": "lava-admin",
                    "submit_time": now,
                    "start_time": now,
                    "end_time": None,
                    "tags": [],
                    "visibility": "Publicly visible",
                    "failure_comment": None,
                },
            },
            {
                "request": "scheduler.jobs.show",
                "args": ("1234",),
                "ret": {
                    "id": "1234",
                    "description": "desc",
                    "device": "qemu01",
                    "device_type": "qemu",
                    "health_check": False,
                    "pipeline": True,
                    "health": "Unknown",
                    "state": "Running",
                    "submitter": "lava-admin",
                    "submit_time": now,
                    "start_time": now,
                    "end_time": None,
                    "tags": [],
                    "visibility": "Publicly visible",
                    "failure_comment": None,
                },
            },
            {
                "request": "scheduler.jobs.show",
                "args": ("1234",),
                "ret": {
                    "id": "1234",
                    "description": "desc",
                    "device": "qemu01",
                    "device_type": "qemu",
                    "health_check": False,
                    "pipeline": True,
                    "health": "Complete",
                    "state": "Finished",
                    "submitter": "lava-admin",
                    "submit_time": now,
                    "start_time": now,
                    "end_time": now,
                    "tags": [],
                    "visibility": "Publicly visible",
                    "failure_comment": None,
                },
            },
        ],
    )

    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "Submitted\nRunning.\n"  # nosec


def test_jobs_submit_follow(setup, monkeypatch, capsys, tmp_path):
    version = "2019.1"
    with (tmp_path / "job.yaml").open("w") as f_out:
        f_out.write("job definition as yaml")
    monkeypatch.setattr(
        sys,
        "argv",
        ["lavacli", "jobs", "submit", "--follow", str(tmp_path / "job.yaml")],
    )
    now = xmlrpc.client.DateTime("20180128T01:01:01")
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.jobs.submit",
                "args": ("job definition as yaml",),
                "ret": 5689,
            },
            {
                "request": "scheduler.jobs.logs",
                "args": ("5689", 0, None),
                "ret": (
                    True,
                    '- {"dt": "2018-04-23T12:07:02.569264", "lvl": "info", "msg": "lava-dispatcher, installed at version: 2019.1-1"}',
                ),
            },
            {
                "request": "scheduler.jobs.show",
                "args": ("5689",),
                "ret": {
                    "id": "5689",
                    "description": "desc",
                    "device": "qemu01",
                    "device_type": "qemu",
                    "health_check": False,
                    "pipeline": True,
                    "health": "Complete",
                    "state": "Finished",
                    "submitter": "lava-admin",
                    "submit_time": now,
                    "start_time": now,
                    "end_time": now,
                    "tags": [],
                    "visibility": "Publicly visible",
                    "failure_comment": None,
                },
            },
        ],
    )
    assert main() == 0  # nosec
    assert "lava-dispatcher, installed at version: 2019.1" in capsys.readouterr()[0]
