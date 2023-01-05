#This script follows the SunGard DRX procedure located at:
#\\erieinsurance.com\IT\IT OLD Data\NETSVC\DATA\0: Procedures\Disaster Recovery\2022.03 Spring\0: Pre-DR Network Procedures Runbook SunGard: Spring 2022.doc.
#All steps numbers below are the same as within the document listed above.

import requests
import getpass
from getpass import getpass
from netmiko import ConnectHandler
requests.packages.urllib3.disable_warnings()

#Global variables
Loop = True
ipcorea = "10.200.71.5"
ipcoreb = "10.200.71.7"
headercores = {
    'Content-Type': 'application/yang.data+xml',
    'Accept': 'application/yang.data+xml',
    'Cache-Control': 'no-cache'
}

#Collect Credentials
def getuser():
    user = input("Username: ")
    pwd = getpass("Password: ")
    return user, pwd

#Collect ASR specific credentials
def getuserasr():
    user = input("Username: ")
    pwd = getpass("Password: ")
    secret = getpass("Secret: ")
    return user, pwd, secret

#Main Menu
def main_menu():
    menu = {
        1 : "Step 3: Disable Port eth1/28 on SunG_Core_A & B",
        2 : "Step 3c: Disable VLANs on SunG_Core_A & B",
        3 : "ASR Changes",
        4 : "Step 2a: Enable Port eth1/20 on SunG_Core_B",
        5 : "Exit"
    }
    print("***Please Note: This script requires the use of the current admin enable password due to TACACS being unavailable.***")
    print("Choose an option from the list below:")
    for key in menu.keys():
        print(key, '-', menu[key])
    try:
        choice = int(input("Selection: "))
        menu[choice]
        if choice == 1:
            disabletwentyeight()
            rerun()
        if choice == 2:
            disablevlans()
            rerun()
        if choice == 3:
            asrchanges()
            rerun()
        if choice == 4:
            enableporttwenty()
            rerun()
        if choice == 5:
            end()
    except Exception as e:
        print(e)

#Prompt user to return to Main Menu
def rerun():
    rerun = {
        1 :  "Yes",
        2 :  "No"
    }
    print("\n""Retrun to main menu?")
    for key in rerun.keys():
        print(key, '-', rerun[key])
    try:
        choice = int(input("Selection: "))
        if choice == 1:
            main_menu()
        elif choice == 2:
            end()
    except Exception as e:
        print(e)

#Enable port eth1/20 on SunG_Core_B
def enableporttwenty():
    try:
        user, pwd = getuser()
        url = "https://"+ipcoreb+"/restconf/data/Cisco-NX-OS-device:System/intf-items/phys-items/"
        payload = """<?xml version="1.0" encoding="UTF-8" ?>
            <PhysIf-list>
                <id>eth1/20</id>
                <adminSt>up</adminSt>
            </PhysIf-list>"""
        print("Sending Request..." '\n')
        response = requests.patch(url, headers=headercores, data=payload,auth=(user, pwd),verify=False)

        if response.ok == True:
            print("Command Successful!""\n")
        else:
            print(str(response)+" "+response.text)

    except Exception as ex:
        print(ex)

#ASR Changes
def asrchanges():
    try:
        user, pwd, secret = getuserasr()
        SG_ASR = {
            'device_type': 'cisco_ios',
            'host':   '10.200.60.9',
            'username': user,
            'password': pwd,
            'secret' : secret,             
                }

        post_commands = ['router ospf 2',
                    'redistribute ospf 1 subnets',
                    'redistribute static subnets route-map VPN_to_OSPF',
                    'no redistribute ospf 1 subnets route-map HO_to_DR',
                    'default-information originate',
                    'exit',
                    'ip prefix-list to_HO seq 75 permit 10.200.60.0/24']

        net_connect = ConnectHandler(**SG_ASR)   
        net_connect.enable()
        output = net_connect.send_config_set(post_commands)
        print(output)
    except Exception as ex:
        print(ex)

#Disable port eth1/28 on SunG_Core_A & B
def disabletwentyeight():
    try:
        user,pwd = getuser()
        payload = """<?xml version="1.0" encoding="UTF-8" ?>
            <PhysIf-list>
                <id>eth1/28</id>
                <adminSt>down</adminSt>
            </PhysIf-list>"""

        #Send payload to Core_A
        urla = "https://"+ipcorea+"/restconf/data/Cisco-NX-OS-device:System/intf-items/phys-items/"
        print("Sending Request to SunG_Core_A...")
        responsea = requests.patch(urla, headers=headercores, data=payload,auth=(user, pwd),verify=False)
        if responsea.ok == True:
            print("Core_A Command Successful!")
        else:
            print(str(responsea)+" "+responsea.text)

        #Send Payload to Core_B
        urlb = "https://"+ipcoreb+"/restconf/data/Cisco-NX-OS-device:System/intf-items/phys-items/"
        print("Sending Request to SunG_Core_B...")
        responseb = requests.patch(urlb, headers=headercores, data=payload,auth=(user, pwd),verify=False)
        if responseb.ok == True:
            print("Core_B Command Successful!""\n")
        else:
            print(str(responseb)+" "+responseb.text)
    except Exception as ex:
        print(ex)

