import requests
import os
import pandas
import numpy
import time
from base64 import b64encode
from getpass import getpass
import warnings
warnings.filterwarnings("ignore")
requests.packages.urllib3.disable_warnings()

def gettoken(ip):
    try:
        user = input("Username: ")
        pwd = getpass("Password: ")
        creds = b64encode(bytes(user+":"+pwd,encoding="utf-8")).decode("ascii")

        url = "https://"+ip+"/api/fmc_platform/v1/auth/generatetoken"
        header = {
            "Authorization":"Basic "+creds
        }
        body = None
        response = requests.post(url,headers=header,data=body,verify=False)

        if response.ok == False:
            print(str(response)+" - "+response.text)

        if response.ok == True:
            auth_token = response.headers["X-auth-access-token"]
            ref_token = response.headers["X-auth-refresh-token"]
            domain_uuid = response.headers["DOMAIN_UUID"]

            print("Login Successful!")
            print("Authentication Token: "+auth_token)
            print("Refresh Token: "+ref_token)
            print("Domain UUID: "+domain_uuid)

            return auth_token, ref_token, domain_uuid

    except Exception as ex:
        print(ex)

def refreshtoken(ip,atoken):
    try:
        url = "https://"+ip+"/api/fmc_platform/v1/auth/refreshtoken"
        header = {
            "X-auth-access-token":atoken,
            "X-auth-refresh-token":atoken
        }
        body = None
        response = requests.post(url,headers=header,data=body,verify=False)

        if response.ok == False:
            print(str(response)+" - "+response.text)
        else:
            print("Token successfully refreshed!")
    except Exception as ex:
        print(ex)

def convertnetworks():
    try:
        csvtable = pandas.DataFrame(columns=["NAME","DESCRIPTION","VALUE","LOOKUP"])

        file = input("Specify source file location: ")
        with open(file, mode="r") as filedata:
            print("Reading source file...""\n")
            csvdata = pandas.read_csv(filedata,header=0,index_col=False,skipinitialspace=True)
            print(csvdata)
        
        filteredcsv = csvdata[["Name","Comments","IPv4 address","Mask"]]

        print("\n""Converting file...")
        mergedtable = pandas.concat([csvtable,filteredcsv.rename(columns={"Name":"NAME","Comments":"DESCRIPTION","IPv4 address":"VALUE"})])
        mergedtable.insert(2,"TYPE","Network")

        mergedtable.loc[mergedtable["Mask"]=="255.255.255.255",["TYPE"]] = "Host"
        mergedtable.loc[mergedtable["Mask"]=="255.255.255.255",["Mask"]] = ""
        mergedtable.loc[mergedtable["Mask"]=="255.255.255.254",["Mask"]] = "/31"
        mergedtable.loc[mergedtable["Mask"]=="255.255.255.252",["Mask"]] = "/30"
        mergedtable.loc[mergedtable["Mask"]=="255.255.255.248",["Mask"]] = "/29"
        mergedtable.loc[mergedtable["Mask"]=="255.255.255.240",["Mask"]] = "/28"
        mergedtable.loc[mergedtable["Mask"]=="255.255.255.224",["Mask"]] = "/27"
        mergedtable.loc[mergedtable["Mask"]=="255.255.255.192",["Mask"]] = "/26"
        mergedtable.loc[mergedtable["Mask"]=="255.255.255.128",["Mask"]] = "/25"
        mergedtable.loc[mergedtable["Mask"]=="255.255.255.0",["Mask"]] = "/24"
        mergedtable.loc[mergedtable["Mask"]=="255.255.254.0",["Mask"]] = "/23"
        mergedtable.loc[mergedtable["Mask"]=="255.255.252.0",["Mask"]] = "/22"
        mergedtable.loc[mergedtable["Mask"]=="255.255.248.0",["Mask"]] = "/21"
        mergedtable.loc[mergedtable["Mask"]=="255.255.240.0",["Mask"]] = "/20"
        mergedtable.loc[mergedtable["Mask"]=="255.255.224.0",["Mask"]] = "/19"
        mergedtable.loc[mergedtable["Mask"]=="255.255.192.0",["Mask"]] = "/18"
        mergedtable.loc[mergedtable["Mask"]=="255.255.128.0",["Mask"]] = "/17"
        mergedtable.loc[mergedtable["Mask"]=="255.255.0.0",["Mask"]] = "/16"
        mergedtable.loc[mergedtable["Mask"]=="255.254.0.0",["Mask"]] = "/15"
        mergedtable.loc[mergedtable["Mask"]=="255.252.0.0",["Mask"]] = "/14"
        mergedtable.loc[mergedtable["Mask"]=="255.248.0.0",["Mask"]] = "/13"
        mergedtable.loc[mergedtable["Mask"]=="255.240.0.0",["Mask"]] = "/12"
        mergedtable.loc[mergedtable["Mask"]=="255.0.0.0",["Mask"]] = "/8"
        mergedtable.loc[mergedtable["Mask"]=="240.0.0.0",["Mask"]] = "/4"

        mergedtable["VALUE"] = mergedtable["VALUE"]+mergedtable["Mask"]
        mergedtable = mergedtable.drop("Mask",axis=1)
        mergedtable["NAME"] = mergedtable["NAME"].replace(" ","_",regex=True)
        extrahosts = mergedtable.loc[mergedtable["TYPE"] == "Host"]
        finaltable = mergedtable.drop(mergedtable.index[mergedtable["TYPE"] == "Host"])

        print("\n""Converted data:")
        print(finaltable)

        print("\n""Networks that will be made as Hosts:")
        print(extrahosts)

        save = input("\n""Create new CSV using the above data? y/n: ")
        if save == "y":
            filepath = input("Specify location to save file: ")+"\\"
            filename = input("Specify new file name: ")
            hostfilename = filename+"-hosts.csv"
            fullfilename = os.path.join(filepath+filename)+".csv"
            fullhostfilename = os.path.join(filepath+hostfilename)

            finaltable.to_csv(fullfilename,index=False)
            extrahosts.to_csv(fullhostfilename,index=False)
            print("\n""File saved!")
            return finaltable, extrahosts
        if save == "n":
            pass
            return finaltable, extrahosts
    
    except Exception as e:
        print(e)

