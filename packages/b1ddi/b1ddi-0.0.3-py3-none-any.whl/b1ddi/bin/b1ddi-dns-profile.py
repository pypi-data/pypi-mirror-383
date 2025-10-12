#!/usr/bin/env python3

import bloxone
import json
import click
from click_option_group import optgroup
from rich.console import Console
from rich.table import Table


@click.command()
@optgroup.group("BloxOne Configuration File")
@optgroup.option("-c", "--config", default="b1config.ini", help="BloxOne Ini File")
@optgroup.group("BloxOne DNS Config Actions")
@optgroup.option(
    "-g", "--get", is_flag=True, default=False, help="Get current DNS Configurations"
)
@optgroup.option(
    "-n", "--new", is_flag=True, default=False, help="Create new DNS Configurations"
)
@optgroup.option(
    "-d", "--delete", is_flag=True, default=False, help="Delete new DNS Configurations"
)
@optgroup.group("New DNS Profile Options")
@optgroup.option("--name", help="DNS Profile Name")
@optgroup.option("--comment", help="Profile Description")
@optgroup.group("Delete DNS Profile Options")
@optgroup.option("--id", help="Profile ID")
def main(config, get, new, delete, name, comment, id):
    b1ddi = bloxone.b1ddi(config)
    if get:
        get_dns_global(b1ddi)
    if new:
        create_dns_config(b1ddi, name, comment)
    if delete:
        del_dns_config(b1ddi, id)


def get_dns_global(b1ddi):
    response = b1ddi.get("/dns/server")
    if response.status_code == 200:
        dhcpGlobal = response.json()
        table = Table(
            "Created", "Name", "Comment", "ID", title="BloxOne DNS Configurations"
        )
        for x in dhcpGlobal["results"]:
            table.add_row(x["created_at"], x["name"], x["comment"], x["id"])
        console = Console()
        console.print(table)
    else:
        print(response.status_code, response.text)


def create_dns_config(b1ddi, name, comment):
    dnBody = {"name": name, "comment": comment}
    response = b1ddi.create("/dns/server", body=json.dumps(dnBody))
    if response.status_code == 200:
        get_dns_global(b1ddi)
    else:
        print(response.status_code, response.text)


def del_dns_config(b1ddi, id):
    response = b1ddi.delete("/dns/server", id=id)
    if response.status_code == 200:
        get_dns_global(b1ddi)
    else:
        print(response.status_code, response.text)


if __name__ == "__main__":
    main()
