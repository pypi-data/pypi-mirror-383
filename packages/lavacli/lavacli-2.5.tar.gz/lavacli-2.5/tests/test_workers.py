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


def test_workers_add(setup, monkeypatch, capsys):
    version = "2019.1"
    monkeypatch.setattr(sys, "argv", ["lavacli", "workers", "add", "worker01"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.workers.add",
                "args": ("worker01", None, False),
                "ret": None,
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == ""  # nosec


def test_workers_add_1(setup, monkeypatch, capsys):
    version = "2019.1"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "lavacli",
            "workers",
            "add",
            "worker01",
            "--description",
            "my worker",
            "--disabled",
        ],
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.workers.add",
                "args": ("worker01", "my worker", True),
                "ret": None,
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == ""  # nosec


def test_workers_config_delete(setup, monkeypatch, capsys, tmp_path):
    version = "2022.4"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "lavacli",
            "workers",
            "config",
            "delete",
            "worker01",
        ],
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.workers.set_config",
                "args": ("worker01", ""),
                "ret": True,
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == ""  # nosec


def test_workers_config_get(setup, monkeypatch, capsys):
    version = "2019.1"
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "workers", "config", "get", "worker01"]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.workers.get_config",
                "args": ("worker01",),
                "ret": "config content",
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "config content\n"  # nosec


def test_workers_config_set(setup, monkeypatch, capsys, tmp_path):
    version = "2019.1"
    with (tmp_path / "config.yaml").open("w") as f_conf:
        f_conf.write("config content")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "lavacli",
            "workers",
            "config",
            "set",
            "worker01",
            str(tmp_path / "config.yaml"),
        ],
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.workers.set_config",
                "args": ("worker01", "config content"),
                "ret": True,
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == ""  # nosec


def test_workers_config_set_error(setup, monkeypatch, capsys, tmp_path):
    version = "2019.1"
    with (tmp_path / "config.yaml").open("w") as f_conf:
        f_conf.write("config content")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "lavacli",
            "workers",
            "config",
            "set",
            "worker01",
            str(tmp_path / "config.yaml"),
        ],
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.workers.set_config",
                "args": ("worker01", "config content"),
                "ret": False,
            },
        ],
    )
    assert main() == 1  # nosec
    assert capsys.readouterr()[1] == "Unable to store worker configuration\n"  # nosec


def test_workers_env_delete(setup, monkeypatch, capsys, tmp_path):
    version = "2022.4"
    monkeypatch.setattr(
        sys,
        "argv",
        ["lavacli", "workers", "env", "delete", "worker01"],
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.workers.set_env",
                "args": ("worker01", ""),
                "ret": True,
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == ""  # nosec


def test_workers_env_get(setup, monkeypatch, capsys):
    version = "2019.6"
    monkeypatch.setattr(sys, "argv", ["lavacli", "workers", "env", "get", "worker01"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.workers.get_env",
                "args": ("worker01",),
                "ret": "env content",
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "env content\n"  # nosec


def test_workers_env_set(setup, monkeypatch, capsys, tmp_path):
    version = "2019.6"
    with (tmp_path / "env.yaml").open("w") as f_conf:
        f_conf.write("env content")
    monkeypatch.setattr(
        sys,
        "argv",
        ["lavacli", "workers", "env", "set", "worker01", str(tmp_path / "env.yaml")],
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.workers.set_env",
                "args": ("worker01", "env content"),
                "ret": True,
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == ""  # nosec


def test_workers_env_set_error(setup, monkeypatch, capsys, tmp_path):
    version = "2019.6"
    with (tmp_path / "env.yaml").open("w") as f_conf:
        f_conf.write("env content")
    monkeypatch.setattr(
        sys,
        "argv",
        ["lavacli", "workers", "env", "set", "worker01", str(tmp_path / "env.yaml")],
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.workers.set_env",
                "args": ("worker01", "env content"),
                "ret": False,
            },
        ],
    )
    assert main() == 1  # nosec
    assert capsys.readouterr()[1] == "Unable to store worker environment\n"  # nosec


def test_workers_env_dut_delete(setup, monkeypatch, capsys, tmp_path):
    version = "2022.4"
    monkeypatch.setattr(
        sys,
        "argv",
        ["lavacli", "workers", "env-dut", "delete", "worker01"],
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.workers.set_env_dut",
                "args": ("worker01", ""),
                "ret": True,
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == ""  # nosec


def test_workers_env_dut_get(setup, monkeypatch, capsys):
    version = "2022.4"
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "workers", "env-dut", "get", "worker01"]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.workers.get_env_dut",
                "args": ("worker01",),
                "ret": "env-dut content",
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "env-dut content\n"  # nosec


def test_workers_env_dut_set(setup, monkeypatch, capsys, tmp_path):
    version = "2022.4"
    with (tmp_path / "env.yaml").open("w") as f_conf:
        f_conf.write("env-dut content")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "lavacli",
            "workers",
            "env-dut",
            "set",
            "worker01",
            str(tmp_path / "env.yaml"),
        ],
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.workers.set_env_dut",
                "args": ("worker01", "env-dut content"),
                "ret": True,
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == ""  # nosec


def test_workers_env_dut_set_error(setup, monkeypatch, capsys, tmp_path):
    version = "2022.4"
    with (tmp_path / "env.yaml").open("w") as f_conf:
        f_conf.write("env-dut content")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "lavacli",
            "workers",
            "env-dut",
            "set",
            "worker01",
            str(tmp_path / "env.yaml"),
        ],
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.workers.set_env_dut",
                "args": ("worker01", "env-dut content"),
                "ret": False,
            },
        ],
    )
    assert main() == 1  # nosec
    assert capsys.readouterr()[1] == "Unable to store worker dut environment\n"  # nosec


