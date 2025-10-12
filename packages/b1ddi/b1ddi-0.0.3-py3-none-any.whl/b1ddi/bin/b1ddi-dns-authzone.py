#!/usr/bin/env python3

import bloxone
import click
from rich.console import Console
from rich.table import Column, Table


@click.command()
@click.option(
    "-c",
    "--config",
    default="~/b1ddi/b1config.ini",
    show_default=True,
    help="bloxone ddi config file",
)
@click.option(
    "-g",
    "--get",
    is_flag=True,
    default=False,
    show_default=True,
    help="Retrieve Auth Zones from UDDI",
)
@click.option(
    "--create",
    is_flag=True,
    default=False,
    show_default=True,
    help="Create UDDI Auth Zone",
)
@click.option("--fqdn", default="domain.com", show_default=True, help="Auth Zone Name")
def main(config: str, get: bool, create: bool, fqdn: str):
    b1 = bloxone.b1ddi(config)
    if get:
        get_authzone(b1)
    if create:
        create_authzone(b1, fqdn)


def get_authzone(b1):
    b1_authzone = b1.get("/dns/auth_zone")
    if b1_authzone.status_code != 200:
        print(b1_authzone.status_code, b1_authzone.text)
    else:
        auth_zones = b1_authzone.json()
        print_zones(b1, auth_zones)


def create_authzone(b1, fqdn):
    # TODO
    # Add support for NSG
    # Add support for external primaries
    # Change primary_type to choice arg
    auth_zone_body = {"fqdn": fqdn, "primary_type": "cloud"}
    b1_authzone = b1.create("/dns/auth_zone", body=auth_zone_body)
    if b1_authzone.status_code != 201:
        print(b1_authzone.status_code, b1_authzone.text)
    else:
        print(b1_authzone.json())


def print_zones(b1, auth_zones):
    table = Table(
        Column(header="FQDN", justify="center"),
        Column(header="ID", justify="center"),
        Column(header="NSG", justify="center"),
        Column(header="Grid Primaries", justify="center"),
        Column(header="Grid Secondaries", justify="center"),
        Column(header="Primary Type", justify="center"),
        title="Infoblox UDDI Auth Zones",
        highlight=True,
        row_styles=["dim", ""],
    )
    for az in auth_zones["results"]:
        table.add_row(
            az["fqdn"],
            az["id"],
            get_nsgs_name(b1, az["nsgs"][0]),
            str(az["grid_primaries"]),
            str(az["grid_secondaries"]),
            str(az["primary_type"]),
        )
    console = Console()
    console.print(table)


def get_nsgs_name(b1, nsgs):
    b1_nsg_id = nsgs.split("/")
    b1_nsgs = b1.get("/dns/auth_nsg", id=b1_nsg_id[2])
    if b1_nsgs.status_code != 200:
        print(f"Error retreiving nsgs: {b1_nsgs.status_code} {b1_nsgs.text}")
    else:
        nsgs = b1_nsgs.json()
        return nsgs["result"]["name"]


if __name__ == "__main__":
    main()
