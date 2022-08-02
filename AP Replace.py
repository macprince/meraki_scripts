#!/usr/bin/env python3

import json
import argparse
import logging
import os.path
import sys

import meraki
import csv
import pprint

pp = pprint.PrettyPrinter(indent=4)

# Set up argparse
parser = argparse.ArgumentParser()
parser.add_argument("--debug",
                    help="Turns Debug Logging On.",
                    action="store_true")
parser.add_argument("--config",
                    help="Specify path to config.json",
                    default=os.path.join(sys.path[0],"config.json"))
parser.add_argument("--network", 
                    help="Network name as matchable in the Meraki Dashboard",
                    required=True)
parser.add_argument("--csv",
                    help="CSV file of access points to import as replacements",
                    required=True)

args = parser.parse_args()

# Set up logging
level = logging.WARNING
if args.debug:
    level = logging.DEBUG
logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %I:%M:%S %p',
                    level=level,
                    filename=os.path.join(sys.path[0],'meraki_batch_replace.log'))
stdout_logging = logging.StreamHandler()
stdout_logging.setFormatter(logging.Formatter())
logging.getLogger().addHandler(stdout_logging)

config = os.path.abspath(args.config)
try:
    with open(config) as config_file:
        settings = json.load(config_file)
except IOError:
    logging.error("No config.json file found! Please create one!")
    sys.exit(2)

# Read in config
meraki_config = settings['meraki_dashboard']

apikey = meraki_config['api_key']
dashboard = meraki.DashboardAPI(api_key=apikey, base_url='https://api.meraki.com/api/v1/', log_file_prefix=__file__[:-3], print_console=False)

# Get our organization ID
orgs = dashboard.organizations.getOrganizations()
orgID = next(item for item in orgs if "Huntley" in item['name'])['id']

#Use our org ID to get the network in question
networks = dashboard.organizations.getOrganizationNetworks(orgID)
networkid = next(item for item in networks if args.network in item['name'])['id']

with open(args.csv) as f:
    reader = csv.DictReader(f)
    data = [r for r in reader]

for d in data:

    old_serial = d['Old Serial']
    new_serial = d['New Serial']
    new_asset = d['New Asset']

    # Retrieve information on old AP
    old_device = dashboard.devices.getDevice(serial=old_serial)

    # Claiming new AP by serial
    dashboard.networks.claimNetworkDevices(networkId=networkid,serials=[new_serial])
    print(f"{new_serial} added to network")

    dashboard.devices.updateDevice(serial=new_serial,
       name=old_device['name'],
       #tags=old_device['tags'],
       notes=f"Asset: {new_asset}",
       lat=old_device['lat'],
       lng=old_device['lng'],
       address=old_device['address'],
       moveMapMarker="true")
    print(f"{new_serial} set to properties of {old_serial}")

    old_name = old_device['name']+"-OLD"
    dashboard.devices.updateDevice(serial=old_serial,name=old_name,suppressprint=True)
    print(f"{old_serial} renamed to {old_name}")
    print()