def converthosts():
    try:
        csvtable = pandas.DataFrame(columns=["NAME","DESCRIPTION","VALUE","LOOKUP"])

        file = input("Specify source file location: ")
        with open(file, mode="r") as filedata:
            print("Reading source file...""\n")
            csvdata = pandas.read_csv(filedata,header=0,index_col=False,skipinitialspace=True)
            print(csvdata)
        
        filteredcsv = csvdata[["Name","Comments","IPv4 address"]]

        print("\n""Converting file...")
        mergedtable = pandas.concat([csvtable,filteredcsv.rename(columns={"Name":"NAME","Comments":"DESCRIPTION","IPv4 address":"VALUE"})])
        mergedtable.insert(2,"TYPE","Host")

        print(mergedtable)
        save = input("\n""Create new CSV using the above data? y/n: ")
        if save == "y":
            filepath = input("Specify location to save file: ")+"\\"
            filename = input("Specify new file name: ")+".csv"
            fullfilename = os.path.join(filepath+filename)

            mergedtable.to_csv(fullfilename,index=False)
            print("\n""File saved!")
            return mergedtable
        if save == "n":
            return mergedtable
    except Exception as ex:
        print(ex)

def converttcpports():
    try:
        csvtable = pandas.DataFrame(columns=["NAME","PORT","ICMPCODE","ICMPTYPE"])

        file = input("Specify source file location: ")
        with open(file, mode="r") as filedata:
            print("Reading source file...""\n")
            csvdata = pandas.read_csv(filedata,header=0,index_col=False,skipinitialspace=True)
            print(csvdata)
        
        filteredcsv = csvdata[["Name","Port"]]

        print("\n""Converting file...")
        mergedtable = pandas.concat([csvtable,filteredcsv.rename(columns={"Name":"NAME","Port":"PORT"})])
        mergedtable.insert(1,"PROTOCOL","TCP")

        print(mergedtable)
        save = input("\n""Create new CSV using the above data? y/n: ")
        if save == "y":
            filepath = input("Specify location to save file: ")+"\\"
            filename = input("Specify new file name: ")+".csv"
            fullfilename = os.path.join(filepath+filename)

            mergedtable.to_csv(fullfilename,index=False)
            print("\n""File saved!")
            return mergedtable
        if save == "n":
            pass
            return mergedtable
    except Exception as ex:
        print(ex)

def convertudpports():
    try:
        csvtable = pandas.DataFrame(columns=["NAME","PORT","ICMPCODE","ICMPTYPE"])

        file = input("Specify source file location: ")
        with open(file, mode="r") as filedata:
            print("Reading source file...""\n")
            csvdata = pandas.read_csv(filedata,header=0,index_col=False,skipinitialspace=True)
            print(csvdata)
        
        filteredcsv = csvdata[["Name","Port"]]

        print("\n""Converting file...")
        mergedtable = pandas.concat([csvtable,filteredcsv.rename(columns={"Name":"NAME","Port":"PORT"})])
        mergedtable.insert(1,"PROTOCOL","UDP")

        print(mergedtable)
        save = input("\n""Create new CSV using the above data? y/n: ")
        if save == "y":
            filepath = input("Specify location to save file: ")+"\\"
            filename = input("Specify new file name: ")+".csv"
            fullfilename = os.path.join(filepath+filename)

            mergedtable.to_csv(fullfilename,index=False)
            print("\n""File saved!")
            return mergedtable
        if save == "n":
            pass
            return mergedtable
    except Exception as ex:
        print(ex)

