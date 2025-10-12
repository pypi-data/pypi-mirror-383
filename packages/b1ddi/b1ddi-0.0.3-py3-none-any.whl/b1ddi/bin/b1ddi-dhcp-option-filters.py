#!/usr/bin/env python3

import csv
import re
import json
import bloxone
import click
from click_option_group import optgroup
from rich.console import Console
from rich.table import Table

# TODO
# More effective way to look up DHCP Codes


@click.command()
@optgroup.group("BloxOne Configuration File")
@optgroup.option("-c", "--config", default="b1config.ini", help="BloxOne Ini File")
@optgroup.group("BloxOne DHCP Filter Actions")
@optgroup.option("-g", "--get", is_flag=True, help="Retrieve DHCP Option Filters")
@optgroup.option("-n", "--new", is_flag=True, help="Import DHCP Option Filters")
@optgroup.group("BloxOne DHCP Option Filters")
@optgroup.option("-f", "--file", help="CSV Import File")
def main(config, file, get, new):
    b1ddi = bloxone.b1ddi(config)
    if get:
        get_dhcp_filters(b1ddi)
    if new:
        open_file(file, b1ddi)


def get_dhcp_filters(b1ddi):
    response = b1ddi.get("/dhcp/option_filter")
    if response.status_code == 200:
        dhOptFilter = response.json()
        dhOptFilterTable = Table(
            "Created",
            "Name",
            "Comment",
            "DHCP Options: (Code ID, Value)",
            "Bootfile ",
            "Boot Server",
            "Next Server",
            "Rule Match",
            "Rule",
            title="BloxOne DHCP Option Filters",
        )
        # print(response.json())
        for x in dhOptFilter["results"]:
            filterRules = []
            filterOptions = []
            for y in x["dhcp_options"]:
                filterOptions.append(
                    "{}, {}".format(y["option_code"], y["option_value"])
                )
            for r in x["rules"]["rules"]:
                filterRules.append(
                    "{}, {}, {}, {}".format(
                        r["compare"],
                        r["option_code"],
                        r["option_value"],
                        r["substring_offset"],
                    )
                )
            dhOptFilterTable.add_row(
                x["created_at"],
                x["name"],
                x["comment"],
                ("\n").join(filterOptions),
                x["header_option_filename"],
                x["header_option_server_name"],
                x["header_option_server_address"],
                x["rules"]["match"],
                str(x["rules"]["rules"]),
            )
        console = Console()
        console.print(dhOptFilterTable)
    else:
        print(response.status_code, response.text)


def process_dhcp_filter(b1ddi, filterRow):
    # Replace the cache with something faster
    option_lookup_cache = {}
    dhcpOptions = []
    filterRules = []
    # Break Down expression to seperate fields
    if filterRow["OPTION-60"]:
        option_code_60 = lookup_dhcp_codes(b1ddi, "vendor-class-identifier")
        dhcpOptions.append(
            {
                "option_code": option_code_60,
                "option_value": filterRow["OPTION-60"],
                "type": "option",
            }
        )
    if filterRow["OPTION-66"]:
        option_code_66 = lookup_dhcp_codes(b1ddi, "tftp-server-name")
        dhcpOptions.append(
            {
                "option_code": option_code_66,
                "option_value": filterRow["OPTION-66"],
                "type": "option",
            }
        )
    if filterRow["OPTION-67"]:
        option_code_67 = lookup_dhcp_codes(b1ddi, "boot-file-name")
        dhcpOptions.append(
            {
                "option_code": option_code_67,
                "option_value": filterRow["OPTION-67"],
                "type": "option",
            }
        )
    isc_expression = filterRow["expression"]
    expression_pattern = r'\((\w+)\(option\s+([\w-]+),0,(\d+)\)="([^"]+)"'
    expression_rules = re.match(expression_pattern, isc_expression)
    if expression_rules:
        if expression_rules.group(2) in option_lookup_cache:
            opt_d_code = option_lookup_cache[expression_rules.group(2)]
        else:
            opt_d_code = lookup_dhcp_codes(b1ddi, expression_rules.group(2))
            option_lookup_cache[expression_rules.group(2)] = opt_d_code
        filterRules.append(
            {
                "compare": "text_substring",
                "option_code": opt_d_code,
                "option_value": expression_rules.group(4),
                "substring_offset": expression_rules.group(3),
            }
        )
    else:
        expression_pattern = r'\(option\s+([\w-]+)="([^"]+)"\)'
        expression_rules = re.match(expression_pattern, isc_expression)
        if expression_rules:
            if expression_rules.group(1) in option_lookup_cache:
                opt_d_code = option_lookup_cache[expression_rules.group(1)]
            else:
                opt_d_code = lookup_dhcp_codes(b1ddi, expression_rules.group(1))
                option_lookup_cache[expression_rules.group(1)] = opt_d_code
            filterRules.append(
                {
                    "compare": "text_substring",
                    "option_code": opt_d_code,
                    "option_value": expression_rules.group(2),
                    "substring_offset": 0,
                }
            )
        else:
            print("Regex Failed: {}".format(isc_expression))

    dhcpFilterBody = {
        "name": filterRow["name"],
        "comment": filterRow["comment"],
        "header_option_filename": filterRow["boot_file"],
        "header_option_server_name": filterRow["boot_server"],
        "header_option_server_address": filterRow["next_server"],
        "dhcp_options": dhcpOptions,
        "rules": {"match": "all", "rules": filterRules},
    }
    return dhcpFilterBody


def create_dhcp_filter(b1ddi, dhcpOptionFilter):
    response = b1ddi.create("/dhcp/option_filter", body=json.dumps(dhcpOptionFilter))
    if response.status_code == 200:
        print(
            "{} DHCP Option Filter Added Successfully".format(dhcpOptionFilter["name"])
        )
    else:
        print(dhcpOptionFilter["name"], response.status_code, response.text)


def open_file(file, b1ddi):
    with open(file, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            processed_row = process_dhcp_filter(b1ddi, row)
            create_dhcp_filter(b1ddi, processed_row)
    get_dhcp_filters(b1ddi)


def lookup_dhcp_codes(b1ddi, option_code_name):
    response = b1ddi.get_id(
        "/dhcp/option_code", key="name", value=option_code_name, include_path=True
    )
    return response


if __name__ == "__main__":
    main()
