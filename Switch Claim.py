#!/usr/bin/env python3

import meraki
import json
import argparse
import subprocess
import logging
import os.path
import sys
import re

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
orgID = meraki_config['org_id']
dashboard = meraki.DashboardAPI(api_key=apikey, base_url='https://api.meraki.com/api/v0/', log_file_prefix=__file__[:-3], print_console=False)

networks = dashboard.networks.getOrganizationNetworks(orgID)
networkid = next(item for item in networks if "Marlowe" in item['name'])['id']

with open("Switches.csv") as f:
    reader = csv.DictReader(f)
    data = [r for r in reader]

for d in data:

    serial = d['Serial Number']

    # Claiming new switch by serial
    dashboard.devices.claimNetworkDevices(networkId=networkid,serials=[serial])
    print(f"{serial} added to network")

    # Set properties of switch
    dashboard.devices.updateNetworkDevice(networkId=networkid,serial=serial,
        name=d['Switch Name'],
        notes=f"Asset: {d['Asset Tag']}"
        )
    print(f"{serial} set to {d['Switch Name']} ({d['Asset Tag']})")
    print()
    


        
    
