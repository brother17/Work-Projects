#This script follows the SunGard DRX procedure located at:
#\\erieinsurance.com\IT\IT OLD Data\NETSVC\DATA\0: Procedures\Disaster Recovery\2022.03 Spring\0: Pre-DR Network Procedures Runbook SunGard: Spring 2022.doc.
#All steps numbers below are the same as within the document listed above.

import requests
import getpass
import os
from getpass import getpass
from netmiko import ConnectHandler
requests.packages.urllib3.disable_warnings()

#Global Variables
Loop = True
ipcorea = "10.200.71.5"
ipcoreb = "10.200.71.7"
headercores = {
    'Content-Type': 'application/yang.data+xml',
    'Accept': 'application/yang.data+xml',
    'Cache-Control': 'no-cache'
}

#Colelct credentials
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
        1 : "Step 2a: Disable Port eth1/20 on SunG_Core_B",
        2 : "ASR Changes",
        3 : "Step 3: Enable Port eth1/28 on SunG_Core_A & B",
        4 : "Step 3c: Enable VLANs on SunG_Core_A & B",
        5 : "Open Validation Script",
        6 : "Exit"
    }
    print("Choose an option from the list below:")
    for key in menu.keys():
        print(key, '-', menu[key])
    try:
        choice = int(input("Selection: "))
        print("\n")
        menu[choice]
        if choice == 1:
            disableporttwenty()
            rerun()
        if choice == 2:
            asrchanges()
            rerun()
        if choice == 3:
            enabletwentyeight()
            rerun()
        if choice == 4:
            enablevlans()
            rerun()
        if choice == 5:
            openvalidate()
        if choice == 6:
            end()
    except Exception as e:
        print(e)

#Prompt user to return to Main Menu
def rerun():
    rerun = {
        1 :  "Yes",
        2 :  "No"
    }
    print("\n""Return to Main Menu?: ")
    for key in rerun.keys():
        print(key, '-', rerun[key])
    try:
        choice = int(input("Selection: "))
        print("\n")
        if choice == 1:
            main_menu()
        elif choice == 2:
            end()
    except (ValueError, KeyError, TypeError):
        print("Invalid option.")

#Prompt to open validation script
def openvalidate():
    try:
        dir = os.path.dirname(os.path.realpath(__file__))
        print("\n""Current Directory: "+str(dir))
        print("Files in directory:")
        filelist = {}
        key=0
        for item in os.scandir(dir):
            if item.is_file():
                name = item.name
                key += 1
                newitem = {key:name}
                filelist.update(newitem)
        for key in filelist.keys():
            print(filelist[key])
        print("\n")
        with os.scandir(dir) as validate:
            for entry in validate:
                if entry.name.startswith('SunGard_DRX_Validate'):
                    script = entry.name
                    answer = input("Open "+script+"? (y/n): ")
                    if answer == "y":
                        os.startfile(dir+"\\"+script)
                    if answer == "n":
                        print("\n")
    
    except Exception as ex:
        print(ex)

#Disagble port eth1/20 on SunG_Core_B
def disableporttwenty():
    try:
        user, pwd = getuser()
        url = "https://"+ipcoreb+"/restconf/data/Cisco-NX-OS-device:System/intf-items/phys-items/"
        payload = """<?xml version="1.0" encoding="UTF-8" ?>
            <PhysIf-list>
                <id>eth1/20</id>
                <adminSt>down</adminSt>
            </PhysIf-list>"""
        print("Sending Request..." '\n')
        response = requests.patch(url,headers=headercores, data=payload,auth=(user, pwd),verify=False)

        if response.ok == True:
            print("Command Successful!")
            print(str.center(" Milestone 1 Reached ",60,"#"))
            print(str.center(" Non-Replication Traffic to HO Cut Off ",60,"#"),"\n")
        else:
            print(str(response)+" - "+response.text)

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

        pre_commands = ['router ospf 2',
                    'no redistribute ospf 1',
                    'no redistribute static',
                    'redistribute ospf 1 subnets route-map HO_to_DR',
                    'no default-information originate',
                    'exit',
                    'no ip prefix-list to_HO seq 75 permit 10.200.60.0/24']

        net_connect = ConnectHandler(**SG_ASR)   
        net_connect.enable()
        output = net_connect.send_config_set(pre_commands)
        print(output)
    
    except Exception as ex:
        print(ex)

#Enable port eth1/28 on SunG_Core_A & B
def enabletwentyeight():
    try:
        user,pwd = getuser()
        payload = """<?xml version="1.0" encoding="UTF-8" ?>
            <PhysIf-list>
                <id>eth1/28</id>
                <adminSt>up</adminSt>
            </PhysIf-list>"""
        
        #Send payload to Core_A
        urla = "https://"+ipcorea+"/restconf/data/Cisco-NX-OS-device:System/intf-items/phys-items/"
        print("Sending Request to SunG_Core_A..." '\n')
        responsea = requests.patch(urla, headers=headercores, data=payload,auth=(user, pwd),verify=False)

        if responsea.ok == True:
            print("Core_A Command Successful!")
        else:
            print(str(responsea)+" - "+responsea.text)

        #Send Payload to Core_B
        urlb = "Https://"+ipcoreb+"/restconf/data/Cisco-NX-OS-device:System/intf-items/phys-items/"
        print("Sending Request to SunG_Core_B..." '\n')
        responseb = requests.patch(urlb, headers=headercores, data=payload,auth=(user, pwd),verify=False)

        if responseb.ok == True:
            print("Core_B Command Successful!""\n")
        else:
            print(str(responseb)+" - "+responseb.text)

    except Exception as ex:
        print(ex)

