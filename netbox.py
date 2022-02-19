""" Modules import """
import re
import getpass
from concurrent.futures import ThreadPoolExecutor
from netmiko import ConnectHandler
import pynetbox

# Get values from user
netbox_token = getpass.getpass("Please enter Netbox token: ")
device_user = input("Please enter device username: ")
device_paswd = getpass.getpass("Please enter device password: ")
status_name = input("Please enter device status: ")
tenant_name = input("Please enter tenant name: ")

# Commands assotiated with Netmiko device type
type_to_command = {
    "cisco_ios": "show version",
    "cisco_nxos": "show version",
    "cisco_asa": "show version",
    "aruba_os": "show version",
    "paloalto_panos": "show system info",
    "juniper_junos": "show version",
}


# Regex to match SW version number
regex_dict = {
    "cisco_ios": r"Cisco.*Version\s(\S+),.*",
    "cisco_nxos": r"NXOS: version\s(\S+)",
    "cisco_asa": r"Cisco Adaptive Security Appliance Software Version\s(\S+)",
    "aruba_os": r"ArubaOS.*Version\s(\S+)",
    "paloalto_panos": r"sw-version:\s(\S+)",
    "juniper_junos": r"^Junos:\s(\S+)",
}


# Describe functions
def show_version(dev_type, dev_ip, dev_id, command, regex):
    """Function connects to device, send command,
    parse output through regex to retrive SW version
    and return a tuple with device id and corresponding version"""

    device_param = {
        "device_type": dev_type,
        "host": dev_ip,
        "username": device_user,
        "password": device_paswd,
    }

    ssh = ConnectHandler(**device_param)
    output = ssh.send_command(command)
    for line in output.split("\n"):
        if re.search(regex, line):
            match = re.search(regex, line).group(1)
            break

    return dev_id, match


def test_active():
    """Test function to check 'active' dictionary"""
    assert bool(active) is True, "Object should not be empty"
    assert all(tag for tag in active), "Tags should not contain None or empty value"
    assert all(
        all(each) for each in active.values()
    ), "ID and IP should not contain None or empty value"


def test_version_list():
    """Test function to check 'version_list' list"""
    assert all(
        all(each) for each in version_list
    ), "ID and Match should not contain None or empty value"


# Connection to Netbox
nb = pynetbox.api("http://localhost:8000", token=netbox_token)

# Retrive list of all devices from Netbox
device_list = list(nb.dcim.devices.all())

# Loop through list of devices, filter devices based on Status and Tenant.
# Generate dictionary for each mathced device: {tag: [ip, id]}
# Tag value represents Netmiko device type.
active = {}
for d in device_list:
    if str(d.status) == status_name and str(d.tenant) == tenant_name:
        active[str(d.tags[0])] = [
            str(d.primary_ip).split("/", maxsplit=1)[0],
            str(d.id),
        ]

# Use of multitheading to concurrently connect to each device from 'active' dict.
# Generate list of function results
version_list = []
with ThreadPoolExecutor(max_workers=6) as executor:
    future_list = []
    for device in active:
        future = executor.submit(
            show_version,
            device,
            active[device][0],
            active[device][1],
            type_to_command[device],
            regex_dict[device],
        )
        future_list.append(future)
    for f in future_list:
        version_list.append(f.result())

# Update SW version on Netbox for each resulting device
# Pytest is not checking this part,
# therefore only direct script run (python cmd) will execute this block of code.
if __name__ == "__main__":
    for version in version_list:
        device_id, device_sw = version
        update_device = nb.dcim.devices.get(id=device_id)
        update_device.update(
            {"id": device_id, "custom_fields": {"sw_version": device_sw}}
        )