def test_workers_list_exclude_retired(setup, monkeypatch, capsys):
    version = "2023.3"
    monkeypatch.setattr(sys, "argv", ["lavacli", "workers", "list"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.workers.list",
                "args": (False,),
                "ret": ["worker01", "worker02"],
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0]
        == """Workers:
* worker01
* worker02
"""
    )


def test_workers_list(setup, monkeypatch, capsys):
    version = "2019.1"
    monkeypatch.setattr(sys, "argv", ["lavacli", "workers", "list"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.workers.list",
                "args": (),
                "ret": ["worker01", "worker02"],
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0]
        == """Workers:
* worker01
* worker02
"""
    )


def test_workers_list_json(setup, monkeypatch, capsys):
    version = "2019.1"
    monkeypatch.setattr(sys, "argv", ["lavacli", "workers", "list", "--json"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.workers.list",
                "args": (),
                "ret": ["worker01", "worker02"],
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == '["worker01", "worker02"]\n'  # nosec


def test_workers_list_yaml(setup, monkeypatch, capsys):
    version = "2019.1"
    monkeypatch.setattr(sys, "argv", ["lavacli", "workers", "list", "--yaml"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.workers.list",
                "args": (),
                "ret": ["worker01", "worker02"],
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "[worker01, worker02]\n"  # nosec


def test_workers_maintenance(setup, monkeypatch, capsys):
    version = "2019.1"
    last_ping = xmlrpc.client.DateTime("20180128T01:01:01")

    def sleep(duration):
        assert duration == 5  # nosec

    monkeypatch.setattr(time, "sleep", sleep)
    monkeypatch.setattr(sys, "argv", ["lavacli", "workers", "maintenance", "worker01"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.workers.update",
                "args": ("worker01", None, "MAINTENANCE"),
                "ret": None,
            },
            {
                "request": "scheduler.workers.show",
                "args": ("worker01",),
                "ret": {
                    "hostname": "worker01",
                    "description": None,
                    "state": "Idle",
                    "health": "Active",
                    "devices": ["qemu01", "bbb-01"],
                    "last_ping": last_ping,
                },
            },
            {
                "request": "scheduler.devices.list",
                "args": (),
                "ret": [
                    {
                        "hostname": "qemu01",
                        "type": "qemu",
                        "health": "Good",
                        "state": "Idle",
                        "current_job": None,
                        "pipeline": True,
                    },
                    {
                        "hostname": "bbb-01",
                        "type": "qemu",
                        "health": "Good",
                        "state": "Running",
                        "current_job": 1234,
                        "pipeline": True,
                    },
                    {
                        "hostname": "bbb-02",
                        "type": "qemu",
                        "health": "Good",
                        "state": "Running",
                        "current_job": 1235,
                        "pipeline": True,
                    },
                ],
            },
            {
                "request": "scheduler.jobs.show",
                "args": (1234,),
                "ret": {
                    "id": "1234",
                    "description": "basic testing",
                    "device": "bbb-01",
                    "device_type": "bbb",
                    "health_check": False,
                    "pipeline": True,
                    "health": "Unknown",
                    "state": "Running",
                    "submitter": "lava-bot",
                    "submit_time": last_ping,
                    "start_time": last_ping,
                    "end_time": None,
                    "tags": [],
                    "visibility": "Publicly visible",
                    "failure_comment": "",
                },
            },
            {
                "request": "scheduler.jobs.show",
                "args": (1234,),
                "ret": {
                    "id": "1234",
                    "description": "basic testing",
                    "device": "bbb-01",
                    "device_type": "bbb",
                    "health_check": False,
                    "pipeline": True,
                    "health": "Complete",
                    "state": "Finished",
                    "submitter": "lava-bot",
                    "submit_time": last_ping,
                    "start_time": last_ping,
                    "end_time": last_ping,
                    "tags": [],
                    "visibility": "Publicly visible",
                    "failure_comment": "",
                },
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "-> waiting for job 1234\n--> waiting\n"  # nosec


def test_workers_maintenance_nowait(setup, monkeypatch, capsys):
    version = "2019.1"

    def sleep(duration):
        assert duration == 5  # nosec

    monkeypatch.setattr(time, "sleep", sleep)
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "workers", "maintenance", "worker01", "--no-wait"]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.workers.update",
                "args": ("worker01", None, "MAINTENANCE"),
                "ret": None,
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == ""  # nosec


def test_workers_maintenance_force(setup, monkeypatch, capsys):
    version = "2019.1"
    last_ping = xmlrpc.client.DateTime("20180128T01:01:01")
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "workers", "maintenance", "worker01", "--force"]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.workers.update",
                "args": ("worker01", None, "MAINTENANCE"),
                "ret": None,
            },
            {
                "request": "scheduler.workers.show",
                "args": ("worker01",),
                "ret": {
                    "hostname": "worker01",
                    "description": None,
                    "state": "Idle",
                    "health": "Active",
                    "devices": ["qemu01", "bbb-01"],
                    "last_ping": last_ping,
                },
            },
            {
                "request": "scheduler.devices.list",
                "args": (),
                "ret": [
                    {
                        "hostname": "qemu01",
                        "type": "qemu",
                        "health": "Good",
                        "state": "Idle",
                        "current_job": None,
                        "pipeline": True,
                    },
                    {
                        "hostname": "bbb-01",
                        "type": "qemu",
                        "health": "Good",
                        "state": "Running",
                        "current_job": 1234,
                        "pipeline": True,
                    },
                ],
            },
            {"request": "scheduler.jobs.cancel", "args": (1234,), "ret": None},
            {
                "request": "scheduler.jobs.show",
                "args": (1234,),
                "ret": {
                    "id": "1234",
                    "description": "basic testing",
                    "device": "bbb-01",
                    "device_type": "bbb",
                    "health_check": False,
                    "pipeline": True,
                    "health": "Canceled",
                    "state": "Finished",
                    "submitter": "lava-bot",
                    "submit_time": last_ping,
                    "start_time": last_ping,
                    "end_time": last_ping,
                    "tags": [],
                    "visibility": "Publicly visible",
                    "failure_comment": "",
                },
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "-> waiting for job 1234\n--> canceling\n"  # nosec


def test_workers_show(setup, monkeypatch, capsys):
    version = "2019.1"
    last_ping = xmlrpc.client.DateTime("20180128T01:01:01")
    monkeypatch.setattr(sys, "argv", ["lavacli", "workers", "show", "worker01"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.workers.show",
                "args": ("worker01",),
                "ret": {
                    "hostname": "worker01",
                    "description": None,
                    "state": "Idle",
                    "health": "Active",
                    "devices": ["qemu01", "bbb-01"],
                    "last_ping": last_ping,
                },
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0]
        == """hostname    : worker01
description : None
state       : Idle
health      : Active
devices     : qemu01, bbb-01
last ping   : 20180128T01:01:01
"""
    )


def test_workers_show_json(setup, monkeypatch, capsys):
    version = "2019.1"
    last_ping = xmlrpc.client.DateTime("20180128T01:01:01")
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "workers", "show", "worker01", "--json"]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.workers.show",
                "args": ("worker01",),
                "ret": {
                    "hostname": "worker01",
                    "description": None,
                    "state": "Idle",
                    "health": "Active",
                    "devices": ["qemu01", "bbb-01"],
                    "last_ping": last_ping,
                },
            },
        ],
    )
    assert main() == 0  # nosec
    assert json.loads(capsys.readouterr()[0]) == {  # nosec
        "hostname": "worker01",
        "description": None,
        "state": "Idle",
        "health": "Active",
        "devices": ["qemu01", "bbb-01"],
        "last_ping": "20180128T01:01:01",
    }


def test_workers_show_yaml(setup, monkeypatch, capsys):
    version = "2019.1"
    last_ping = xmlrpc.client.DateTime("20180128T01:01:01")
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "workers", "show", "worker01", "--yaml"]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.workers.show",
                "args": ("worker01",),
                "ret": {
                    "hostname": "worker01",
                    "description": None,
                    "state": "Idle",
                    "health": "Active",
                    "devices": ["qemu01", "bbb-01"],
                    "last_ping": last_ping,
                },
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0]
        == """description: null
devices: [qemu01, bbb-01]
health: Active
hostname: worker01
last_ping: 20180128T01:01:01
state: Idle
"""
    )


def test_workers_update(setup, monkeypatch, capsys):
    version = "2019.1"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "lavacli",
            "workers",
            "update",
            "worker01",
            "--description",
            "worker",
            "--health",
            "ACTIVE",
        ],
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.workers.update",
                "args": ("worker01", "worker", "ACTIVE"),
                "ret": None,
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == ""  # nosec
