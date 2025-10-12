#!/usr/bin/env python3

import bloxone
import click
from click_option_group import optgroup
from rich.console import Console
from rich.table import Column, Table


@click.command()
@optgroup.group("Bloxone Configuration")
@optgroup.option(
    "-c",
    "--config",
    default="~/b1ddi/b1config.ini",
    show_default=True,
    help="Bloxone DDI Config File",
)
@optgroup.group("Get Actions")
@optgroup.option(
    "-g", "--get", is_flag=True, help="Retrieve current DHCP Configuration Profiles"
)
def main(config: str, get: bool):
    b1 = bloxone.b1ddi(config)
    if get:
        get_dhcp_server_config(b1)


def get_dhcp_server_config(b1):
    b1_subnet = b1.get("/dhcp/server")
    if b1_subnet.status_code != 200:
        print(b1_subnet.status_code, b1_subnet.text)
    else:
        configprofile = b1_subnet.json()
        displayresults(configprofile["results"])


def displayresults(results):
    table = Table(
        Column("Name", justify="center"),
        Column("ID", justify="center"),
        Column("Comment", justify="center"),
        Column("Profile Type", justify="center"),
        Column("Created", justify="center"),
        title="UDDI DHCP Configuration Profiles",
        row_styles=["dim", ""],
        highlight=True,
    )
    for c in results:
        table.add_row(
            c["name"], c["id"], c["comment"], c["profile_type"], c["created_at"]
        )
    console = Console()
    console.print(table)


if __name__ == "__main__":
    main()
