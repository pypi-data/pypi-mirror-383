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
    "-c",
    "--config",
    default="b1config.ini",
    help="File containing BloxOne login information",
)
@optgroup.group("BloxOne Actions")
@optgroup.option("-g", "--get", is_flag=True, help="Retreive IP Spaces")
@optgroup.option("-n", "--new", is_flag=True, help="Create new IP Space")
@optgroup.option("-d", "--delete", is_flag=True, help="Create new IP Space")
@optgroup.group("IP Space ID")
@optgroup.option("-i", "--id", help="IP Space ID")
@optgroup.group("New IP Space Options")
@optgroup.option("--name", help="IP Space Name")
@optgroup.option("--comment", help="IP Space Comment")
def main(config, get, new, delete, id, name, comment):
    b1ddi = bloxone.b1ddi(config)
    if get:
        get_ip_space(b1ddi)
    if new:
        new_ip_space(b1ddi, name, comment)
    if delete:
        del_ip_space(b1ddi, id)


def get_ip_space(b1ddi):
    response = b1ddi.get("/ipam/ip_space")
    if response.status_code == 200:
        ip_space = response.json()
        table = Table(
            "Created", "Name", "ID", "Comment", "Tags", title="BloxOne UDDI IP Space"
        )
        for x in ip_space["results"]:
            table.add_row(x["created_at"], x["name"], x["id"], x["comment"], x["tags"])
        console = Console()
        console.print(table)

    else:
        print(response.status_code, response.text)


def new_ip_space(b1ddi, name, comment):
    ipsBody = {"name": name, "comment": comment}
    response = b1ddi.create("/ipam/ip_space", body=json.dumps(ipsBody))
    if response.status_code == 200:
        get_ip_space(b1ddi)
    else:
        print(response.status_code, response.text)


def del_ip_space(b1ddi, id):
    response = b1ddi.delete("/ipam/ip_space", id=id)
    if response.status_code == 200:
        get_ip_space(b1ddi)
    else:
        print(response.status_code, response.text)


if __name__ == "__main__":
    main()
