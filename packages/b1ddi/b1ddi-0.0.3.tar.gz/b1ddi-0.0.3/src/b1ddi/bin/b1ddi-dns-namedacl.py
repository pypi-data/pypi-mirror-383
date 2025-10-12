#!/usr/bin/env python3
# TODO
# Add ability to create ACL, delete ACL and update ACL

import bloxone
import click
from rich.console import Console
from rich.table import Table


@click.command()
@click.option(
    "-c", "--config", default="~/b1ddi/b1config.ini", help="BloxOne DDI Config File"
)
@click.option(
    "-g", "--get", is_flag=True, default=False, help="Retrieve ACL Information"
)
def main(config: str, get: bool):
    b1 = bloxone.b1ddi(config)
    if get:
        get_acl(b1)


def get_acl(b1):
    b1_acl = b1.get("/dns/acl")
    if b1_acl.status_code != 200:
        print(b1_acl.status_code, b1_acl.text)
    else:
        named_list = b1_acl.json()
        for x in named_list["results"]:
            table = Table(
                title=x["name"] + " " + x["id"], row_styles=["dim", ""], highlight=True
            )
            table.add_column("Access", justify="center")
            table.add_column("Nested ACL", justify="center")
            table.add_column("Address", justify="center")
            table.add_column("Element", justify="center")
            table.add_column("TSIG", justify="center")
            for y in x["list"]:
                table.add_row(
                    y["access"],
                    y["acl"],
                    y["address"],
                    y["element"],
                    y["tsig_key"],
                )
            console = Console()
            console.print(table)


if __name__ == "__main__":
    main()
