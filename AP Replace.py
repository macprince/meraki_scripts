#!/usr/bin/env python3

import json
import argparse
import os.path
import sys

import meraki
import pprint
import gspread

pp = pprint.PrettyPrinter(indent=4)

# Set up argparse
parser = argparse.ArgumentParser()
parser.add_argument("--debug",
                    help="Turns Debug Logging On.",
                    action="store_false")
parser.add_argument("--config",
                    help="Specify path to config.json",
                    default=os.path.join(sys.path[0],"config.json"))
parser.add_argument("--network", 
                    help="Network name as matchable in the Meraki Dashboard",
                    required=True)

args = parser.parse_args()


config = os.path.abspath(args.config)
try:
    with open(config) as config_file:
        settings = json.load(config_file)
except IOError:
    print("No config.json file found! Please create one!")
    sys.exit(2)

# Read in config
meraki_config = settings['meraki_dashboard']

apikey = meraki_config['api_key']
dashboard = meraki.DashboardAPI(api_key=apikey, base_url='https://api.meraki.com/api/v1/', print_console=False, output_log=False)

# Get our organization ID
orgs = dashboard.organizations.getOrganizations()
orgID = next(item for item in orgs if meraki_config['org_name'] in item['name'])['id']

#Use our org ID to get the network in question
networks = dashboard.organizations.getOrganizationNetworks(orgID)
networkid = next(item for item in networks if args.network in item['name'])['id']




# for d in data:

#     old_serial = d['Old Serial']
#     new_serial = d['New Serial']
#     new_asset = d['New Asset']

#     # Retrieve information on old AP
#     old_device = dashboard.devices.getDevice(serial=old_serial)

#     # Claiming new AP by serial
#     dashboard.networks.claimNetworkDevices(networkId=networkid,serials=[new_serial])
#     print(f"{new_serial} added to network")

#     dashboard.devices.updateDevice(serial=new_serial,
#        name=old_device['name'],
#        #tags=old_device['tags'],
#        notes=f"Asset: {new_asset}",
#        lat=old_device['lat'],
#        lng=old_device['lng'],
#        address=old_device['address'],
#        moveMapMarker="true")
#     print(f"{new_serial} set to properties of {old_serial}")

#     old_name = old_device['name']+"-OLD"
#     dashboard.devices.updateDevice(serial=old_serial,name=old_name,suppressprint=True)
#     print(f"{old_serial} renamed to {old_name}")
#     print()
