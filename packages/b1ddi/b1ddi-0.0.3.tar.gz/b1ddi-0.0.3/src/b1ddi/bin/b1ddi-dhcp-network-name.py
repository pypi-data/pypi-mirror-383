#!/usr/bin/env python3
# TODO Clean up display output

import bloxone
import logging
import json
import csv
import click
from click_option_group import optgroup
# Uncomment to enable debug logging
# logging.basicConfig(level=logging.DEBUG)


@click.command()
@optgroup.group(
    "Bloxone Configuration File", help="Tool for updating the subnet name field"
)
@optgroup.option("-c", "--config", default="b1config.ini", help="Bloxone INI File")
@optgroup.group("File Input")
@optgroup.option("-f", "--file", help="CSV File containing networks to be updated")
@optgroup.group("Bloxone Actions")
@optgroup.option(
    "-u", "--update", is_flag=True, help="Apply updates from provided file input"
)
def main(config, file, update):
    # Read config file for UDDI key
    b1ddi = bloxone.b1ddi(config)
    if file:
        with open(file, mode="r") as input_file:
            csv_reader = csv.DictReader(input_file)
            for row in csv_reader:
                net_id = get_network_id(b1ddi, row["Prefix"])
                if net_id:
                    print(
                        "Update {} Network ID: {} Name: {}".format(
                            row["Prefix"], net_id, row["Comment"]
                        )
                    )
                    if update:
                        update_network_name(b1ddi, net_id, row["Comment"])
                else:
                    print("Review {} Network ID not found".format(row["Prefix"]))
    else:
        print("No Input File Specified")


def get_network_id(b1ddi, network):
    # Lookup UDDI ID from network value
    net, cidr = network.split("/")
    network_id = b1ddi.get_id("/ipam/subnet", key="address", value=net)
    if network_id:
        return network_id
    else:
        return None


def update_network_name(b1ddi, id, name):
    print("Retreving B1DDI Object")
    b1ddi_subnet = b1ddi.get("/ipam/subnet", id=id)
    if b1ddi_subnet.status_code == 200:
        subnet = b1ddi_subnet.json()
        # Determine if name field is already populated or not
        if subnet["result"]["name"] == "":
            print("Applying Name Field Update: ID: {} Name: {}".format(id, name))
            # Use replace instead of update to get the correct http verb
            updated_network = b1ddi.replace(
                "/ipam/subnet", id=id, body=json.dumps({"name": name})
            )
            if updated_network.status_code == 200:
                print("Name Field Updated: ID: {} Name: {}".format(id, name))
            else:
                print(updated_network.status_code, updated_network.text)
        else:
            print("Current Name Assigned: ", subnet["result"]["name"])
    else:
        print(b1ddi_subnet.status_code, b1ddi_subnet.text)


if __name__ == "__main__":
    main()
