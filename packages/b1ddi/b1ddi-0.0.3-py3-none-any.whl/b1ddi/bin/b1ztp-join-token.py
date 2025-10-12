#!/usr/bin/env python3

import bloxone
import json
import click
from click_option_group import optgroup
from rich.console import Console
from rich.table import Table

# TODO
# Add code to save join token to file


@click.command()
@optgroup.group("BloxOne Configuration")
@optgroup.option(
    "--config", default="b1config.ini", help="File containing BloxOne API Key"
)
@optgroup.group("BloxOne Zero Touch Provisioning Join Token Actions")
@optgroup.option(
    "-l", "--list", is_flag=True, default=False, help="List current join tokens"
)
@optgroup.option(
    "-c", "--create", is_flag=True, default=False, help="Create join token"
)
@optgroup.option(
    "-d", "--delete", is_flag=True, default=False, help="Delete join token"
)
@optgroup.option(
    "-r",
    "--registration",
    is_flag=True,
    default=False,
    help="Registration verification",
)
@optgroup.group("B1ZTP ID")
@optgroup.option("-i", "--id", type=str, help="Join Token ID")
def main(config, list, create, delete, registration, id):
    b1ztp = bloxone.b1ztp(config)
    if list:
        if id:
            response = b1ztp.get("/jointoken", id=id)
        else:
            response = b1ztp.get("/jointoken")
        if response.status_code == 200:
            list_token(response.json())
        else:
            print(response.status_code, response.text)

    if create:
        # Collect name and description information from user
        name = input("UDDI Join Token Name:")
        description = input("UDDI Join Token Description:")
        jToken = {"name": name, "description": description}
        # Create token
        response = b1ztp.create("/jointoken", body=json.dumps(jToken))
        if response.status_code == 201:
            create_token(response.json())
        else:
            print(response.status_code, response.text)

    if delete:
        if id:
            response = b1ztp.delete("/jointoken", id=id)
            if response.status_code == 204:
                print("{} deleted successfully".format(id))
            else:
                print(response.status_code, response.text)
        else:
            print("No ID Provided")

    if registration:
        federation = input("Federation: True or False")
        if id:
            rToken = {"federation": federation, "join_token": id}
        else:
            joinToken = input("Join Token: ")
            rToken = {"federation": federation, "join_token": joinToken}
        response = b1ztp.create("/registration/verify", body=json.dumps(rToken))
        if response.status_code == 201:
            print("Verification Complete")
        else:
            print(response.status_code, response.text)


def list_token(response):
    table = Table(title="BloxOne Join Tokens")
    joinToken = response
    if "results" in joinToken:
        table.add_column("ID", justify="center")
        table.add_column("Last Used", justify="center")
        table.add_column("Name", justify="center")
        table.add_column("Status", justify="center")
        table.add_column(
            "Token ID",
            justify="center",
        )
        table.add_column("Use Counter", justify="center")
        for x in joinToken["results"]:
            if "last_used_at" in x:
                table.add_row(
                    x["id"],
                    x["last_used_at"],
                    x["name"],
                    x["status"],
                    x["token_id"],
                    str(x["use_counter"]),
                )
            else:
                table.add_row(
                    x["id"],
                    "Unused",
                    x["name"],
                    x["status"],
                    x["token_id"],
                    str(x["use_counter"]),
                )
    else:
        table.add_column("ID", justify="center")
        table.add_column("Last Used", justify="center")
        table.add_column("Name", justify="center")
        table.add_column("Status", justify="center")
        table.add_column(
            "Token ID",
            justify="center",
        )
        table.add_column("Use Counter", justify="center")
        table.add_row(
            joinToken["result"]["id"],
            joinToken["result"]["description"],
            joinToken["result"]["name"],
            joinToken["result"]["status"],
            joinToken["result"]["token_id"],
            str(joinToken["result"]["use_counter"]),
        )
    console = Console()
    console.print(table)


def create_token(response):
    table = Table(title="BloxOne Join Tokens")
    createToken = response
    table.add_column("ID", justify="center")
    table.add_column("Last Used", justify="center")
    table.add_column("Name", justify="center")
    table.add_column("Status", justify="center")
    table.add_column(
        "Token ID",
        justify="center",
    )
    table.add_column("Use Counter", justify="center")
    table.add_row(
        createToken["join_token"],
        createToken["result"]["token_id"],
        createToken["result"]["id"],
        createToken["result"]["name"],
        createToken["result"]["description"],
        str(createToken["result"]["use_counter"]),
    )
    console = Console()
    console.print(table)


if __name__ == "__main__":
    main()
