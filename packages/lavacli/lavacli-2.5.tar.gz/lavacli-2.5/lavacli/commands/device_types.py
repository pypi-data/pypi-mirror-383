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

import argparse
import json
import sys

from lavacli.utils import safe_yaml


def configure_parser(parser, version):
    sub = parser.add_subparsers(dest="sub_sub_command", help="Sub commands")
    sub.required = True

    # "add"
    dt_add = sub.add_parser("add", help="add a device type")
    dt_add.add_argument("name", help="name of the device-type")
    dt_add.add_argument("--description", default=None, help="device-type description")
    dt_add.add_argument(
        "--hide",
        dest="display",
        action="store_false",
        default=True,
        help="device is hidden in the UI",
    )
    dt_add.add_argument(
        "--owners-only",
        action="store_true",
        default=False,
        help="devices are only visible to owners",
    )
    dt_health = dt_add.add_argument_group("health check")
    dt_health.add_argument(
        "--health-frequency",
        default=24,
        type=int,
        help="how often to run health checks.",
    )
    dt_health.add_argument(
        "--health-denominator",
        default="hours",
        choices=["hours", "jobs"],
        help="initiate health checks by hours or by jobs.",
    )

    # "aliases"
    dt_aliases = sub.add_parser(
        "aliases", help="manage aliases for the given device-type"
    )
    aliases_sub = dt_aliases.add_subparsers(
        dest="sub_sub_sub_command", help="Sub commands"
    )
    aliases_sub.required = True

    aliases_add = aliases_sub.add_parser("add", help="add aliases")
    aliases_add.add_argument("name", help="name of the device-type")
    aliases_add.add_argument("alias", help="name of alias")

    aliases_delete = aliases_sub.add_parser("delete", help="delete aliases")
    aliases_delete.add_argument("name", help="name of the device-type")
    aliases_delete.add_argument("alias", help="name of alias")

    aliases_list = aliases_sub.add_parser(
        "list", help="list aliases for the device-type"
    )
    aliases_list.add_argument("name", help="device-type")
    out_format = aliases_list.add_mutually_exclusive_group()
    out_format.add_argument(
        "--json",
        dest="output_format",
        default=None,
        action="store_const",
        const="json",
        help="print as json",
    )
    out_format.add_argument(
        "--yaml",
        dest="output_format",
        default=None,
        action="store_const",
        const="yaml",
        help="print as yaml",
    )

    # "devices"
    if version >= (2025, 10):
        dt_devices = sub.add_parser("devices", help="list devices for the device-type")
        dt_devices.add_argument("name", help="Device-type")
        dt_devices.add_argument(
            "--health",
            type=str,
            default=None,
            choices=["GOOD", "UNKNOWN", "LOOPING", "BAD", "MAINTENANCE"],
            help="filter devices by health",
        )

        out_format = dt_devices.add_mutually_exclusive_group()
        out_format.add_argument(
            "--json",
            dest="output_format",
            default=None,
            action="store_const",
            const="json",
            help="print as json",
        )
        out_format.add_argument(
            "--yaml",
            dest="output_format",
            default=None,
            action="store_const",
            const="yaml",
            help="print as yaml",
        )

    # "heath-check"
    dt_hc = sub.add_parser("health-check", help="device-type health-check")
    dt_sub = dt_hc.add_subparsers(dest="sub_sub_sub_command", help="Sub commands")
    dt_sub.required = True
    if version >= (2022, 4):
        dt_delete = dt_sub.add_parser(
            "delete", help="delete the device-type health-check"
        )
        dt_delete.add_argument("name", help="name of the device-type")

    dt_get = dt_sub.add_parser("get", help="get the device-type health-check")
    dt_get.add_argument("name", help="name of the device-type")

    dt_set = dt_sub.add_parser("set", help="set the device-type health-check")
    dt_set.add_argument("name", help="name of the device-type")
    dt_set.add_argument(
        "definition", type=argparse.FileType("r"), help="health-check definition"
    )

    # "list"
    dt_list = sub.add_parser("list", help="list available device-types")
    dt_list.add_argument(
        "--all",
        "-a",
        dest="show_all",
        default=False,
        action="store_true",
        help="show all device types in the database, " "including non-installed ones",
    )
    out_format = dt_list.add_mutually_exclusive_group()
    out_format.add_argument(
        "--json",
        dest="output_format",
        default=None,
        action="store_const",
        const="json",
        help="print as json",
    )
    out_format.add_argument(
        "--yaml",
        dest="output_format",
        default=None,
        action="store_const",
        const="yaml",
        help="print as yaml",
    )

    # "perms"
    if version >= (2023, 3):
        dt_perms = sub.add_parser("perms", help="permissions")
        perms_sub = dt_perms.add_subparsers(
            dest="sub_sub_sub_command", help="Sub commands"
        )
        perms_sub.required = True

        perms_add = perms_sub.add_parser("add", help="add permissions")
        perms_add.add_argument("name", help="name of the device-type")
        perms_add.add_argument("group", help="group")
        perms_add.add_argument("permission", help="permission")

        perms_delete = perms_sub.add_parser("delete", help="delete permissions")
        perms_delete.add_argument("name", help="name of the device-type")
        perms_delete.add_argument("group", help="group")
        perms_delete.add_argument("permission", help="permission")

        perms_list = perms_sub.add_parser("list", help="list permissions")
        perms_list.add_argument("name", help="name of the device-type")
        out_format = perms_list.add_mutually_exclusive_group()
        out_format.add_argument(
            "--json",
            dest="output_format",
            default=None,
            action="store_const",
            const="json",
            help="print as json",
        )
        out_format.add_argument(
            "--yaml",
            dest="output_format",
            default=None,
            action="store_const",
            const="yaml",
            help="print as yaml",
        )

    # "show"
    dt_show = sub.add_parser("show", help="show device-type details")
    dt_show.add_argument("name", help="name of the device-type")
    out_format = dt_show.add_mutually_exclusive_group()
    out_format.add_argument(
        "--json",
        dest="output_format",
        default=None,
        action="store_const",
        const="json",
        help="print as json",
    )
    out_format.add_argument(
        "--yaml",
        dest="output_format",
        action="store_const",
        const="yaml",
        default=None,
        help="print as yaml",
    )

    # "template"
    dt_template = sub.add_parser("template", help="device-type template")
    dt_sub = dt_template.add_subparsers(dest="sub_sub_sub_command", help="Sub commands")
    dt_sub.required = True
    if version >= (2022, 4):
        dt_delete = dt_sub.add_parser(
            "delete", help="delete the custom device-type template"
        )
        dt_delete.add_argument("name", help="name of the device-type")

    dt_get = dt_sub.add_parser("get", help="get the device-type template")
    dt_get.add_argument("name", help="name of the device-type")

    dt_set = dt_sub.add_parser("set", help="set the device-type template")
    dt_set.add_argument("name", help="name of the device-type")
    dt_set.add_argument("template", type=argparse.FileType("r"), help="template file")

    # "update"
    dt_update = sub.add_parser("update", help="update device-type")
    dt_update.add_argument("name", help="name of the device-type")
    dt_update.add_argument(
        "--description", default=None, help="device-type description"
    )

    visibility = dt_update.add_mutually_exclusive_group()
    visibility.add_argument(
        "--hide",
        dest="display",
        action="store_false",
        default=None,
        help="device-type is hidden in the UI",
    )
    visibility.add_argument(
        "--show",
        dest="display",
        action="store_true",
        help="device-type is visible in the UI",
    )

    owner = dt_update.add_mutually_exclusive_group()
    owner.add_argument(
        "--owners-only",
        action="store_true",
        dest="owners_only",
        default=None,
        help="devices are only visible to owners",
    )
    owner.add_argument(
        "--public",
        action="store_false",
        dest="owners_only",
        help="devices are visible to all users",
    )

    dt_health = dt_update.add_argument_group("health check")
    dt_health.add_argument(
        "--health-frequency",
        default=None,
        type=int,
        help="how often to run health checks.",
    )
    dt_health.add_argument(
        "--health-denominator",
        default=None,
        choices=["hours", "jobs"],
        help="initiate health checks by hours or by jobs.",
    )

    health = dt_health.add_mutually_exclusive_group()
    health.add_argument(
        "--health-disabled",
        default=None,
        action="store_true",
        help="disable health checks",
    )
    health.add_argument(
        "--health-active",
        dest="health_disabled",
        action="store_false",
        help="activate health checks",
    )


