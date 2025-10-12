#!/usr/bin/env python3

import bloxone
import json
import click
from rich.console import Console
from rich.table import Table


@click.command()
@click.option(
    "-c", "--config", default="~/b1ddi/b1config.ini", help="Bloxone DDI Config File"
)
@click.option("--getddns", is_flag=True, help="Retrieve Current DDNS Configuration")
@click.option("--add", is_flag=True, help="Add Current DNS Zone to DDNS Configuration")
def main(config: str, getddns: bool, add: bool):
    b1 = bloxone.b1ddi(config)
    if getddns:
        current_ddns(b1)
    if add:
        add_domains(b1)


def current_ddns(b1):
    b1_ddns = b1.get("/dhcp/global")
    if b1_ddns.status_code != 200:
        print(b1_ddns.status_code, b1_ddns.text)
    else:
        display_ddns(b1_ddns)


def find_zones(b1):
    b1_zones = b1.get("/dns/auth_zone")
    if b1_zones.status_code != 200:
        print(b1_zones.status_code, b1_zones.text)
    else:
        zones = b1_zones.json()
        return zones


def zoneid(b1, zone):
    zone_id = b1.get_id("/dns/auth_zone", key="fqdn", value=zone, include_path=True)
    return zone_id


def viewid(b1, view):
    view_id = b1.get_id("/dns/view", key="name", value=view, include_path=True)
    return view_id


def add_domains(b1):
    ddns_list = []
    dns_zones = find_zones(b1)
    for z in dns_zones["results"]:
        zone_id = zoneid(b1, z["fqdn"])
        ddns_list.append({"zone": zone_id})
    add_ddns(b1, ddns_list)
    current_ddns(b1)


def add_ddns(b1, ddns_zones):
    ddnsBody = {"ddns_zones": ddns_zones}
    ddns_update = b1.replace(
        "/dhcp/global",
        body=json.dumps(ddnsBody),
    )
    if ddns_update.status_code != 200:
        print(ddns_update.status_code, ddns_update.text)


def display_ddns(b1_ddns):
    table = Table(title="UDDI DDNS Zones")
    table.add_column("FQDN", justify="center")
    table.add_column("View Name", justify="center")
    table.add_column("Zone ID", justify="center")
    table.add_column("View ID", justify="center")
    table.add_column("TSIG", justify="center")
    table.add_column("GSS TSGIG", justify="center")
    table.add_column("TSIG Key", justify="center")
    table.add_column("Nameservers ", justify="center")
    b1_ddns_zones = b1_ddns.json()
    for z in b1_ddns_zones["result"]["ddns_zones"]:
        table.add_row(
            z["fqdn"],
            z["view_name"],
            z["zone"],
            z["view"],
            str(z["tsig_enabled"]),
            str(z["gss_tsig_enabled"]),
            z["tsig_key"],
            str(z["nameservers"]),
        )
    console = Console()
    console.print(table)


if __name__ == "__main__":
    main()
