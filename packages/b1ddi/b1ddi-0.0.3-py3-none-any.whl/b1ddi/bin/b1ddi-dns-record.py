#!/usr/bin/env python3

import bloxone
import click


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
    b1 = bloxone.b1ddi(config)
    if get:
        tenant_records = get_record(b1)
        if tenant_records:
            for r in tenant_records:
                print(r)


def get_record(b1):
    b1_record = b1.get("/dns/record")
    if b1_record.status_code != 200:
        print(b1_record.status_code, b1_record.text)
    else:
        uddi_records = b1_record.json()
        return uddi_records


if __name__ == "__main__":
    main()
