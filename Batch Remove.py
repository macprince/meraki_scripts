#!/usr/bin/env python3

from meraki import meraki
import json
import argparse
import subprocess
import logging
import os.path
import sys
import re

import csv
import pprint

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
level = logging.INFO
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
myOrgs = meraki.myorgaccess(apikey,suppressprint=True)
orgID = meraki_config['org_id']

networkID = ""

for n in meraki.getnetworklist(apikey,orgID,suppressprint=True):
    if "High School" in n['name']:
        networkID = n['id']

with open("Import.csv") as f:
    reader = csv.DictReader(f)
    data = [r for r in reader]

for d in data:
    old_serial = d['Old Serial']

    meraki.removedevfromnet(apikey,networkID,old_serial,suppressprint=True)
    logging.info(f"{old_serial} removed from network")