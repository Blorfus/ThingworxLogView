import http.client
import ssl
import json
import random
import time
import yaml
import argparse
from datetime import datetime
from datetime import timedelta

TWX_HOST=""
TWX_PORT=443
TWX_SECURE=True
TWX_AppKey=""
refreshRate=20  #The rate at which the data update routine runs in seconds.
testRun = False
previousTimespan=-30  #the number of minutes to query when starting up, must be negative
maxItems=100
logType = "Script"
#global firstRun

def callThingworxService(thingType, thingName, serviceName, content):
    if(TWX_SECURE):
        conn = http.client.HTTPSConnection(TWX_HOST, 443, context = ssl._create_unverified_context())
    else:
        conn = http.client.HTTPConnection(TWX_HOST, TWX_PORT)
    url = "/Thingworx/"+thingType+"/"+thingName+"/Services/"+serviceName
    conn.request('POST', url, content, {"Accept": "application/json", "appKey": TWX_AppKey, "Content-Type": "application/json"})
    
    r = conn.getresponse()
    responseStatus = r.status
    responseBody = r.read()

    if(responseStatus != 200):
        print("\x1b[91mERROR:\x1b[0mUnexpected HTTP code encountered["+str(responseStatus)+"] when requesting: "+url)
        

    return responseBody, responseStatus

def getLogs(type, startTime):
    global firstRun
    global lastRetrievalTime
    endDate = datetime.now()
    if(firstRun):
        print("First Run")
        startDate = endDate - timedelta(hours=0, minutes=30, seconds=0)
        firstRun=False
    else:
        startDate = startTime
    startDateStr=datetimeToISOStr(startDate +  timedelta(hours=4, minutes=0, seconds=0))
    endDateStr = datetimeToISOStr(endDate +  timedelta(hours=4, minutes=0, seconds=0))
    lastRetrievalTime=endDate
    jsonParamStr = "{ \"startDate\":\""+startDateStr+"\",\"endDate\":\""+endDateStr+"\",\"maxItems\":"+str(maxItems)+",\"fromLogLevel\":\"ALL\",\"instance\":\"\",\"origin\":\"\",\"searchExpression\":\".*.*\",\"thread\":\"\",\"toLogLevel\":\"ALL\",\"user\":\"\",\"isRegex\":true,\"oldestFirst\":true}"
    
    body, status =callThingworxService("Logs", type, "QueryLogEntries", jsonParamStr)

    #print("Got Status:"+str(status))
    #print("response:"+str(body))
    fullIT_dict = json.loads(body)
    rows = fullIT_dict["rows"]
    for row in rows:
        print(formatEntry(str(row["level"]), row["timestamp"], row["thread"], str(row["content"])))

def formatEntry(entryLevel, logTime, threadName, message):
    formattedOutput=""
    formattedOutput+=formatDate(logTime)
    formattedOutput+=" "
    formattedOutput+=formatThreadName(threadName)
    formattedOutput+=" "
    formattedOutput+=colorLogEntry(entryLevel)
    formattedOutput+=" "
    formattedOutput+=formatMessage(entryLevel, message)
    return formattedOutput

def colorLogEntry(entryLevel):
    match entryLevel:
        case "ERROR":
            return "\x1b[91mERROR:\x1b[0m"
        case "WARN":
            return "\x1b[93mWARN:\x1b[0m"
        case "INFO":
            return "\x1b[36mINFO:\x1b[0m"
        case "DEBUG":
            return "\x1b[32mDEBUG:\x1b[0m"
        case "TRACE":
            return "\x1b[37mTRACE:\x1b[0m"

def formatMessage(logLevel, message):
    match logLevel:
        case "ERROR":
            return "\033[38;2;255;255;255;48;2;64;0;0m"+message+"\x1b[0m"
        case "WARN":
            return "\033[38;2;200;200;200;48;2;69;69;12m"+message+"\x1b[0m"
        case "INFO":
            return "\x1b[36m"+message+"\x1b[0m"
        case "DEBUG":
            return "\x1b[32m"+message+"\x1b[0m"
        case "TRACE":
            return "\x1b[37m"+message+"\x1b[0m"
    

def formatDate(timestamp):
    dateObj = datetime.fromtimestamp(timestamp/1000)
    dateStr = dateObj.strftime(("%H:%M:%S.%f"))
    return "\033[38;2;0;200;0m"+dateStr+"\x1b[0m"

def formatThreadName(threadName):
    return "\033[38;2;100;100;100m["+threadName+"]\x1b[0m"

def datetimeToISOStr(dateStamp): #ex 2023-08-27T14:19:31.387Z\
    return dateStamp.strftime(("%Y-%m-%dT%H:%M:%S.%f%Z"))

     
def process_request():
    #print("Getting updates....")
    if logType == "Application":
        getLogs("ApplicationLog", lastRetrievalTime)
    elif logType == "Script":
        getLogs("ScriptLog", lastRetrievalTime)

    time.sleep(refreshRate)

def loadSettings(serverConfigName):
    global refreshRate
    global maxItems
    global TWX_HOST
    global TWX_PORT
    global TWX_SECURE
    global TWX_AppKey

    fstream = open("config.yaml",'r')
    config = yaml.safe_load(fstream.read())
    print(config)
    refreshRate = config["interval_s"]
    maxItems = config["maxItems"]
    #serverConfig = config["default"]
    TWX_HOST = config[serverConfigName]["host"]
    TWX_PORT = config[serverConfigName]["port"]
    TWX_SECURE = config[serverConfigName]["isSecure"]
    TWX_AppKey = config[serverConfigName]["appKey"]

def setup():
    global firstRun
    global lastRetrievalTime
    global logType
    parser = argparse.ArgumentParser(prog='Thingworx Log Viewer', description='Lets you view the thingworx logs from the command line in real time')
    parser.add_argument('LogType', help='The types of logs to display, Application OR Script', default="Script")
    parser.add_argument('Server', help='The name of your server configuration section in the config.yaml file', default="default")

    args = parser.parse_args()
    logType = args.LogType

    loadSettings(args.Server)
    
    lastRetrievalTime=datetime.now()
    firstRun=True



if __name__ == '__main__':
    setup()
    while True:
        process_request()