#!/usr/bin/env python3

import json
import argparse
import os.path
import sys

import meraki
import pprint
import gspread
from gspread_formatting import *

pp = pprint.PrettyPrinter(indent=4)

# Set up argparse
parser = argparse.ArgumentParser()
parser.add_argument("mode",
                    help="_export_ AP data to Sheets, _replace_ APs in Meraki, or _remove_ old APs",
                    default="export")
parser.add_argument("--debug",
                    help="Turns Debug Logging On.",
                    action="store_false")
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
sheets_config = settings['sheets']

apikey = meraki_config['api_key']
dashboard = meraki.DashboardAPI(api_key=apikey, base_url='https://api.meraki.com/api/v1/', print_console=False, output_log=False)

# Get our organization ID
orgs = dashboard.organizations.getOrganizations()
orgID = orgs[0]['id'] # I used to specifically select the org with the correct name, but we haven't had multiple orgs in a while, so I'm lazy
# orgID = next(item for item in orgs if meraki_config['org_name'] in item['name'])['id']

networks = dashboard.organizations.getOrganizationNetworks(orgID)
networks = sorted(networks,key=lambda x: x['name'])

gc = gspread.service_account()
wb = gc.open_by_key(sheets_config['spreadsheet_id'])
sheets = wb.worksheets()
sheet_titles = [sheet.title for sheet in sheets]

match args.mode:
    case "export": 
        for net in networks:
            if net['name'] not in sheet_titles:
                ws = wb.add_worksheet(
                title=net['name'],
                rows=300,
                cols=4
                )
            else:
                ws = wb.worksheet(net['name'])
                ws.clear()

            ws.batch_format([
        {"range": "A1:D1", "format": {"textFormat": {"bold": True}}},
        {"range": "C2:E", "format": {"textFormat": {"fontFamily": "Courier New"}}},
    ])

            set_column_widths(ws,[ ('A', 160), ('B', 75),('C', 120),('D', 120) ])
            set_frozen(ws,rows=1)

            dash_aps = dashboard.organizations.getOrganizationDevices(
                organizationId=orgID,
                networkIds=[net['id']],
                productTypes=["wireless"],
                perPage=1000,
                total_pages='all'
                )
            dash_aps = sorted(dash_aps,key=lambda x: x['name'])
            
            output_aps = []
            output_aps.append(["Name","Old Model","Old Serial","New Serial","New Asset"])
            for ap in dash_aps:
                output_aps.append([ap['name'],ap['model'],ap['serial'],"",""])

            ws.update(output_aps,"A1:E")

    case "replace":
        print("Replace detected")
        sheet_titles = [s for s in sheet_titles if "Sheet" not in s]
    case "remove":
        print("Remove detected")
    case _:
        print("Mode not found, exiting.")
        sys.exit(1)




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
