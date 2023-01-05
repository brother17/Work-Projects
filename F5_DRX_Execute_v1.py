from getpass import getpass
import os
import requests
import paramiko
from paramiko import SSHClient
from scp import SCPClient
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
    devicemenu = {
        1 : "Internet F5",
        2 : "Corp-DMZ F5",
        3 : "Prod F5",
        4 : "Exit"
    }
    print("\n""F5 devices are listed below:")
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
        1 : "Create & Download UCS backup file",
        2 : "Delete SNMP Traps",
        3 : "Update Management IP to SunGard Address",
        4 : "Update Default Gateway",
        5 : "Return"
    }
    print("\n""Available actions:")
    for key in action_menu.keys():
        print(key, '-', action_menu[key])
    try:
        choice = int(input("Please select the action to perform: "))
        action_menu[choice]
        if choice == 1:
            hostname = None
            if ip == "10.1.54.20":
                hostname = "labf5"
                #hostname = "INT_DMZ-f5-secondary"
            #if ip == "10.1.54.20":
                #hostname = "CorpDMZ-f5-crp-secondary"
            #if ip == "10.1.54.20":
                #hostname = "Prod-f5-secondary"
            createucs(ip,user,pwd,hostname)
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

#Create a UCS backup file with the specified name and download it to a specified location
def createucs(ip, user, pwd,hostname):
    url = "https://"+ip+"/mgmt/tm/sys/ucs"
    filename = input("Filename: ")+".ucs"
    payload = {
            "command": "save",
            "name": filename
        }
    response = requests.post(url,json=payload,headers=headers,auth=(user,pwd),verify=False)
    print("\n""Device response: "+response.text,"\n")

    getucs(user,pwd,filename,hostname)

#Delete the SNMP Traps on the specified device as outlined in the DRX guide
#Note: The Internet F5 only has one trap removed, while Corp DMZ and Prod have two
def deletetraps(ip,user,pwd):
    url = "https://"+ip+"/mgmt/tm/sys/management-route/"
    payload = {}
    if ip == internetf5ip:
        dsturl = url+"snmp_trap_dst"
        response = requests.delete(dsturl,json=payload,headers=headers,auth=(user,pwd),verify=False)
        print("\n""Device response: "+response.text,"\n")
    if ip == corpdmzf5ip or prodf5ip:
        dsturl = url+"snmp_trap_dst"
        response = requests.delete(dsturl,json=payload,headers=headers,auth=(user,pwd),verify=False)
        print("\n""Device response: "+response.text,"\n")

        nim12url = url+"snmp_trap_dst_nim12"
        response = requests.delete(nim12url,json=payload,headers=headers,auth=(user,pwd),verify=False)
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

#Open SCP connection to device and download UCS file to specified location
def getucs(user,pwd,filename,host):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host+'.erieinsurance.com', 
            port = '22',
            username=user,
            password=pwd,
            look_for_keys=False)

    scp = SCPClient(ssh.get_transport())
    savefrom = "/var/local/ucs/"+filename
    saveto = os.path.normpath((input("Specify where to save the UCS file: ")))
    scp.get(savefrom,saveto)  

#Open SCP connection to the device, specify the file, and upload it to the device
def uploaducs(ip,user,pwd):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=ip+'.erieinsurance.com', 
            port = '22',
            username=user,
            password=pwd,
            look_for_keys=False)

    # SCPCLient takes a paramiko transport as an argument
    scp = SCPClient(ssh.get_transport())    
    scp.put('C:\\Temp\\F5\\F5-Lab-Backup.ucs', '/var/local/ucs/F5-Lab-Backup.ucs')

    # Uploading the 'test' directory with its content in the
    # '/home/user/dump' remote directory
    #scp.put('test', recursive=True, remote_path='/export/home/j9856s')
    scp.close()

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