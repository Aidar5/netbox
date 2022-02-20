# netbox

# Algoritm:
- The script downloads all devices from Netbox
- Creates a list of dictionaries of only those devices that match the given parameters (status and tenant)
- Script connects to devices from the list; sends the show command; receives a response; filters the output based on regex to get the SW version on the device.
- The result of the regex is stored in a dictionary with the corresponding device id on the Netbox.
- Script updates the value of custom_fiels:sw_version on Netbox for each id in the dictionary. 

# Task requirements:
- Collect information for devices with Status = Active, Tenant = NOC in Netbox - **DONE**
- Information to collect: software version - **DONE**
- Custom field to update: "sw_version" - **DONE**
- Devices: Cisco Catalyst IOS, Cisco Nexus OS, Cisco ASA OS, Aruba OS, PaloAlto PAN-OS (more device types covered more points) + **JUNOS** - **DONE**
- Should contain unit tests – pytest should be used - **DONE**
- Should pass pylint and black (optional) - **DONE**

# Comments
Script implies that:
- All devices have the same credentials to login via SSH.
- Device username priveledge level allows login directly to enable mode (like bypassing EXEC mode in Cisco)
- Device "tag" field in Netbox contains Netmiko "device_type" value.

Netmiko was chosen because it is simple and supports all devices from requirements.
User is promted to enter Status and Tenant. This approach provides flexibility in choosing other values, not only 'Active': 'NOC'.
Multithreading is used for faster collecting of information from devices. It becomes benefitial if there are hundreds or thousands devices need to be polled.
Try/except helps to avoid breaking of script run in case if some devices are not reachable or access is denied. Also, in case of exception the script informs which device has an issue.
