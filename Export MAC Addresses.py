#!/usr/local/bin/python3

# Standard Imports
import json
import argparse
import os.path
import sys
# Specific Imports
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

days = 14

apikey = meraki_config['api_key']
dashboard = meraki.DashboardAPI(api_key=apikey, base_url='https://api.meraki.com/api/v1/', print_console=False, output_log=False)

orgs = dashboard.organizations.getOrganizations()
orgID = next(o for o in orgs if "Huntley" in o['name'])['id']
networks = dashboard.organizations.getOrganizationNetworks(orgID)
wirelessnetworks = [n for n in networks if 'wireless' in n['productTypes']]

macs=[]

for net in wirelessnetworks:
    print(f"Retrieving clients from network {net['name']}")
    clients = dashboard.networks.getNetworkClients(net['id'], timespan=60*60*24*days, perPage=1000, total_pages='all')
    for c in clients:
        macs.append(c['mac'].replace(":",""))

with open('Meraki.csv',"w") as f:
    writer = csv.writer(f, lineterminator = '\n')
    writer.writerow(["MAC_Address"])
    for mac in sorted(macs):
        writer.writerow([mac])