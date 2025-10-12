#!/usr/bin/env python3

import csv
import json
import bloxone
import click
from click_option_group import optgroup
from rich.console import Console
from rich.table import Table

# TODO
# Add Delete Functionality


@click.command()
@optgroup("BloxOne Configuration File")
@optgroup.option(
    "-c", "--config", default="b1config.ini", help="BloxOne Configuration Ini"
)
@optgroup.group("BloxOne File Import")
@optgroup.option("-f", "--file", help="DHCP Options File in NIOS Format")
@optgroup.group("BloxOne Option Actions")
@optgroup.option("-g", "--get", is_flag=True, help="Get DHCP Options")
@optgroup.option("--codes", is_flag=True, help="Get DHCP Option Codes")
@optgroup.option("-n", "--new", is_flag=True, help="New DHCP Options")
@optgroup.group("New DHCP Options")
@optgroup.option("--code", help="DHCP Code")
@optgroup.option("--codetype", help="DHCP Code Type")
@optgroup.option("--allowmultiple", type=bool, default=False, help="Allow Multiple")
@optgroup.option("--optionspace", help="BloneOne DHCP Option Space")
@optgroup.option(
    "--comment", default="Customer Imported DHCP Option", help="DHCP Option Comment"
)
def main(
    config, file, get, new, codes, code, codetype, allowmultiple, optionspace, comment
):
    b1ddi = bloxone.b1ddi(config)
    if get:
        get_dhcp_option_space(b1ddi)
        if codes:
            get_dhcp_option_code(b1ddi)
    if new:
        if file:
            open_file(file, b1ddi, comment, optionspace, allowmultiple)
        else:
            create_dhcp_option(
                b1ddi, allowmultiple, name, code, codetype, comment, optionspace
            )


def get_dhcp_option_space(b1ddi):
    response = b1ddi.get("/dhcp/option_space")
    if response.status_code == 200:
        dhOptionSpace = Table(
            "Created",
            "Name",
            "Comment",
            "ID",
            "Protocol",
            title="BloxOne Global DHCP Option Space",
        )
        dhcpOptions = response.json()
        for x in dhcpOptions["results"]:
            dhOptionSpace.add_row(
                x["created_at"], x["name"], x["comment"], x["id"], x["protocol"]
            )
        console = Console()
        console.print(dhOptionSpace)
    else:
        print(response.status_code, response.text)


def get_dhcp_option_code(b1ddi):
    response = b1ddi.get("/dhcp/option_code")
    if response.status_code == 200:
        dhOptionSpace = Table(
            "Created",
            "Updated",
            "Name",
            "Code",
            "Type",
            "Comment",
            "ID",
            "Option Space",
            "Multiple",
            title="BloxOne Global DHCP Option Codes",
        )
        dhcpOptions = response.json()
        for x in dhcpOptions["results"]:
            dhOptionSpace.add_row(
                x["created_at"],
                x["updated_at"],
                x["name"],
                str(x["code"]),
                x["type"],
                x["comment"],
                x["id"],
                x["option_space"],
                str(x["array"]),
            )
        console = Console()
        console.print(dhOptionSpace)
    else:
        print(response.status_code, response.text)


def create_dhcp_option(
    b1ddi, allowmultiple, name, code, codetype, comment, optionspace
):
    dhcp_code_type = {"T_STRING": "text", "T_ARRAY_IP_ADDRESS": "address4"}
    optionArray = allowmultiple
    if codetype == "T_ARRAY_IP_ADDRESS":
        optionArray = True
    else:
        optionArray = False
    dhcpOptionBody = {
        "array": optionArray,
        "code": code,
        "comment": comment,
        "name": name,
        "type": dhcp_code_type[codetype],
        "option_space": optionspace,
    }
    response = b1ddi.create("/dhcp/option_code", body=json.dumps(dhcpOptionBody))
    if response.status_code == 200:
        # print(response.json())
        new_dhcp_option = response.json()
        newDhcp = Table(
            "Multiple",
            "Code",
            "Name",
            "Comment",
            "ID",
            "Option Space",
            title="New DHCP Option",
        )
        newDhcp.add_row(
            str(new_dhcp_option["result"]["array"]),
            str(new_dhcp_option["result"]["code"]),
            new_dhcp_option["result"]["name"],
            new_dhcp_option["result"]["comment"],
            new_dhcp_option["result"]["id"],
            new_dhcp_option["result"]["option_space"],
        )
        console = Console()
        console.print(newDhcp)
    else:
        print(response.status_code, response.text)


def open_file(file, b1ddi, comment, optionspace, allowmultiple):
    with open(file, newline="") as csvfile:
        dhcp_option_reader = csv.DictReader(csvfile)
        for row in dhcp_option_reader:
            create_dhcp_option(
                b1ddi,
                allowmultiple,
                row["name"],
                row["code"],
                row["type"],
                comment,
                optionspace,
            )


if __name__ == "__main__":
    main()
