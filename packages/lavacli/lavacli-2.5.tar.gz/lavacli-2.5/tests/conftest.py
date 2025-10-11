# vim: set ts=4

# Copyright 2017 Rémi Duraffort
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

import xmlrpc.client

import pytest

from lavacli.utils import safe_yaml


class RecordingProxyFactory:
    def __new__(cls, proxy_data):
        class RecordingProxy:
            data = proxy_data

            def __init__(self, uri, allow_none, transport):
                self.request = []

            def __call__(self, *args):
                request = ".".join(self.request)
                self.request = []
                data = self.data.pop(0)
                assert request == data["request"]  # nosec
                assert args == data["args"]  # nosec
                ret = data["ret"]
                if isinstance(ret, dict) and ret.get("fault_code"):
                    raise xmlrpc.client.Fault(ret.get("fault_code"), "fault string")
                return ret

            def __getattr__(self, attr):
                self.request.append(attr)
                return self

        return RecordingProxy


@pytest.fixture
def setup(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    with (tmp_path / "lavacli.yaml").open("w") as f_conf:
        safe_yaml.dump({"default": {"uri": "https://lava.example.com/RPC2"}}, f_conf)
    monkeypatch.setattr(xmlrpc.client, "ServerProxy", RecordingProxyFactory(None))