#Disable VLANs on both SunG_Core_A & B
def disablevlans():
    try:
        user, pwd = getuser()
        payload = """<?xml version="1.0" encoding="UTF-8" ?>
            <svi-items>
                <If-list>
                    <id>vlan50</id>
                    <adminSt>down</adminSt>
                </If-list>
                <If-list>
                    <id>vlan51</id>
                    <adminSt>down</adminSt>
                </If-list>
                <If-list>
                    <id>vlan52</id>
                    <adminSt>down</adminSt>
                </If-list>
                <If-list>
                    <id>vlan53</id>
                    <adminSt>down</adminSt>
                </If-list>
                <If-list>
                    <id>vlan54</id>
                    <adminSt>down</adminSt>
                </If-list>
                <If-list>
                    <id>vlan57</id>
                    <adminSt>down</adminSt>
                </If-list>
                <If-list>
                    <id>vlan100</id>
                    <adminSt>down</adminSt>
                </If-list>
                <If-list>
                    <id>vlan101</id>
                    <adminSt>down</adminSt>
                </If-list>
                <If-list>
                    <id>vlan102</id>
                    <adminSt>down</adminSt>
                </If-list>
                <If-list>
                    <id>vlan152</id>
                    <adminSt>down</adminSt>
                </If-list>
                <If-list>
                    <id>vlan255</id>
                    <adminSt>down</adminSt>
                </If-list>
                <If-list>
                    <id>vlan700</id>
                    <adminSt>down</adminSt>
                </If-list>
                <If-list>
                    <id>vlan701</id>
                    <adminSt>down</adminSt>
                </If-list>
                <If-list>
                    <id>vlan702</id>
                    <adminSt>down</adminSt>
                </If-list>
                <If-list>
                    <id>vlan703</id>
                    <adminSt>down</adminSt>
                </If-list>
                <If-list>
                    <id>vlan704</id>
                    <adminSt>down</adminSt>
                </If-list>
                <If-list>
                    <id>vlan911</id>
                    <adminSt>down</adminSt>
                </If-list>
                <If-list>
                    <id>vlan1055</id>
                    <adminSt>down</adminSt>
                </If-list>
                <If-list>
                    <id>vlan1102</id>
                    <adminSt>down</adminSt>
                </If-list>
                <If-list>
                    <id>vlan1103</id>
                    <adminSt>down</adminSt>
                </If-list>
                <If-list>
                    <id>vlan1104</id>
                    <adminSt>down</adminSt>
                </If-list>
                <If-list>
                    <id>vlan1105</id>
                    <adminSt>down</adminSt>
                </If-list>
                <If-list>
                    <id>vlan1106</id>
                    <adminSt>down</adminSt>
                </If-list>
                <If-list>
                    <id>vlan1107</id>
                    <adminSt>down</adminSt>
                </If-list>
                <If-list>
                    <id>vlan1521</id>
                    <adminSt>down</adminSt>
                </If-list>
                <If-list>
                    <id>vlan1524</id>
                    <adminSt>down</adminSt>
                </If-list>
                <If-list>
                    <id>vlan2152</id>
                    <adminSt>down</adminSt>
                </If-list>
                <If-list>
                    <id>vlan2369</id>
                    <adminSt>down</adminSt>
                </If-list>
                <If-list>
                    <id>vlan3500</id>
                    <adminSt>down</adminSt>
                </If-list>
                <If-list>
                    <id>vlan3501</id>
                    <adminSt>down</adminSt>
                </If-list>
            </svi-items>"""

        #Send payload to Core_A
        urla = "https://"+ipcorea+"/restconf/data/Cisco-NX-OS-device:System/intf-items/"
        print("Sending Request to SunG_Core_A...")
        responsea = requests.patch(urla, headers=headercores, data=payload,auth=(user, pwd),verify=False)
        if responsea.ok == True:
            print("Core_A Command Successful!")
        else:
            print(str(responsea)+" "+responsea.text)

        #Send payload to Core_B
        urlb = "https://"+ipcoreb+"/restconf/data/Cisco-NX-OS-device:System/intf-items/"
        print("Sending Request to SunG_Core_B...")
        responseb = requests.patch(urlb, headers=headercores, data=payload,auth=(user, pwd),verify=False)
        if responseb.ok == True:
            print("Core_B Command Successful!""\n")
        else:
            print(str(responseb)+" "+responseb.text)

    except Exception as ex:
        print(ex)

#End the application
def end():
    print("Thank-you for using this application!")
    input("Press enter to close.")
    quit()

#Loop to keep Main Menu open
print("Welcome!")
while Loop == True:
    main_menu()
