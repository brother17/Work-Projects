from getpass import getpass
import requests
requests.packages.urllib3.disable_warnings()

#Variables
loop = True
headers = {
    'Content-Type': 'application/json',
    'Accept': '*/*',
    'Cache-Control': 'no-cache'
}
#Device IPs used throughout this application
internetf5ip = "10.1.54.20"
corpdmzf5ip = "10.1.54.20"
prodf5ip = "10.1.54.20"

#Main menu to select a device
def main_menu(user,pwd):
    print("\n""F5 devices are listed below:")
    devicemenu = {
        1 : "Internet F5",
        2 : "Corp-DMZ F5",
        3 : "Prod F5",
        4 : "Exit"
    }
    for key in devicemenu.keys():
        print(key, '-', devicemenu[key])
    try:
        choice = int(input("Please select the target device: "))
        devicemenu[choice]
        if choice == 1:
            print("\n""Selected Device: "+ devicemenu[choice])
            action_menu(internetf5ip,user,pwd)
        if choice == 2:
            print("\n""Selected Device: "+ devicemenu[choice])
            action_menu(corpdmzf5ip,user,pwd)
        if choice == 3:
            print("\n""Selected Device: "+ devicemenu[choice])
            action_menu(prodf5ip,user,pwd)
        if choice == 4:
            end()
    except Exception as e :
        print(e)

#Designate the action to perform on the selected device
def action_menu(ip, user, pwd):
    action_menu = {
        1 : "Create UCS backup file",
        2 : "Re-create SNMP Traps",
        3 : "Revert Management IP to Home Office Address",
        4 : "Revert Default Gateway to Home Office Device",
        5 : "Return"
    }
    print("\n""Available actions:")
    for key in action_menu.keys():
        print(key, '-', action_menu[key])
    try:
        choice = int(input("Please select the action to perform: "))
        action_menu[choice]
        if choice == 1:
            createucs(ip,user,pwd)
            rerun(ip,user,pwd)
        if choice == 2:
            deletetraps(ip,user,pwd)
            rerun(ip,user,pwd)
        if choice == 3:
            changemgmtip(ip,user,pwd)
            rerun(ip,user,pwd)
        if choice == 4:
            changegateway(ip,user,pwd)
            rerun(ip,user,pwd)
        if choice == 5:
            main_menu(user, pwd)
    except Exception as e :
        print(e)

#Collect user credentials
def getuser():
    user = input("Username: ")
    pwd = getpass("Password: ")
    return user, pwd

#Create a UCS backup file with the specified name
def createucs(ip, user, pwd):
    url = "https://"+ip+"/mgmt/tm/sys/ucs"
    filename = input("Filename: ")+".ucs"
    payload = {
            "command": "save",
            "name": filename
        }
    response = requests.post(url,json=payload,headers=headers,auth=(user,pwd),verify=False)
    print("\n""Device response: "+response.text,"\n")

    #if input("Download file? y/n ") == "y":
    #    fileurl = "https://"+ip+"/mgmt/shared/file-transfer/ucs-downloads/"+filename
    #    file = open(filename, "wb")
    #    file.write(requests.get(fileurl,auth=(user,pwd),verify=False,stream=True).content)
    #    file.close

#Delete the SNMP Traps on the specified device as outlined in the DRX guide
#Note: The Internet F5 only has one trap removed, while Corp DMZ and Prod have two
def deletetraps(ip,user,pwd):
    url = "https://"+ip+"/mgmt/tm/sys/management-route/"
    payload = {
        "items": [
            {
                "kind": "tm:sys:management-route:management-routestate",
                "name": "snmp_trap_dst",
                "partition": "Common",
                "fullPath": "/Common/snmp_trap_dst",
                "generation": 1,
                "selfLink": "https://localhost/mgmt/tm/sys/management-route/~Common~snmp_trap_dst?ver=14.1.4.6",
                "gateway": "10.200.15.20",
                "mtu": 0,
                "network": "10.1.50.138/32"
            }
        ]
    }
    payload2 = "**placeholder**"
    if ip == internetf5ip:
        dsturl = url+"snmp_trap_dst"
        response = requests.put(dsturl,json=payload,headers=headers,auth=(user,pwd),verify=False)
        print("\n""Device response: "+response.text,"\n")
    if ip == corpdmzf5ip or prodf5ip:
        dsturl = url+"snmp_trap_dst"
        response = requests.put(dsturl,json=payload2,headers=headers,auth=(user,pwd),verify=False)
        print("\n""Device response: "+response.text,"\n")

        nim12url = url+"snmp_trap_dst_nim12"
        response = requests.put(nim12url,json=payload2,headers=headers,auth=(user,pwd),verify=False)
        print("\n""Device response: "+response.text,"\n")

#Update the mamagement IP on the selected device
def changemgmtip(ip,user,pwd):
    url = "https://"+ip+"/mgmt/tm/sys/management-ip"
    if ip == internetf5ip:
        mgmt = "10.200.60.15"
    if ip == corpdmzf5ip:
        mgmt = "10.200.60.17"
    if ip == prodf5ip:
        mgmt = "10.200.60.16"
    payload = {
        "name": mgmt+"/255.255.255.0"
    }
    print("Sending request...""\n")
    response = requests.patch(url,json=payload,headers=headers,auth=(user,pwd),verify=False)
    print("\n""Device response: "+response.text,"\n")

#Update the default gateway on the selected device
def changegateway(ip,user,pwd):
    gateway = "10.200.60.20"
    url = "https://"+ip+"/mgmt/tm/sys/management-route/default"
    payload = {
            "name": "default",
            "gateway": gateway
        }
    print("Sending request...""\n")
    response = requests.patch(url,json=payload,headers=headers,auth=(user,pwd),verify=False)
    print("\n""Device response: "+response.text,"\n")

#Save the device configuration
def saveconfig(ip,user,pwd):
    url = "https://"+ip+"/mgmt/tm/sys/"
    payload = {
            "command": "save"
        }
    print("\n""Saving device configuration...")
    response = requests.post(url,json=payload,headers=headers,auth=(user,pwd),verify=False)
    print("\n""Device response: "+response.text,"\n")

#Prompt to continue working with the selected device
def rerun(ip,user,pwd):
    print("\n""Continue with selected device?")
    rerun = {
        1 :  "Yes",
        2 :  "No"
    }
    for key in rerun.keys():
        print(key, '-', rerun[key])
    try:
        choice = int(input("Selection: "))
        if choice == 1:
            action_menu(ip,user,pwd)
        elif choice == 2:
            main_menu(user,pwd)
    except Exception as e:
        print(e)

#Exit the application
def end():
    print("\n""Thank-you for using this application!")
    input("Press enter to close.")
    quit()

#Loop to keep Main Menu open and collect user credentials
#User credentials are passed throughout the application
while loop == True:
    print("Welcome!")
    user, pwd = getuser()
    main_menu(user,pwd)