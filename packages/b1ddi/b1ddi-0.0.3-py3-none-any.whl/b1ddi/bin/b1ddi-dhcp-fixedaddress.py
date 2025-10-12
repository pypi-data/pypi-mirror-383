#!/usr/bin/env python3

import csv
import json
import bloxone
import click


@click.command()
@click.option(
    "-c", "--config", default="~/b1ddi/b1config.ini", help="Bloxone ddi config file"
)
@click.option("-f", "--file", help="CSV Input File")
@click.option("-s", "--ipspace", help="CSV Input File")
def main(config: str, file: str, ipspace: str):
    b1 = bloxone.b1ddi(config)
    readcsv(b1, ipspace, file)


def readcsv(b1, ipspace, file):
    with open(file, newline="", encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile, dialect="excel")
        for row in reader:
            ip_space = getspaceid(b1, ipspace)
            createfixed(b1, ip_space, row["Name"], row["MAC"], row["IP"])


def getspaceid(b1, ipspace):
    space_id = b1.get_id("/ipam/ip_space", key="name", value=ipspace, include_path=True)
    return space_id


def createfixed(b1, ip_space, name, mac, ip):
    faBody = {
        "address": ip,
        "match_type": "mac",
        "match_value": mac,
        "comment": name,
        "ip_space": ip_space,
    }
    fixed_addr = b1.create("/dhcp/fixed_address", body=json.dumps(faBody))
    if fixed_addr.status_code != 200:
        print(fixed_addr.status_code, fixed_addr.text)
    else:
        print(fixed_addr.json())


if __name__ == "__main__":
    main()
