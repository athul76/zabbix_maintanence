## written by Marcel Kragt & Nicklas Gehlen / lanufaktur GbR
## Version 1.1

import csv
import requests
import json
import datetime

# Editable
ZabbixAPIURL = "http://dcfra-vision-vi-zabbix.sec.allianz/api_jsonrpc.php"
ZabbixAPIUser = 'postman'
ZabbixAPIPassword = 'Mera23Luna5'
logPath = "../logs/maintenance_log.txt"
zabbixHosts = []

# Nix mehr Editable

class Logger():
    def __init__(self, out_path):
        self.out_path = out_path
        with open(self.out_path, mode='a') as f:
            timecode = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write("-"*23 + "\n")
        
    def Log(self, message):
        with open(self.out_path, mode='a') as f:
            timecode = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write("[" + timecode + "] Info: " + message + "\n")
    
    def LogError(self, message):
        with open(self.out_path, mode='a') as f:
            timecode = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write("[" + timecode + "] Error: " + message + "\n")
            

class ZabbixHost():
    def __init__(self, hostName, changeID, von, bis, hostID):
        self.hostName = hostName
        self.changeID = changeID
        self.von = von
        self.bis = bis
        self.hostID = hostID
    
    def getDuration(self):
        return self.bis - self.von
     

def getApiKey():
    result = makeRequest("""
    {
        "jsonrpc": "2.0",
        "method": "user.login",
        "params": {
            "user": "%s",
            "password": "%s"
        },
        "id": 1,
        "auth": null
    }""" % (ZabbixAPIUser, ZabbixAPIPassword))
    return result["result"]
    

def getHostID(hostName):
    result = makeRequest("""{
        "jsonrpc": "2.0",
        "method": "host.get",
        "params": {
            "output": ["hostid"],
            "filter": {
                "host": [
                    "%s"
                ]
            }
        },
        "auth": "%s",
        "id": 1
    }""" % (hostName, apiKey))

    if(len(result["result"]) > 0):
        return result["result"][0]["hostid"]
    return None
    
def makeRequest(payload):
    headers = {
      'Content-Type': 'application/json'
    }
    zbx_api_response = requests.request("POST", ZabbixAPIURL, headers=headers, data = payload)
    return json.loads(zbx_api_response.text)

def createMaintenance(host):
    result = makeRequest("""
        {
        "jsonrpc": "2.0",
        "method": "maintenance.create",
        "params": {
            "name": "%s",
            "active_since": %s,
            "active_till": %s,
                    "hostids": [
                "%s"
            ],
             "timeperiods": [
                {
                    "timeperiod_type": 0,
                    "start_date": %s,
                    "period": %s
                }
            ]       
        },
        "auth": "%s",
        "id": 1
    }""" % (host.changeID + " " + host.hostName, host.von, host.bis, host.hostID, host.von, host.getDuration(), apiKey))
    try:
        error = result["error"]
        logger.LogError("Error while creating maintenance: %s" % (str(error)))
    except:
        logger.Log("Created maintenance for host %s(id: %s)" % (host.hostName, str(result["result"]["maintenanceids"][0])))

def convertTimeToUnix(time):
    return int((datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S") - datetime.datetime(1970,1,1)).total_seconds() - 7200)
    
apiKey = ""
logger = Logger(logPath)

logger.Log("Getting API key...")
apiKey = getApiKey()
#logger.Log("Api key: " + apiKey)

# get Hosts from csv file
firstLine = True
with open('SNOW_Maintenance.csv', newline='') as f:
  reader = csv.reader(f, )

  for row in reader:
    if firstLine:
        firstLine = False
        continue
    if row.__len__() > 0:
        zabbixHosts.append(ZabbixHost(row[0].lower(), row[1], convertTimeToUnix(row[2]), convertTimeToUnix(row[3]), getHostID(row[0])))

for host in zabbixHosts:
    if host.hostID is None:
        logger.LogError("Host " + host.hostName + " not found!")
    else:
        createMaintenance(host)
		