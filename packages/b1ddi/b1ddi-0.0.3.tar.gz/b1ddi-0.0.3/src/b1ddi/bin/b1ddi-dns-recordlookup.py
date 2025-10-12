#!/usr/bin/env python3
# TODO
# Fix tables to display all information returned by BloxOne

import bloxone
import click
from rich.console import Console
from rich.table import Table


@click.command()
@click.option(
    "-c", "--config", default="~/b1ddi/b1config.ini", help="bloxone ddi config file"
)
@click.option("--hostname", help="Hostname to Search")
@click.option("-r", "--raw", is_flag=True, help="Display Output in JSON Format")
@click.option("-s", "--simple", is_flag=True, help="Display Output in Simple Format")
@click.option("-p", "--pretty", is_flag=True, help="Display Output in Table")
def main(config: str, hostname: str, raw: bool, simple: bool, pretty: bool):
    """Tool to Search BloxOne DNS records for record information"""
    table = Table(
        "FQDN",
        "Zone",
        "Created",
        "DNS Name",
        "RDATA",
        "ID",
        "Source",
        "TTL",
        "Type",
        title="BloxOne Record Lookup",
    )
    b1 = bloxone.b1ddi(config)
    b1_id = b1.get_id(
        "/dns/record", key="name_in_zone", value=hostname, include_path=False
    )
    if b1_id:
        b1_record = b1.get("/dns/record", id=b1_id)
        if b1_record.status_code != 200:
            print(b1_record.status_code, b1_record.text)
        else:
            record = b1_record.json()
            if raw:
                print(b1_record.json())
            elif simple:
                for x in record["result"]:
                    print("{}: {}".format(x, record["result"][x]))
            elif pretty:
                table.add_row(
                    record["result"]["dns_absolute_name_spec"],
                    record["result"]["dns_absolute_zone_name"],
                    record["result"]["created_at"],
                    record["result"]["dns_name_in_zone"],
                    record["result"]["dns_rdata"],
                    record["result"]["id"],
                    str(record["result"]["source"]),
                    str(record["result"]["ttl"]),
                    record["result"]["type"],
                )
                console = Console()
                console.print(table)
            else:
                print("Output format not specified")
    else:
        print("ID Not Found")


if __name__ == "__main__":
    main()