def convertrange():
    try:
        csvtable = pandas.DataFrame(columns=["NAME","DESCRIPTION","VALUE","LOOKUP"])

        file = input("Specify source file location: ")
        with open(file, mode="r") as filedata:
            print("Reading source file...""\n")
            csvdata = pandas.read_csv(filedata,header=0,index_col=False,skipinitialspace=True)
            print(csvdata)
        
        filteredcsv = csvdata[["Name","Comments","IPv4 address"]]

        print("\n""Converting file...")
        mergedtable = pandas.concat([csvtable,filteredcsv.rename(columns={"Name":"NAME","Comments":"DESCRIPTION","IPv4 address":"VALUE"})])
        mergedtable.insert(2,"TYPE","Range")
        print(mergedtable)
        
        save = input("\n""Create new CSV using the above data? y/n: ")
        if save == "y":
            filepath = input("Specify location to save file: ")+"\\"
            filename = input("Specify new file name: ")+".csv"
            fullfilename = os.path.join(filepath+filename)

            mergedtable.to_csv(fullfilename,index=False)
            print("\n""File saved!")
            return mergedtable
        if save == "n":
            pass
            return mergedtable
    except Exception as ex:
        print(ex)
    return mergedtable

def end():
    print("Thank-you for using this application!")
    input("Press enter to close.")
    quit()

Loop = True
fmc, auth_token, ref_token, domain_uuid = None, None, None, None
main_menu = {
    1 : "Authentication Options",
    2 : "Upload Options",
    3 : "Exit"
}
token_menu = {
    1 : "Login",
    2 : "Refresh Token",
    3 : "Return"
}
upload_menu = {
    1 : "Convert & Create Network Objects - Networks",
    2 : "Convert & Create Network Objects - Ranges",
    3 : "Convert & Create Network Objects - Hosts",
    4 : "Convert & Create Network Objects - TCP Ports",
    5 : "Convert & Create Network Objects - UDP Ports",
    6 : "Exit"
}