def help_string():
    return "manage device-types"


def handle_add(proxy, options, _):
    proxy.scheduler.device_types.add(
        options.name,
        options.description,
        options.display,
        options.owners_only,
        options.health_frequency,
        options.health_denominator,
    )
    return 0


def handle_aliases(proxy, options, _):
    if options.sub_sub_sub_command == "add":
        proxy.scheduler.device_types.aliases.add(options.name, options.alias)
    elif options.sub_sub_sub_command == "list":
        aliases = proxy.scheduler.device_types.aliases.list(options.name)
        if options.output_format == "json":
            print(json.dumps(aliases))
        elif options.output_format == "yaml":
            safe_yaml.dump(aliases, sys.stdout)
        else:
            print("Aliases:")
            for alias in aliases:
                print("* %s" % alias)
    else:
        assert options.sub_sub_sub_command == "delete"
        proxy.scheduler.device_types.aliases.delete(options.name, options.alias)
    return 0


def handle_hc(proxy, options, _):
    if options.sub_sub_sub_command == "delete":
        template = proxy.scheduler.device_types.set_health_check(options.name, "")
    elif options.sub_sub_sub_command == "get":
        template = proxy.scheduler.device_types.get_health_check(options.name)
        print(str(template).rstrip("\n"))
    else:
        hc = options.definition.read()
        proxy.scheduler.device_types.set_health_check(options.name, hc)
    return 0


