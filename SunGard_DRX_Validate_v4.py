import requests
import getpass
import json
from getpass import getpass
requests.packages.urllib3.disable_warnings()

#Global Variables
Loop = False
ipcorea = '10.200.71.5'
ipcoreb = '10.200.71.7'

#Main Menu
def main_menu():
    menu = {
        1 : "Verify Route to CorpDMZ",
        2 : "Verify Route to IntDMZ(Default Route)",
        3 : "VLAN 1102 OSPF Adjacency",
        4 : "VLAN 1105 OSPF Adjancency",
        5 : "Exit"
    }
    print("Choose an option from the list below:")
    for key in menu.keys():
        print(key, '-', menu[key])
    try:
        choice = int(input("Selection: "))
        menu[choice]
        if choice == 1:
            print("Core_A Route to 172.23.35.0 via:")
            routeverify1(ipcorea,corea_cookie)
            print("Core_B Route to 172.23.35.0 via:")
            routeverify1(ipcoreb,coreb_cookie)
            print("Core_A Route to 172.24.35.0 via:")
            routeverify2(ipcorea,corea_cookie)
            print("Core_B Route to 172.24.35.0 via:")
            routeverify2(ipcoreb,coreb_cookie)
            rerun()
        if choice == 2:
            print("Core_A Route to 0.0.0.0 via:")
            routenexthopverify(ipcorea,corea_cookie)
            print("Core_A Route to 0.0.0.0 via:")
            routenexthopverify(ipcoreb,coreb_cookie)
            rerun()
        if choice == 3:
            print("Core_A Adjacency:")
            vlan1102adj(ipcorea,corea_cookie)
            print("Core_B Adjacency:")
            vlan1102adj(ipcoreb,coreb_cookie)
            rerun()
        if choice == 4:
            print("Core_A Adjacency:")
            vlan1105adj(ipcorea,corea_cookie)
            print("Core_B Adjacency:")
            vlan1105adj(ipcoreb,coreb_cookie)
            rerun()
        if choice == 5:
            end()
    except Exception as e:
        print(e)

#Collect Credentials
def getuser():
    user = input("Username: ")
    pwd = getpass("Password: ")
    return user, pwd

#Login to device and generate Authentication Cookie
def aaa_login(user, pwd, ip):
    
    try:
        payload = {
            'aaaUser' : {
                'attributes' : {
                    'name' : user,
                    'pwd' : pwd
                    }
                }
            }
        url = "https://" + ip + "/api/aaaLogin.json"
        authcookie = {}

        response = requests.post(url, data=json.dumps(payload),verify=False)
        if response.ok:
            data = json.loads(response.text)
            token = data['imdata'][0]['aaaLogin']['attributes']['token']
            authcookie = {"APIC-cookie":token}
            return authcookie
        else:
            print(str(response)+" "+response.text)
    
    except Exception as ex:
        print(ex)
  
def routeverify1(ip, auth_cookie):
    url = "https://" + ip + "/api/mo/sys/ipv4/inst/dom-default/rt-[172.23.35.0/24].json?rsp-subtree=full"
    response = requests.get(url,data=None, cookies=auth_cookie, verify=False)
    data = json.loads(response.text)
    route = data["imdata"][0]["ipv4Route"]["children"][0]["ipv4Nexthop"]["attributes"]["nhAddr"]
    print(route,"\n")

def routeverify2(ip, auth_cookie):
    url = "https://" + ip + "/api/mo/sys/ipv4/inst/dom-default/rt-[172.24.35.0/24].json?rsp-subtree=full"
    response = requests.get(url,data=None, cookies=auth_cookie, verify=False)
    data = json.loads(response.text)
    route = data["imdata"][0]["ipv4Route"]["children"][0]["ipv4Nexthop"]["attributes"]["nhAddr"]
    print(route,"\n")

