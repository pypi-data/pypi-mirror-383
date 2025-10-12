#!/usr/bin/env python3

import bloxone
import json
import click
from click_option_group import optgroup
from rich.console import Console
from rich.table import Table


@click.command()
@optgroup.group("BloxOne Configuration File")
@optgroup.option(
    "-c", "--config", default="b1config.ini", show_default=True, help="BloxOne Ini File"
)
@optgroup.group("BloxOne DHCP Config Actions")
@optgroup.option(
    "-g", "--get", is_flag=True, default=False, help="Get current DHCP Configurations"
)
@optgroup.option(
    "-n", "--new", is_flag=True, default=False, help="Create new DHCP Configurations"
)
@optgroup.option(
    "-d", "--delete", is_flag=True, default=False, help="Delete new DHCP Configurations"
)
@optgroup.option(
    "-u", "--update", is_flag=True, default=False, help="Delete new DHCP Configurations"
)
@optgroup.group("New DHCP Profile Options")
@optgroup.option("--name", help="DHCP Profile Name")
@optgroup.option("--comment", help="Profile Description")
@optgroup.group("DHCP Profile Options")
@optgroup.option("--id", help="Profile or Host ID")
@optgroup.option("--serverid", help="DHCP Server ID")
def main(
    config: str,
    get: bool,
    new: bool,
    delete: bool,
    update: bool,
    name: str,
    comment: str,
    id: str,
    serverid: str,
):
    b1ddi = bloxone.b1ddi(config)
    if get:
        get_dhcp_global(b1ddi)
    if new:
        create_dhcp_config(b1ddi, name, comment)
    if delete:
        del_dhcp_config(b1ddi, id)
    if update:
        assign_dhcp_config(b1ddi, id, serverid)


def get_dhcp_global(b1ddi):
    response = b1ddi.get("/dhcp/server")
    if response.status_code == 200:
        dhcpGlobal = response.json()
        table = Table(
            "Created",
            "Name",
            "Comment",
            "ID",
            title="BloxOne DHCP Configurations",
            highlight=True,
            row_styles=["dim", ""],
        )
        for x in dhcpGlobal["results"]:
            table.add_row(x["created_at"], x["name"], x["comment"], x["id"])
        console = Console()
        console.print(table)
        get_dhcp_hosts(b1ddi)
    else:
        print(response.status_code, response.text)


def get_dhcp_hosts(b1ddi):
    response = b1ddi.get("/dhcp/host")
    if response.status_code == 200:
        b1Hosts = response.json()
        hostTable = Table(
            "Name",
            "Address",
            "ID",
            "Comment",
            "DHCP Profile",
            "DHCP Config ID",
            title="BloxOne DHCP Hosts",
            highlight=True,
            row_styles=["dim", ""],
        )
        for x in b1Hosts["results"]:
            if x["associated_server"] == None:
                x["associated_server"] = {"name": "None"}
            hostTable.add_row(
                x["name"],
                x["address"],
                x["id"],
                x["comment"],
                x["associated_server"]["name"],
                x["server"],
            )
        console = Console()
        console.print(hostTable)
    else:
        print(response.status_code, response.text)


def create_dhcp_config(b1ddi, name, comment):
    dhBody = {"name": name, "comment": comment}
    response = b1ddi.create("/dhcp/server", body=json.dumps(dhBody))
    if response.status_code == 200:
        get_dhcp_global(b1ddi)
    else:
        print(response.status_code, response.text)


def del_dhcp_config(b1ddi, id):
    response = b1ddi.delete("/dhcp/server", id=id)
    if response.status_code == 200:
        get_dhcp_global(b1ddi)
    else:
        print(response.status_code, response.text)


def assign_dhcp_config(b1ddi, id, serverid):
    updateDhcpConfig = {"server": serverid}
    response = b1ddi.update("/dhcp/host", id=id, body=json.dumps(updateDhcpConfig))
    if response.status_code == 200:
        get_dhcp_global(b1ddi)
    else:
        print(response.status_code, response.text)


if __name__ == "__main__":
    main()
