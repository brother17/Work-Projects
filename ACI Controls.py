from getpass import getpass
import requests
import json
import pandas
requests.packages.urllib3.disable_warnings()

def aaa_login(ip,user,pwd):
    url = "https://"+ip+"/api/aaaLogin.json"
    creds = {
        "aaaUser":
            {"attributes":
                {
                    "name":user,
                    "pwd":pwd
                }
            }
        }
    
    try: 
        response = requests.post(url,json=creds,verify=False)
        json_response = json.loads(response.text)
        token = json_response["imdata"][0]["aaaLogin"]["attributes"]["token"]
        if response.ok == True:
            print("Login Successful!""\n")
            print("Token: "+str(token))
            return token
        else:
            print(response.text)

    except Exception as ex:
        print(ex)

def aaa_logout(ip,user,token):
    url = "https://"+ip+"/api/aaaLogout.json"
    creds = {
        "aaaUser":
            {"attributes":
                {
                    "name":user
                }
            }
        }
    auth = {
        "APIC-Cookie":token
    }

    try:
        response = requests.post(url,json=creds,cookies=auth,verify=False)
        if response.ok == True:
            print("Logout Successful!")
        else:
            print(response.text)
    except Exception as ex:
        print(ex)

def fvBD(ip, token):
    url = "https://"+ip+"/api/class/fvBD.json?rsp-subtree=full"
    auth = {
        "APIC-Cookie":token
    }

    response = requests.get(url,cookies=auth,verify=False)
    raw = json.loads(response.text)
    data = pandas.read_json(raw["imdata"])
    print(data)

def fvAEPg(ip,token):
    url = "https://"+ip+"/api/class/fvAEPg.json?rsp-subtree=full"
    auth = {
        "APIC-Cookie":token
    }

    response = requests.get(url,cookies=auth,verify=False)
    data = json.loads(response.text)
    print(json.dumps(data,indent=2))
    #for count, fvAEPg in enumerate(data["imdata"], start=1):
        #print("Entry "+str(count)+" - "+"'"+fvAEPg["fvAEPg"]["attributes"]["name"]+"':")
        #print(json.dumps(fvAEPg["fvAEPg"]["attributes"],indent=2))

loop = True
ip, token = None, None
main_menu = {
    1 : "Login",
    2 : "Actions",
    3 : "Exit"
}
action_menu = {
    1 : "fvBD",
    2 : "fvAEPg"
}
while loop == True:
    print("Choose an option from the list below:")
    for key in main_menu.keys():
        print(key," - ",main_menu[key])
    try:
        main_choice = int(input("Selection: "))
        if main_choice == 1:
            ip = input("Enter Device IP: ")
            username = input("Enter username: ")
            password = getpass("Enter password: ")
            token = aaa_login(ip,username,password)
        if main_choice == 2:
            if token is None:
                print("\n""You must authenticate before proceeding.""\n""Please use option 1 to authenticate.""\n")
            else:
                print("Choose an option from the list below:")
                for key in action_menu.keys():
                    print(key," - ",action_menu[key])
                action_choice = int(input("Selection: "))
                if action_choice == 1:
                    fvBD(ip,token)
                if action_choice == 2:
                    fvAEPg(ip,token)
        if main_choice == 3:
            if token is not None:
                aaa_logout(ip,username,token)
            input("Press enter to close")
            exit()
    except Exception as ex:
        print(ex)