# Overview
Collection of scripts for interfacing with [Infoblox](https://docs.infoblox.com/space/BloxOneDDI/684523986/Universal+DDI+Overview) UDDI platform

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)


## Installation
The following python packages will be required to run these tools:
- [bloxone](https://github.com/ccmarris/python-bloxone)
- [click](https://click.palletsprojects.com/en/stable/)
- [click-option-group](https://click-option-group.readthedocs.io/en/latest/)
- [prettytable](https://github.com/prettytable/prettytable)
- [rich](https://github.com/Textualize/rich)
```
pip3 install -r requirements.txt
```

## Scripts
| Framework | Description |
| --- | --- |
| b1ddi-framework.py | Basic UDDI Script to connect and get an object |

| B1TDC Tools | Description |
| ---- | ---- |
| b1td-named-list.py | Add, Update, Delete B1TDC Named Lists |
| b1tdc.py | Get B1TDC Objects and display them on screen |

| B1DDI Tools (DNS) | Description |
| ---- | ---- |
| b1ddi-dns-profile.py | Get, Add, Delete B1DDI Global DNS Profiles |
| b1ddi-dns-namedacl.py | 
| b1ddi-dns-record.py | Get, B1DDI DNS Records |
| b1ddi-dns-recordlookup.py | None |
| b1ddi-dns-nsg.py | Get, Add, Delete B1DDI Auth NSG |
| b1ddi-dns-view.py | Get, Add, Delete B1DDI DNS Views |
| b1ddi-dns-authzone.py | Get, Add B1DDI Auth Zones|

| B1DDI Tools (DHCP) | Description |
| ---- | ---- |
| b1ddi-dhcp-ha.py | Get, Add, Delete B1DDI DHCP HA Groups |
| b1ddi-dhcp-ipspace.py | Get, Add, Delete B1DDI IP Space |
| b1ddi-dhcp-profile.py | Get, Add, Delete B1DDI Global DHCP Profiles |
| b1ddi-dhcp-options.py | Get, Add DHCP Options |
| b1ddi-dhcp-option-filters.py | Get, Add DHCP Options Filters |
| b1ddi-dhcp-network-service-instance.py | Get,Update Subnet/Range Service Assignment |
| b1ddi-dhcp-network-name.py | Update B1DDI Network Name | 
| b1ddi-dhcp-fixedaddress.py | B1DDI Fixed addresses |
| b1ddi-dhcp-ddns.py | Get, Add to DDNS configuration |

| UDDI Platform | Description |
| --- | --- |
| b1ddi-users.py | Get, B1DDI tenant users |
| b1ztp-join-token.py | Get, Add, Delete B1DDI Join Tokens |
| b1infra-host-services.py | Get, Add, Update Host / Service Assignment and Start / Stop Services |

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