def handle_devices(proxy, options, _):
    devices = proxy.scheduler.device_types.devices(options.name, options.health)

    if options.output_format == "json":
        print(json.dumps(devices))
    elif options.output_format == "yaml":
        safe_yaml.dump(devices, sys.stdout)
    else:
        print("Devices:")
        for d in devices:
            print(f"* {d['hostname']} : {d['state']},{d['health']}")

    return 0


def handle_list(proxy, options, _):
    device_types = proxy.scheduler.device_types.list(options.show_all)

    if options.output_format == "json":
        print(json.dumps(device_types))
    elif options.output_format == "yaml":
        safe_yaml.dump(device_types, sys.stdout)
    else:
        print("Device-Types:")
        for dt in device_types:
            print(f"* {dt['name']} ({dt['devices']})")
    return 0


def handle_perms(proxy, options, _):
    if options.sub_sub_sub_command == "add":
        proxy.scheduler.device_types.perms_add(
            options.name, options.group, options.permission
        )
    elif options.sub_sub_sub_command == "delete":
        proxy.scheduler.device_types.perms_delete(
            options.name, options.group, options.permission
        )
    elif options.sub_sub_sub_command == "list":
        perms = proxy.scheduler.device_types.perms_list(options.name)
        if options.output_format == "json":
            print(json.dumps(perms))
        elif options.output_format == "yaml":
            safe_yaml.dump(perms, sys.stdout)
        else:
            print("Permissions:")
            for perm in perms:
                print("* %s %s" % (perm["group"], perm["name"]))
    return 0


def handle_show(proxy, options, config):
    dt = proxy.scheduler.device_types.show(options.name)

    if options.output_format == "json":
        print(json.dumps(dt))
    elif options.output_format == "yaml":
        safe_yaml.dump(dt, sys.stdout)
    else:
        print("name            : %s" % dt["name"])
        print("description     : %s" % dt["description"])
        print("display         : %s" % dt["display"])
        if config["version"] <= (2019, 7):
            print("owners only     : %s" % dt["owners_only"])
        print("health disabled : %s" % dt["health_disabled"])
        print("aliases         : %s" % dt["aliases"])
        print("devices         : %s" % dt["devices"])
    return 0


def handle_template(proxy, options, _):
    if options.sub_sub_sub_command == "delete":
        template = proxy.scheduler.device_types.set_template(options.name, "")
    elif options.sub_sub_sub_command == "get":
        template = proxy.scheduler.device_types.get_template(options.name)
        print(str(template).rstrip("\n"))
    else:
        template = options.template.read()
        proxy.scheduler.device_types.set_template(options.name, template)
    return 0


def handle_update(proxy, options, _):
    proxy.scheduler.device_types.update(
        options.name,
        options.description,
        options.display,
        options.owners_only,
        options.health_frequency,
        options.health_denominator,
        options.health_disabled,
    )
    return 0


def handle(proxy, options, config):
    handlers = {
        "add": handle_add,
        "aliases": handle_aliases,
        "devices": handle_devices,
        "health-check": handle_hc,
        "list": handle_list,
        "perms": handle_perms,
        "show": handle_show,
        "template": handle_template,
        "update": handle_update,
    }
    return handlers[options.sub_sub_command](proxy, options, config)
