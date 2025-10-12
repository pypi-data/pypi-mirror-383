#!/usr/bin/env python3

# TODO
# Change PrettyTable for RichTables
# Fix file functions to resolve possibly unbound errors
# Rewrite file section to use functions
# Resolve password undefined in mail function
# assign type in main()
import csv
import bloxone
from prettytable import PrettyTable
import click
from click_option_group import optgroup
import smtplib
import ssl


@click.command()
@optgroup.group("Required Options")
@optgroup.option(
    "--config", type=str, default="b1config.ini", help="B1DDI Configuration INI file"
)
@optgroup.group("Batch Operations")
@optgroup.option(
    "-f", "--file", type=str, help="CSV file containing data for processing"
)
@optgroup.group("B1TD NamedList Actions")
@optgroup.option(
    "-l",
    "--listnl",
    is_flag=True,
    help="Use this method to retrieve information on all Named List objects for the account. Note that list items are not returned for this operation",
)
@optgroup.option(
    "-c",
    "--create",
    is_flag=True,
    help="Use this method to create a Named List object.",
)
@optgroup.option(
    "-d",
    "--delete",
    is_flag=True,
    help="Use this method to delete Named List objects. Deletion of multiple lists is an all-or-nothing operation (if any of the specified lists can not be deleted then none of the specified lists will be deleted).",
)
@optgroup.option(
    "-p",
    "--patch",
    is_flag=True,
    help="Use this method to insert items for multiple Named List objects. Note that duplicated items correspondig to named list are silently skipped and only new items are appended to the named list. Note that DNSM, TI, Fast Flux and DGA lists cannot be updated. Only named lists of Custom List type can be updated by this operation. If one or more of the list ids is invalid, or the list is of invalid type then the entire operation will be failed.  The Custom List Items represent the list of the FQDN or IPv4 addresses to define whitelists and blacklists for additional protection.",
)
@optgroup.group("B1TD NamedList Fields")
@optgroup.option(
    "-n", "--name", type=str, help="The identifier for a Named List object."
)
@optgroup.option(
    "-i", "--item", type=str, help="Add the item in the custom list using this field."
)
@optgroup.option(
    "--comment",
    help="Add the description/comments to each item in the custom list using this field.",
)
@optgroup.option(
    "--confidence",
    default="HIGH",
    type=click.Choice(["LOW", "MEDIUM", "HIGH"]),
    help="Confidence level of item",
)
@optgroup.group("Email Options")
@optgroup.option(
    "--mail", type=bool, default=False, help="Mail output to designated people"
)
@optgroup.option("--sender", multiple=True, help="SMTP Sender")
@optgroup.option("-r", "--receipients", multiple=True, help="SMTP Receipients")
@optgroup.option(
    "--subject",
    default="Infoblox: Bloxone Threat Defense Cloud Update",
    help="SMTP Subject",
)
@optgroup.option("-s", "--server", help="SMTP Server")
def main(
    config,
    file,
    listnl,
    create,
    delete,
    patch,
    name,
    comment,
    item,
    confidence,
    mail,
    sender,
    receipients,
    subject,
    server,
):
    # Consume b1ddi ini file for login
    b1tdc = bloxone.b1tdc(config)
    # Uncomment if needed
    # print("API Key: {}".format(b1tdc.api_key))
    # print("API Version: {}".format(b1tdc.api_version))

    if listnl:
        if name:
            try:
                response = b1tdc.get_custom_list(name)
                named_list(response)
            except Exception as e:
                print(e)
        else:
            try:
                response = b1tdc.get_custom_lists()
                get_named_list(response)
            except Exception as e:
                print(e)

    if create:
        try:
            response = b1tdc.create_custom_list(
                name,
                confidence,
                items_described=[{"description": comment, "item": item}],
            )
            named_list(response)
        except Exception as e:
            print(e)

    if delete:
        if item and comment:
            try:
                response = b1tdc.delete_items_from_custom_list(
                    name, items_described=[{"description": comment, "item": item}]
                )
                if response.status_code == 204:
                    print("{} deleted from {}".format(item, name))
                    response = b1tdc.get_custom_list(name)
                    named_list(response)
                else:
                    print(response.status_code, response.text)
            except Exception as e:
                print(e)
        elif name:
            try:
                response = b1tdc.delete_custom_lists(names=[name])
                if response.status_code == 204:
                    print("{} list deleted".format(name))
                else:
                    print(response.status_code, response.text)
            except Exception as e:
                print(e)
        else:
            print("Invalid Flags Specified")

    if patch:
        try:
            response = b1tdc.add_items_to_custom_list(
                name, items_described=[{"description": comment, "item": item}]
            )
            if response.status_code == 201:
                print("{} update successful".format(name))
                response = b1tdc.get_custom_list(name)
                named_list(response)
            else:
                print(response.status_code, response.text)
        except Exception as e:
            print(e)

    if file:
        if mail:
            automated_report = []
        with open(file, newline="") as csvfile:
            b1tdcfile = csv.reader(csvfile, delimiter=",")
            for row in b1tdcfile:
                if row[0] == "create":
                    response = b1tdc.create_custom_list(
                        row[1],
                        confidence,
                        items_described=[{"description": row[2], "item": row[3]}],
                    )
                elif row[0] == "update":
                    response = b1tdc.add_items_to_custom_list(
                        row[1],
                        items_described=[{"description": row[2], "item": row[3]}],
                    )
                elif row[0] == "deleteitem":
                    response = b1tdc.delete_items_from_custom_list(
                        row[1],
                        items_described=[{"description": row[2], "item": row[3]}],
                    )
                elif row[0] == "delete":
                    response = b1tdc.delete_custom_lists(names=[row[1]])
                else:
                    print("Undefined Action")

                if (
                    response.status_code == 200
                    or response.status_code == 201
                    or response.status_code == 204
                ):
                    if len(row) == 2:
                        print("{} {} Successful".format(row[0], row[1]))
                    else:
                        print(
                            "{} {} Successful : {} {} ".format(
                                row[1], row[0], row[3], row[2]
                            )
                        )
                        if mail:
                            automated_report.append(
                                "{row[1]} {row[0]} Successful : {row[3]} {row[2]}"
                            )
                else:
                    print(response.status_code, response.text)
                    if mail:
                        automated_report.append(
                            "{response.status_code} {response.text}"
                        )
                if mail:
                    send_mail_report(
                        server, sender, receipients, subject, automated_report
                    )


