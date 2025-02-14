#!/usr/bin/env python3

# This script performs a speedtest

# This library hides sensitive input and replaces it with another character; default *
from pwinput import pwinput

# Cisco SDK for Catlayst SDWAN
from catalystwan.session import create_manager_session
from catalystwan.utils.alarm_status import Severity
from catalystwan.utils.personality import Personality
from catalystwan.utils.dashboard import HealthColor


# Standard libraries
from pprint import pprint
import urllib3

username = input("Enter your username: ")
password = pwinput("Enter your password: ")

base_url = "https://vmanage-171203704.sdwan.cisco.com/"

# Disable insecure wanring due to self signed cert on SDWAN manager
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print(f"Connecting to vManage...\n")

# Create SDWAN Manager session
try:
    session = create_manager_session(url=base_url, username=username, password=password)
except ManagerHTTPError as error:
    # Error processing
    print(error.response.status_code)
    print(error.info.code)
    print(error.info.message)
    print(error.info.details)

# Get Critial alarms that have occurred in the last 6 hours
hours = 6
try:
    critical_alarms = session.api.alarms.get(from_time=hours).filter(severity=Severity.CRITICAL)
except ManagerHTTPError as error:
    # Error processing
    print(error.response.status_code)
    print(error.info.code)
    print(error.info.message)
    print(error.info.details)

for alarm in critical_alarms:
    print(alarm)

# Get devices

print(f"Retrieving list of devices...\n")

devices = session.api.devices.get()

print("\nController status:\n")

# Report vManage status

vmanage = devices.filter(personality=Personality.VMANAGE)[0]

print(f"Hostname:       {vmanage.hostname}")
print(f"Reachability:   {str(vmanage.reachability).split('.')[1]}")
print(f"Status:         {vmanage.status}\n")

# Report vSmart Status

vsmarts = devices.filter(personality=Personality.VSMART)

for vsmart in vsmarts:
    print(f"Hostname:       {vsmart.hostname}")
    print(f"Reachability:   {str(vsmart.reachability).split('.')[1]}")
    print(f"Status:         {vsmart.status}\n")

# Report vBond Status

vbonds = devices.filter(personality=Personality.VBOND)

for vbond in vbonds:
    print(f"Hostname:       {vbond.hostname}")
    print(f"Reachability:   {str(vbond.reachability).split('.')[1]}")
    print(f"Status:         {vbond.status}\n")

# Report on controller certificates

try:
    certificates = session.api.dashboard.get_certificates_status()
except ManagerHTTPError as error:
    # Error processing
    print(error.response.status_code)
    print(error.info.code)
    print(error.info.message)
    print(error.info.details)

print(f"\n{certificates.data[0]}")

# Report Device Health Overview

try:
    devicehealthoverview = session.api.dashboard.get_devices_health_overview()
except ManagerHTTPError as error:
    # Error processing
    print(error.response.status_code)
    print(error.info.code)
    print(error.info.message)
    print(error.info.details)

print(f"\n{devicehealthoverview.data[0]}")

# Report on device in "Yellow" health state

devhealth=session.api.dashboard.get_devices_health()
yellow_devs = devhealth.devices.filter(health=HealthColor.YELLOW)

print("\nDevices in yellow state:")

for device in yellow_devs:
    print(f"\n{device.system_ip:<20}{device.name}")
    
    device_overview = devices.filter(local_system_ip=device.system_ip)

    if device_overview[0].cpu_state != "normal":
        print(f"CPU state: {device_overview[0].cpu_state}")
    if device_overview[0].mem_state != "normal":
        print(f"Memory state: {device_overview[0].mem_state}")
    

    if device.control_connections != device.control_connections_up:
        print(f"Control connections up/expected: {device.control_connections_up}/{device.control_connections}")
    if device.vsmart_control_connections != device.expected_vsmart_connections:
        print(f"vSmart connections up/expected: {device.vsmart_control_connections}/{device.expected_vsmart_connections}")
    if device.personality == Personality.VMANAGE:
        continue
    if device.bfd_sessions != device.bfd_sessions_up:
        print(f"BFD Sessions up/expected: {device.bfd_sessions_up}/{device.bfd_sessions}")
    if device.omp_peers != device.omp_peers_up:
        print(f"OMP Peers up/expected: {device.omp_peers_up}/{device.omp_peers}")

# Report unreachable edges

routers = devices.filter(personality=Personality.EDGE)

print("\nRouters offline/down:\n")
for router in routers:
    if not router.is_reachable:
        print(f"{router.local_system_ip:<20}{router.hostname}")

n2r2 = devices.find()