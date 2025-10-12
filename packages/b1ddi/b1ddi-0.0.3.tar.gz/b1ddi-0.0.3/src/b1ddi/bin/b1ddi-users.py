#!/usr/bin/env python3

import bloxone
import click
from rich.console import Console
from rich.table import Column, Table
from rich import box


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
    help="Retrieve UDDI users",
)
def main(config: str, get: bool):
    """Infoblox UDDI User Script"""
    b1 = bloxone.b1platform(config)
    customer = b1.get_current_tenant()
    if get:
        users = get_user_table(b1)
        if users:
            report_user_table(customer, users)
        else:
            print(f"Unable to retreive {customer} UDDI users")


def get_user_table(b1):
    b1_users = b1.get_users()
    if b1_users.status_code != 200:
        print(b1_users.status_code, b1_users.text)
    else:
        return b1_users.json()


def report_user_table(customer, users):
    table = Table(
        Column(header="Name", justify="center"),
        Column(header="Email", justify="center"),
        Column(header="Account ID", justify="center"),
        Column(header="ID", justify="center"),
        Column(header="Sign In Count", justify="center"),
        Column(header="Type", justify="center"),
        Column(header="Created", justify="center"),
        Column(header="Updated", justify="center"),
        Column(header="Confirmation", justify="center"),
        Column(header="Confirmed", justify="center"),
        title=f"Infoblox: {customer} UDDI Users",
        box=box.SIMPLE,
    )
    for u in users["results"]:
        if "sign_in_count" in u:
            login_count = u["sign_in_count"]
        else:
            login_count = None
        if "confirmation_sent_at" in u:
            confirmation_email = u["confirmation_sent_at"]
        else:
            confirmation_email = None
        table.add_row(
            u["name"],
            u["email"],
            u["account_id"],
            u["id"],
            str(login_count),
            u["type"],
            u["created_at"],
            u["updated_at"],
            confirmation_email,
            u["confirmed_at"],
        )
    console = Console()
    console.print(table)


if __name__ == "__main__":
    main()
