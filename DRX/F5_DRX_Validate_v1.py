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
internetf5ip = "10.200.60.15"
corpdmzf5ip = "10.200.60.17"
prodf5ip = "10.200.60.16"

#Main menu to select a device
def main_menu(user,pwd):
    devicemenu = {
        1 : "Internet F5",
        2 : "Corp-DMZ F5",
        3 : "Prod F5",
        4 : "Exit"
    }
    print("\n""Note: This script will only work AFTER performing DRX activities.")
    print("F5 devices are listed below:")
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
        1 : "View Management IP",
        2 : "View Default Gateway",
        3 : "Return"
    }
    print("\n""Available actions: ")
    for key in action_menu.keys():
        print(key, '-', action_menu[key])
    try:
        choice = int(input("Selection: "))
        action_menu[choice]
        if choice == 1:
            verifymgmtip(ip,user,pwd)
            rerun(ip,user,pwd)
        if choice == 2:
            verifygateway(ip,user,pwd)
            rerun(ip,user,pwd)
        if choice == 3:
            main_menu(user, pwd)
    except Exception as e :
        print(e)

#Collect user credentials
def getuser():
    user = input("Username: ")
    pwd = getpass("Password: ")
    return user, pwd

#View the mamagement IP on the selected device
def verifymgmtip(ip,user,pwd):
    url = "https://"+ip+"/mgmt/tm/sys/management-ip"
    payload = {}
    print("Sending request...""\n")
    response = requests.get(url,json=payload,headers=headers,auth=(user,pwd),verify=False)
    print("\n""Device response: "+response.text,"\n")

#View the default gateway on the selected device
def verifygateway(ip,user,pwd):
    url = "https://"+ip+"/mgmt/tm/sys/management-route/default"
    payload = {}
    print("Sending request...""\n")
    response = requests.get(url,json=payload,headers=headers,auth=(user,pwd),verify=False)
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
