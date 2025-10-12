#!/usr/bin/env python3

import bloxone
import json
import click
from click_option_group import optgroup
from rich.console import Console
from rich.table import Table

# TODO
# Add ability to delete hosts
# Add ability to delete services


@click.command()
@optgroup.group("BloxOne Configuration file")
@optgroup.option(
    "-c", "--config", default="b1config.ini", help="BloxOne Configuration File"
)
@optgroup.group("BloxOne Host Services Actions")
@optgroup.option(
    "-g", "--get", is_flag=True, help="Retreive BloxOne Hosts and Services"
)
@optgroup.group("BloxOne Hosts")
@optgroup.option("--hosts", is_flag=True, help="Create / Update BloxOne Hosts")
@optgroup.option(
    "-u", "--update", is_flag=True, help="Update BloxOne Hosts and Services"
)
@optgroup.group("BloxOne Services")
@optgroup.option(
    "--services", is_flag=True, help="Create / Update BloxOne Services"
)
@optgroup.option("-n", "--new", is_flag=True, help="Create BloxOne Service Resource")
@optgroup.group("Host and Service Options")
@optgroup.option("--name", help="BloxOne Host or Service Name")
@optgroup.option("--id", help="BloxOne Host ID")
@optgroup.option("--poolid", help="BloxOne Host Pool ID")
@optgroup.option("--ipspace", help="IP Space ID")
@optgroup.option(
    "--comment", default="Script API Testing", help="Comment for Host or Service"
)
@optgroup.group(" Service Options")
@optgroup.option(
    "--servicetype",
    type=click.Choice(
        [
            "dns",
            "dhcp",
            "ntp"
        ],
        case_sensitive=True,
    ),
)
@optgroup.group("Start or Stop Services")
@optgroup.option(
    "--desiredstate",
    type=click.Choice(["start", "stop"], case_sensitive=True),
    help="Start or Stop Service on Creation",
)
def main(
    config,
    get,
    hosts,
    services,
    new,
    update,
    name,
    id,
    poolid,
    ipspace,
    servicetype,
    desiredstate,
    comment,
):
    b1infra = bloxone.b1infra(config)
    if get:
        get_b1_hosts(b1infra)
    if hosts and update:
        update_b1_host(b1infra, id, poolid, name, ipspace)
    if services and new:
        create_service_resource(
            b1infra, name, servicetype, poolid, comment, desiredstate
        )
    if services and desiredstate:
        start_stop_service(b1infra, id, name, servicetype, poolid, desiredstate)


def get_b1_hosts(b1infra):
    response = b1infra.b1_hosts()
    if response.status_code == 200:
        hosts = response.json()
        hTable = Table(
            "Name", "ID", "IP Address", "IP Space", "Pool ID", title="BloxOne Hosts"
        )
        sTable = Table(
            "Name",
            "ID",
            "Service ID",
            "Service Type",
            title="BloxOne Host Service Assignment",
        )
        for x in hosts["results"]:
            if "ip_space" not in x:
                x["ip_space"] = "None"
            hTable.add_row(
                x["display_name"], x["id"], x["ip_address"], x["ip_space"], x["pool_id"]
            )
            for y in x["configs"]:
                sTable.add_row(
                    x["display_name"], y["id"], y["service_id"], y["service_type"]
                )
        console = Console()
        console.print(hTable)
        console.print(sTable)
        get_b1_services(b1infra)
    else:
        print(response.status_code, response.text)


def get_b1_services(b1infra):
    response = b1infra.get("/services")
    if response.status_code == 200:
        # print(response.json())
        services_infra = response.json()
        sTable = Table(
            "Created",
            "Name",
            "Description",
            "Service Type",
            "Desired State",
            "Pool ID",
            "Host",
            title="BloxOne Services",
        )
        for x in services_infra["results"]:
            if "description" not in x:
                x["description"] = "None"
            raw_hostid = x["configs"][0]["host_id"]
            hostId = raw_hostid.split("/")
            b1_display_name = get_b1_hostname(b1infra, hostId[2])
            sTable.add_row(
                x["created_at"],
                x["name"],
                x["description"],
                x["service_type"],
                x["desired_state"],
                x["pool_id"],
                b1_display_name,
            )
        console = Console()
        console.print(sTable)
    else:
        print(response.status_code, response.text)


def get_b1_hostname(b1infra, id):
    response = b1infra.get("/hosts", id=id)
    if response.status_code == 200:
        b1_name = response.json()
        return b1_name["result"]["display_name"]
    else:
        print(response.status_code, response.text)


def create_service_resource(b1infra, name, servicetype, poolid, commenti, desiredstate):
    b1ServiceBody = {
        "name": name,
        "service_type": servicetype,
        "pool_id": poolid,
        "desired_state": desiredstate,
        "description": comment,
    }
    response = b1infra.create("/services", body=json.dumps(b1ServiceBody))
    if response.status_code == 201:
        get_b1_hosts(b1infra)
    else:
        print(response.status_code, response.text)


def update_b1_host(b1infra, id, poolid, displayname, ipspace):
    b1HostUpdate = {"pool_id": poolid, "display_name": displayname, "ip_space": ipspace}
    response = b1infra.update("/hosts", id=id, body=json.dumps(b1HostUpdate))
    if response.status_code == 200:
        get_b1_hosts(b1infra)
    else:
        print(response.status_code, response.text)


def start_stop_service(b1infra, id, name, servicetype, poolid, desiredstate):
    disableBody = {
        "name": name,
        "service_type": servicetype,
        "pool_id": poolid,
        "desired_state": desiredstate,
    }
    response = b1infra.update("/services", id=id, body=json.dumps(disableBody))
    if response.status_code == 200:
        get_b1_hosts(b1infra)
    else:
        print(response.status_code, response.text)


if __name__ == "__main__":
    main()