def routenexthopverify(ip, auth_cookie):
    url = "https://" + ip + "/api/mo/sys/ospf/inst-eriecore/dom-default/db-rt/rt-[0.0.0.0/0].json?rsp-subtree=full"
    response = requests.get(url,data=None, cookies=auth_cookie, verify=False)
    data = json.loads(response.text)
    route = data["imdata"][0]["ospfRoute"]["children"][0]["ospfUcNexthop"]["attributes"]["rn"]
    print(route,"\n")

def vlan1102adj(ip, auth_cookie):
    url = "https://" + ip + "/api/mo/sys/ospf/inst-eriecore/dom-default/if-[vlan1102].json?rsp-subtree=children&rsp-subtree-class=ospfAdjEp"
    response = requests.get(url,data=None, cookies=auth_cookie, verify=False)
    data = json.loads(response.text)
    id = data["imdata"][0]["ospfIf"]["children"][0]["ospfAdjEp"]["attributes"]["id"]
    peer = data["imdata"][0]["ospfIf"]["children"][0]["ospfAdjEp"]["attributes"]["peerIp"]
    print("Neighbor ID: "+id,"\n""Address: "+peer,"\n")

def vlan1105adj(ip, auth_cookie):
    url = "https://" + ip + "/api/mo/sys/ospf/inst-eriecore/dom-default/if-[vlan1105].json?rsp-subtree=children&rsp-subtree-class=ospfAdjEp"
    response = requests.get(url,data=None, cookies=auth_cookie, verify=False)
    data = json.loads(response.text)
    id = data["imdata"][0]["ospfIf"]["children"][0]["ospfAdjEp"]["attributes"]["id"]
    peer = data["imdata"][0]["ospfIf"]["children"][0]["ospfAdjEp"]["attributes"]["peerIp"]
    print("Neighbor ID: "+id,"\n""Address: "+peer,"\n")

#Prompt user to return to Main Menu
def rerun():
    rerun = {
        1 :  "Yes",
        2 :  "No"
    }
    print("Return to Main Menu?: ")
    for key in rerun.keys():
        print(key, '-', rerun[key])
    try:
        choice = int(input("Selection: "))
        if choice == 1:
            main_menu()
        elif choice == 2:
            end()
    except (ValueError, KeyError, TypeError):
        print("Invalid option.")

#Log out of device session
def aaa_logout(user, ip, auth_cookie):
    try:
        payload = {
            'aaaUser' : {
                'attributes' : {
                    'name' : user
                    }
                }
            }
        url = "https://" + ip + "/api/aaaLogout.json"

        response = requests.post(url, data=json.dumps(payload),cookies=auth_cookie,verify=False)
        if response.ok == True:
            print("\n""Logout Successful""\n")
        else:
            print(str(response)+" "+response.text)

    except Exception as ex:
        print(ex)

#End the application
def end():
    print("Thank-you for using this application!")
    aaa_logout(user,ipcorea,corea_cookie)
    aaa_logout(user,ipcoreb,coreb_cookie)
    input("Press enter to close.")
    quit()

#Display welcome message & collect user credentials
print("Welcome!")
print(str.center(" IMPORTANT ",60,"#"))
print(str.center("Validation requires use of the local admin account with the current enable password ",60,"#"),"\n")
#Loop to keep Login prompt open if authentication fails
while Loop == False:
    try:
        user, pwd = getuser()
        #Collect token specific for Core A & display the token
        corea_cookie = aaa_login(user, pwd, ipcorea)
        print("\n" "Core_A Authentication Token: " "\n" + str(corea_cookie["APIC-cookie"]), "\n")
        #Collect token specific for Core B & display the token
        coreb_cookie = aaa_login(user, pwd, ipcoreb)
        print("Core_B Authentication Token: " "\n" + str(coreb_cookie["APIC-cookie"]), "\n")
    except Exception as ex:
        print(ex)
        print("Login error. Please try again.""\n")
    else:
        #Change Loop variable to true in order to keep Main Menu open after successful authentication
        Loop = True
        while Loop == True:
            main_menu()