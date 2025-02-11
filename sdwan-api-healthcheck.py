#!/usr/bin/env python3

# This library hides sensitive input and replaces it with another character; default *
from pwinput import pwinput

# Cisco SDK for Catlayst SDWAN
from catalystwan.session import create_manager_session
from catalystwan.utils.alarm_status import Severity

# Standard libraries
from pprint import pprint
import urllib3

username = input("Enter your username: ")
password = pwinput("Enter your password: ")

base_url = "https://vmanage-171203704.sdwan.cisco.com/"

# Disable insecure wanring due to self signed cert on SDWAN manager
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Create SDWAN Manager session
session = create_manager_session(url=base_url, username=username, password=password)

# Get Critial alarms that have occurred in the last 5 hours
hours = 5
critical_alarms = session.api.alarms.get(from_time=hours).filter(severity=Severity.CRITICAL)

for alarm in critical_alarms:
    print(alarm)

# Check certificates

certificates = session.api.dashboard.get_certificates_status()
print(f"\n{certificates.data[0]}")

# Check Device Health

devicehealth = session.api.dashboard.get_devices_health_overview()
print(f"\n{devicehealth.data[0]}")

