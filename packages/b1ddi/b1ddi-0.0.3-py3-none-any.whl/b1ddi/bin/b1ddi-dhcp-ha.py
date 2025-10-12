#!/usr/bin/env python3

import bloxone
import json
import click
from click_option_group import optgroup
from rich.console import Console
from rich.table import Table


@click.command()
@optgroup.group("BloxOne Configuration")
@optgroup.option(
    "-c", "--config", default="b1config.ini", help="BloxOne Configuration File"
)
@optgroup.group("BloxOne DHCP HA Actions")
@optgroup.option("-g", "--get", is_flag=True, help="Retreive DHCP HA Configurations")
@optgroup.option("-n", "--new", is_flag=True, help="New DHCP HA Configurations")
@optgroup.option("-d", "--delete", is_flag=True, help="Delete DHCP HA Configurations")
@optgroup.group("New DHCP HA Options")
@optgroup.option("--comment", default="This is an API Test", help="DHCP Description")
@optgroup.option("--name", default="Internal-HA", help="DHCP HA Name")
@optgroup.option(
    "--hosts", default=[], multiple=True, help="DHCP HA Hosts Format: hostid:ipaddress"
)
@optgroup.option("--ipspace", help="IP Space ID")
@optgroup.group("Delete DHCP HA Options")
@optgroup.option("--id", help="DHCP HA ID")
def main(config, get, new, delete, comment, name, hosts, ipspace, id):
    b1ddi = bloxone.b1ddi(config)
    if get:
        get_dhcp_ha(b1ddi)
    if new:
        create_dhcp_ha(b1ddi, comment, name, hosts, ipspace)
    if delete:
        del_dhcp_ha(b1ddi, id)


def get_dhcp_ha(b1ddi):
    response = b1ddi.get("/dhcp/ha_group")
    if response.status_code == 200:
        dhcpHa = response.json()
        dhcpHaTable = Table(
            "Name",
            "Comment",
            "Address",
            "Role",
            "DHCP Host",
            "DHCP Host ID",
            "IP Space",
            "ID",
            title="BloxOne DHCP HA Groups",
        )
        for x in dhcpHa["results"]:
            for y in x["hosts"]:
                rawHostId = y["host"]
                dhcpHostId = rawHostId.split("/")
                dhcpHostname = get_dhcp_hosts(b1ddi, dhcpHostId[2])
                dhcpHaTable.add_row(
                    x["name"],
                    x["comment"],
                    y["address"],
                    y["role"],
                    dhcpHostname,
                    y["host"],
                    x["ip_space"],
                    x["id"],
                )
        console = Console()
        console.print(dhcpHaTable)
    else:
        print(response.status_code, response.text)


def get_dhcp_hosts(b1ddi, id):
    response = b1ddi.get("/dhcp/host", id=id)
    if response.status_code == 200:
        dhcpHosts = response.json()
        return dhcpHosts["result"]["name"]
    else:
        print(response.status_code, response.text)


def create_dhcp_ha(b1ddi, comment, name, hosts, ipspace):
    haHosts = []
    for h in hosts:
        host, address = h.split(":")
        haHosts.append({"host": host, "address": address, "role": "active"})
    dhcpHaBody = {"name": name, "comment": comment, "hosts": haHosts}
    response = b1ddi.create("/dhcp/ha_group", body=json.dumps(dhcpHaBody))
    if response.status_code == 200:
        get_dhcp_ha(b1ddi)
    else:
        print(response.status_code, response.text)


def del_dhcp_ha(b1ddi, id):
    response = b1ddi.delete("/dhcp/ha_group", id=id)
    if response.status_code == 200:
        get_dhcp_ha(b1ddi)
    else:
        print(response.status_code, response.text)


if __name__ == "__main__":
    main()
