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

import sys

from lavacli import main
from lavacli.utils import safe_yaml


def test_identities_add(setup, monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "lavacli",
            "identities",
            "add",
            "v.l.o",
            "--uri",
            "https://validation.linaro.org/RPC2",
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == ""  # nosec

    with (tmp_path / "lavacli.yaml").open() as f_in:
        data = safe_yaml.load(f_in)
        assert set(data.keys()) == {"default", "v.l.o"}  # nosec
        assert data["default"] == {"uri": "https://lava.example.com/RPC2"}  # nosec
        assert data["v.l.o"] == {"uri": "https://validation.linaro.org/RPC2"}  # nosec


def test_identities_add_1(setup, monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "lavacli",
            "identities",
            "add",
            "v.l.o",
            "--uri",
            "https://validation.linaro.org/RPC2",
            "--proxy",
            "http://proxy:3128",
            "--username",
            "admin",
            "--token",
            "12345",
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == ""  # nosec

    with (tmp_path / "lavacli.yaml").open() as f_in:
        data = safe_yaml.load(f_in)
        assert set(data.keys()) == {"default", "v.l.o"}  # nosec
        assert data["default"] == {"uri": "https://lava.example.com/RPC2"}  # nosec
        assert data["v.l.o"] == {  # nosec
            "uri": "https://validation.linaro.org/RPC2",
            "proxy": "http://proxy:3128",
            "username": "admin",
            "token": "12345",
        }


def test_identities_add_empty_config(setup, monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "lavacli",
            "identities",
            "add",
            "v.l.o",
            "--uri",
            "https://validation.linaro.org/RPC2",
        ],
    )
    (tmp_path / "lavacli.yaml").unlink()
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == ""  # nosec

    with (tmp_path / "lavacli.yaml").open() as f_in:
        data = safe_yaml.load(f_in)
        assert set(data.keys()) == {"v.l.o"}  # nosec
        assert data["v.l.o"] == {"uri": "https://validation.linaro.org/RPC2"}  # nosec


def test_identities_delete(setup, monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(sys, "argv", ["lavacli", "identities", "delete", "v.l.o"])
    with (tmp_path / "lavacli.yaml").open("w") as f_conf:
        f_conf.write(
            "default:\n  uri: https://lava.example.com/RPC2\nv.l.o:\n  uri: https://validation.linaro.org/RPC"
        )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == ""  # nosec

    with (tmp_path / "lavacli.yaml").open() as f_in:
        data = safe_yaml.load(f_in)
        assert list(data.keys()) == ["default"]  # nosec
        assert data["default"] == {"uri": "https://lava.example.com/RPC2"}  # nosec


def test_identities_delete_empty_config(setup, monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(sys, "argv", ["lavacli", "identities", "delete", "v.l.o"])
    (tmp_path / "lavacli.yaml").unlink()
    assert main() == 1  # nosec
    assert capsys.readouterr()[1] == "Unknown identity 'v.l.o'\n"  # nosec
    assert not (tmp_path / "lavacli.yaml").exists()  # nosec


def test_identities_delete_missing_key(setup, monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(sys, "argv", ["lavacli", "identities", "delete", "v.l.o"])
    assert main() == 1  # nosec
    assert capsys.readouterr()[1] == "Unknown identity 'v.l.o'\n"  # nosec

    with (tmp_path / "lavacli.yaml").open() as f_in:
        data = safe_yaml.load(f_in)
        assert list(data.keys()) == ["default"]  # nosec
        assert data["default"] == {"uri": "https://lava.example.com/RPC2"}  # nosec


def test_identities_list(setup, monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(sys, "argv", ["lavacli", "identities", "list"])
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "Identities:\n* default\n"  # nosec

    with (tmp_path / "lavacli.yaml").open() as f_in:
        data = safe_yaml.load(f_in)
        assert list(data.keys()) == ["default"]  # nosec
        assert data["default"] == {"uri": "https://lava.example.com/RPC2"}  # nosec


def test_identities_list_1(setup, monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(sys, "argv", ["lavacli", "identities", "list"])
    with (tmp_path / "lavacli.yaml").open("w") as f_conf:
        f_conf.write(
            "default:\n  uri: https://lava.example.com/RPC2\nv.l.o:\n  uri: https://validation.linaro.org/RPC2"
        )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "Identities:\n* default\n* v.l.o\n"  # nosec

    with (tmp_path / "lavacli.yaml").open() as f_in:
        data = safe_yaml.load(f_in)
        assert set(data.keys()) == {"default", "v.l.o"}  # nosec
        assert data["default"] == {"uri": "https://lava.example.com/RPC2"}  # nosec
        assert data["v.l.o"] == {"uri": "https://validation.linaro.org/RPC2"}  # nosec


def test_identities_list_2(setup, monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(sys, "argv", ["lavacli", "identities", "list"])
    (tmp_path / "lavacli.yaml").unlink()
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "Identities:\n"  # nosec
    assert not (tmp_path / "lavacli.yaml").exists()  # nosec


def test_identities_show(setup, monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(sys, "argv", ["lavacli", "identities", "show", "default"])
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "uri: https://lava.example.com/RPC2\n"  # nosec


def test_identities_show_missing(setup, monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(sys, "argv", ["lavacli", "identities", "show", "missing"])
    assert main() == 1  # nosec
    assert capsys.readouterr()[1] == "Unknown identity 'missing'\n"  # nosec


def test_identities_show_no_config(setup, monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(sys, "argv", ["lavacli", "identities", "show", "default"])
    (tmp_path / "lavacli.yaml").unlink()
    assert main() == 1  # nosec
    assert capsys.readouterr()[1] == "Unknown identity 'default'\n"  # nosec


def test_identities_show_invalid_config(setup, monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(sys, "argv", ["lavacli", "identities", "show", "default"])
    with (tmp_path / "lavacli.yaml").open("w") as f_conf:
        f_conf.write("hello")
    assert main() == 1  # nosec
    assert capsys.readouterr()[1] == "Invalid configuration file\n"  # nosec