while Loop == True:
    print("Choose an option from the list below:")
    for key in main_menu.keys():
        print(key," - ",main_menu[key])
    try:
        main_choice = int(input("Selection: "))
        main_menu[main_choice]
        if main_choice == 1:
            print("Choose an option from the list below:")
            for key in token_menu.keys():
                print(key," - ",token_menu[key])    
            try:
                auth_choice = int(input("Selection: "))
                token_menu[auth_choice]
                if auth_choice == 1:
                    fmc = input("Enter FMC IP: ")
                    auth_token, ref_token, domain_uuid = gettoken(fmc)
                    header = {
                                "X-auth-access-token":auth_token
                            }
                if auth_choice == 2:
                    refreshtoken(fmc,auth_token)
                if auth_choice == 3:
                    pass
            except Exception as ex:
                print(ex)
        if main_choice == 2:
            if auth_token == None:
                print("You must generate a Login Token to proceed.""\n""Please use option 1 to generate a token.""\n")
            else:
                print("Choose an option from the list below:")
                for key in upload_menu.keys():
                    print(key," - ",upload_menu[key])
                try:
                    upload_choice = int(input("Selection: "))
                    upload_menu[upload_choice]
                    if upload_choice == 1:
                        net_obj, ehost = convertnetworks()
                        try:
                            net_url = "https://"+str(fmc)+"/api/fmc_config/v1/domain/"+str(domain_uuid)+"/object/networks?bulk=true"
                            #net_body = []
                            for i,row in net_obj.iterrows():
                                n_body={
                                        "name": str(row["NAME"]),
                                        "value": str(row["VALUE"]),
                                        "description": str(row["DESCRIPTION"]),
                                        "type": str(row["TYPE"])
                                    }
                                #net_body.append(n_body.copy())
                                try:
                                    response = requests.post(net_url,headers=header,json=n_body,verify=False)
                                    time.sleep(0.5)
                                    if response.ok == True:
                                        print("Network "+str(n_body["name"])+" successfully created.")
                                    else:
                                        print("Error for "+str(n_body["name"])+" - "+str(response)+" "+response.text)
                                except Exception as ex:
                                    print(ex)

                            ehost_url = "https://"+str(fmc)+"/api/fmc_config/v1/domain/"+str(domain_uuid)+"/object/hosts?bulk=true"
                            #ehost_body = []
                            for i,row in ehost.iterrows():
                                eh_body={
                                        "name": str(row["NAME"]),
                                        "value": str(row["VALUE"]),
                                        "description": str(row["DESCRIPTION"]),
                                        "type": str(row["TYPE"])
                                    }
                                #ehost_body.append(eh_body.copy())
                                try:
                                    response = requests.post(ehost_url,headers=header,json=eh_body,verify=False)
                                    time.sleep(0.5)
                                    if response.ok == True:
                                        print("Host "+str(eh_body["name"])+" successfully created.")
                                    else:
                                        print("Error for "+str(eh_body["name"])+" - "+str(response)+" "+response.text)
                                except Exception as ex:
                                    print(ex)
                        except Exception as ex:
                            print(ex)
                    if upload_choice == 2:
                        range_obj = convertrange()
                        try:
                            range_url = "https://"+str(fmc)+"/api/fmc_config/v1/domain/"+str(domain_uuid)+"/object/ranges?bulk=true"
                            #range_body = []
                            for i,row in range_obj.iterrows():
                                r_body={
                                        "name": str(row["NAME"]),
                                        "value": str(row["VALUE"]),
                                        "description": str(row["DESCRIPTION"]),
                                        "type": str(row["TYPE"])
                                    }
                                #range_body.append(r_body.copy())
                                try:
                                    response = requests.post(range_url,headers=header,json=r_body,verify=False)
                                    time.sleep(0.5)
                                    if response.ok == True:
                                        print("Range "+str(r_body["name"])+" successfully created.")
                                    else:
                                        print("Error for "+str(r_body["name"])+" - "+str(response)+" "+response.text)
                                except Exception as ex:
                                    print(ex)
                        except Exception as ex:
                            print(ex)
                    if upload_choice == 3:
                        host_obj = converthosts()
                        try:
                            host_url = "https://"+str(fmc)+"/api/fmc_config/v1/domain/"+str(domain_uuid)+"/object/hosts?bulk=true"
                            #host_body = []
                            for i,row in host_obj.iterrows():
                                h_body={
                                        "name": str(row["NAME"]),
                                        "value": str(row["VALUE"]),
                                        "description": str(row["DESCRIPTION"]),
                                        "type": str(row["TYPE"])
                                    }
                                #host_body.append(h_body.copy())
                                try:
                                    response = requests.post(host_url,headers=header,json=h_body,verify=False)
                                    time.sleep(0.5)
                                    if response.ok == True:
                                        print("Host "+str(h_body["name"])+" successfully created.")
                                    else:
                                        print("Error for host "+str(h_body["name"])+" - "+str(response)+" "+response.text)
                                except Exception as ex:
                                    print(ex)
                        except Exception as ex:
                            print(ex)
                    if upload_choice == 4:
                        tcp_obj = converttcpports()
                        try:
                            tcp_url = "https://"+str(fmc)+"/api/fmc_config/v1/domain/"+str(domain_uuid)+"/object/protocolportobjects?bulk=true"
                            #tcp_body = []
                            for i,row in tcp_obj.iterrows():
                                t_body={
                                        "name": str(row["NAME"]),
                                        "protocol": str(row["PROTOCOL"]),
                                        "port": str(row["PORT"]),
                                        "type": "ProtocolPortObject"
                                    }
                                #tcp_body.append(t_body.copy())
                                try:
                                    response = requests.post(tcp_url,headers=header,json=t_body,verify=False)
                                    time.sleep(0.5)
                                    if response.ok == True:
                                        print("TCP Object "+str(t_body["name"])+" successfully created.")
                                    else:
                                        print("Error for: "+str(t_body["name"])+" - "+str(response)+" "+response.text)
                                except Exception as ex:
                                    print(ex)
                        except Exception as ex:
                            print(ex)
                    if upload_choice == 5:
                        udp_obj = convertudpports()
                        try:
                            udp_url = "https://"+str(fmc)+"/api/fmc_config/v1/domain/"+str(domain_uuid)+"/object/protocolportobjects?bulk=true"
                            #udp_body = []
                            for i,row in udp_obj.iterrows():
                                u_body={
                                        "name": str(row["NAME"]),
                                        "protocol": str(row["PROTOCOL"]),
                                        "port": str(row["PORT"]),
                                        "type": "ProtocolPortObject"
                                    }
                                #udp_body.append(u_body.copy())
                                try:
                                    response = requests.post(udp_url,headers=header,json=u_body,verify=False)
                                    time.sleep(0.5)
                                    if response.ok == True:
                                        print("UDP Object "+str(u_body["name"])+" successfully created.")
                                    else:
                                        print("Error for: "+str(u_body["name"])+" - "+str(response)+" "+response.text)
                                except Exception as ex:
                                    print(ex)
                        except Exception as ex:
                            print(ex)
                    if upload_choice == 6:
                        pass
                except Exception as ex:
                    print(ex)
        if main_choice == 3:
            end()
    except Exception as ex:
        print(ex)