def get_named_list(response):
    table = PrettyTable()
    table.field_names = [
        "Confidence Level",
        "Creation Time",
        "Description",
        "ID",
        "Item Count",
        "Name",
        "Policies",
        "Tags",
        "Threat Level",
        "Type",
        "Last Updated",
    ]
    if response.status_code == 200:
        b1tdc_list = response.json()
        for nl in b1tdc_list["results"]:
            table.add_row(
                [
                    *[
                        str(nl[key])
                        for key in [
                            "confidence_level",
                            "created_time",
                            "description",
                            "id",
                            "item_count",
                            "name",
                            "policies",
                            "tags",
                            "threat_level",
                            "type",
                            "updated_time",
                        ]
                    ]
                ]
            )
    else:
        print(response.status_code, response.text)
    print(table)


def named_list(response):
    table = PrettyTable()
    table.field_names = [
        "Confidence Level",
        "Creation Time",
        "Description",
        "ID",
        "Item Count",
        "Items",
        "Items Description",
        "Name",
        "Policies",
        "Tags",
        "Threat Level",
        "Type",
        "Last Updated",
    ]
    if response.status_code == 200 or response.status_code == 201:
        b1tdc_named_list = response.json()
        for nl in b1tdc_named_list["results"]["items_described"]:
            table.add_row(
                [
                    b1tdc_named_list["results"]["confidence_level"],
                    b1tdc_named_list["results"]["created_time"],
                    b1tdc_named_list["results"]["description"],
                    b1tdc_named_list["results"]["id"],
                    b1tdc_named_list["results"]["item_count"],
                    nl["item"],
                    nl["description"],
                    b1tdc_named_list["results"]["name"],
                    b1tdc_named_list["results"]["policies"],
                    b1tdc_named_list["results"]["tags"],
                    b1tdc_named_list["results"]["threat_level"],
                    b1tdc_named_list["results"]["type"],
                    b1tdc_named_list["results"]["updated_time"],
                ]
            )
        print(table)
    else:
        print(response.status_code, response.text)


def send_mail_report(server, sender, receipients, subject, automated_report):
    smtp_server = server
    sender_email = sender
    receiver_email = ",".join(receipients)
    message = "Subject: {} \nNamed List Updates \n{}".format(subject, automated_report)

    ssl_context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.ehlo()  # Can be omitted
        if server.has_extn("starttls"):
            server.starttls(context=ssl_context)
            server.login(sender_email, password)
        else:
            server.login(sender_email, password)
        try:
            server.sendmail(sender_email, receiver_email, message)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()
