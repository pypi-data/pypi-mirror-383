#!/usr/bin/env python3

import bloxone
import click
from rich.console import Console
from rich.table import Column, Table
from rich import box


@click.command()
@click.option(
    "-c", "--config", default="~/b1ddi/b1config.ini", help="bloxone ddi config file"
)
@click.option(
    "-g",
    "--get",
    is_flag=True,
    default=False,
    show_default=True,
    help="Retrieve DNS views",
)
def main(config: str, get: bool):
    """Example Infoblox UDDI python script"""
    b1 = bloxone.b1ddi(config)
    if get:
        dns_view = get_view(b1)
        if dns_view:
            report_dns_view(dns_view)
        else:
            print("Unable to retreive UDDI DNS Views")


def get_view(b1):
    b1_dns_view = b1.get("/dns/view")
    if b1_dns_view.status_code != 200:
        print(b1_dns_view.status_code, b1_dns_view.text)
    else:
        return b1_dns_view.json()


def report_dns_view(dns_view):
    table = Table(
        Column(header="Name", justify="center"),
        Column(header="ID", justify="center"),
        Column(header="IP Space", justify="center"),
        Column(header="Comment", justify="center"),
        Column(header="Created", justify="center"),
        Column(header="Updated", justify="center"),
        title="Infoblox UDDI DNS Views",
        box=box.SIMPLE,
    )
    for v in dns_view["results"]:
        table.add_row(
            v["name"],
            v["id"],
            str(v["ip_spaces"]),
            str(v["comment"]),
            v["created_at"],
            v["updated_at"],
        )
    console = Console()
    console.print(table)


if __name__ == "__main__":
    main()