#Enable VLANs on both SunG_Core_A & B
def enablevlans():
    try:
        user, pwd = getuser()
        payload = """<?xml version="1.0" encoding="UTF-8" ?>
            <svi-items>
                <If-list>
                    <id>vlan50</id>
                    <adminSt>up</adminSt>
                </If-list>
                <If-list>
                    <id>vlan51</id>
                    <adminSt>up</adminSt>
                </If-list>
                <If-list>
                    <id>vlan52</id>
                    <adminSt>up</adminSt>
                </If-list>
                <If-list>
                    <id>vlan53</id>
                    <adminSt>up</adminSt>
                </If-list>
                <If-list>
                    <id>vlan54</id>
                    <adminSt>up</adminSt>
                </If-list>
                <If-list>
                    <id>vlan57</id>
                    <adminSt>up</adminSt>
                </If-list>
                <If-list>
                    <id>vlan100</id>
                    <adminSt>up</adminSt>
                </If-list>
                <If-list>
                    <id>vlan101</id>
                    <adminSt>up</adminSt>
                </If-list>
                <If-list>
                    <id>vlan102</id>
                    <adminSt>up</adminSt>
                </If-list>
                <If-list>
                    <id>vlan152</id>
                    <adminSt>up</adminSt>
                </If-list>
                <If-list>
                    <id>vlan255</id>
                    <adminSt>up</adminSt>
                </If-list>
                <If-list>
                    <id>vlan700</id>
                    <adminSt>up</adminSt>
                </If-list>
                <If-list>
                    <id>vlan701</id>
                    <adminSt>up</adminSt>
                </If-list>
                <If-list>
                    <id>vlan702</id>
                    <adminSt>up</adminSt>
                </If-list>
                <If-list>
                    <id>vlan703</id>
                    <adminSt>up</adminSt>
                </If-list>
                <If-list>
                    <id>vlan704</id>
                    <adminSt>up</adminSt>
                </If-list>
                <If-list>
                    <id>vlan911</id>
                    <adminSt>up</adminSt>
                </If-list>
                <If-list>
                    <id>vlan1055</id>
                    <adminSt>up</adminSt>
                </If-list>
                <If-list>
                    <id>vlan1102</id>
                    <adminSt>up</adminSt>
                </If-list>
                <If-list>
                    <id>vlan1103</id>
                    <adminSt>up</adminSt>
                </If-list>
                <If-list>
                    <id>vlan1104</id>
                    <adminSt>up</adminSt>
                </If-list>
                <If-list>
                    <id>vlan1105</id>
                    <adminSt>up</adminSt>
                </If-list>
                <If-list>
                    <id>vlan1106</id>
                    <adminSt>up</adminSt>
                </If-list>
                <If-list>
                    <id>vlan1107</id>
                    <adminSt>up</adminSt>
                </If-list>
                <If-list>
                    <id>vlan1521</id>
                    <adminSt>up</adminSt>
                </If-list>
                <If-list>
                    <id>vlan1524</id>
                    <adminSt>up</adminSt>
                </If-list>
                <If-list>
                    <id>vlan2152</id>
                    <adminSt>up</adminSt>
                </If-list>
                <If-list>
                    <id>vlan2369</id>
                    <adminSt>up</adminSt>
                </If-list>
                <If-list>
                    <id>vlan3500</id>
                    <adminSt>up</adminSt>
                </If-list>
                <If-list>
                    <id>vlan3501</id>
                    <adminSt>up</adminSt>
                </If-list>
            </svi-items>"""
        #Send payload to Core_A
        urla = "https://"+ipcorea+"/restconf/data/Cisco-NX-OS-device:System/intf-items/"
        responsea = requests.patch(urla, headers=headercores, data=payload,auth=(user, pwd),verify=False)

        if responsea.ok == True:
            print("Core_A Command Successful!")
        else:
            print(str(responsea)+" - "+responsea.text)

        #Send payload to Core_B
        urlb = "https://"+ipcoreb+"/restconf/data/Cisco-NX-OS-device:System/intf-items/"
        print("Sending Request to SunG_Core_B..." '\n')
        responseb = requests.patch(urlb, headers=headercores, data=payload,auth=(user, pwd),verify=False)

        if responseb.ok == True:
            print("Core_B Command Successful!")
        else:
            print(str(responseb)+" - "+responseb.text)

        if responsea.ok and responseb.ok == True:
            print(str.center(" Milestone 2 Reached ",60,"#"))
            print(str.center(" Recovery Network is UP. Core Network and Command Center are now available. ",60,"#"),"\n")
    
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
