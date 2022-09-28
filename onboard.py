# Import required modules
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import argparse
import datetime
import time
import uuid
from tqdm import tqdm
import sys,os
from srcfiles.cpcode.cpCodeUtility import createCPCode
from srcfiles.ehn.ehnUtility import createEdgeHostName
from srcfiles.cps.cpsUtility import addSANtoCert,getDVChallenges,updateGodaddyDomain
from srcfiles.common.akamaihttp import AkamaiHTTPHandler
from srcfiles.common.commonutilities import print_log,readCommonSettings,getEmailNotificationList
from srcfiles.propertymanager.akamaiproperty import AkamaiProperty
from srcfiles.ksd.ksdUtility import addHostnametoSecConfig,createNewSecConfigVersion,activateStagingAppSecConfig
import configparser

settingsconfig = configparser.ConfigParser()
settingsconfig.read('config.ini')
edgercLocation = settingsconfig['Edgerc']['location']
edgercLocation = os.path.expanduser(edgercLocation)
akhttp = AkamaiHTTPHandler(edgercLocation,settingsconfig['Edgerc']['section'])


jobId = str(uuid.uuid1())
logfilepath = ''



scope = ["https://spreadsheets.google.com/feeds", 
        'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", 
         "https://www.googleapis.com/auth/drive"]
 
 
# Assign credentials ann path of style sheet
creds = ServiceAccountCredentials.from_json_keyfile_name(settingsconfig['Sheet']['creds_location'], scope)
client = gspread.authorize(creds)

sheet = client.open(settingsconfig['Sheet']['Name'])


def addHostNametoConfig(akConfig,newVersion,hostname,edgeHostName,config,udpateStatus):
    addhostnameStatus = akConfig.addHostname(newVersion,hostname,edgeHostName)
    print_log("Status of adding the hostname {} to config {} is {}".format(hostname,config,addhostnameStatus))
    udpateStatus = udpateStatus and addhostnameStatus
    return udpateStatus

def addOriginCPCodetoConfig(akConfig,newVersion,hostname,contentProviderCode,originHostName,config,udpateStatus):
    origin_data = ''
    with open('srcfiles/propertymanager/origin.json') as json_file:
        origin_data = json.load(json_file)
    
    new_origin_data = {}
    new_origin_data = origin_data.copy()
    new_origin_data['name'] = hostname
    new_origin_data['behaviors'][0]['options']['hostname'] = originHostName
    new_origin_data['behaviors'][1]['options']["value"]['id'] = contentProviderCode
    new_origin_data['behaviors'][1]['options']["value"]['description'] = hostname
    new_origin_data['behaviors'][1]['options']["value"]['name'] = hostname

    new_origin_data['criteria'][0]['options']['values'][0] = hostname

    ruleTree = akConfig.getRuleTree(newVersion)
    for children in ruleTree['rules']['children']:
        if children['name'] == 'Static Origins':
            children['children'].insert(len(children['children']),new_origin_data) 

    propruleInfo_json = json.dumps(ruleTree,indent=2)
    print_log(propruleInfo_json)
    
    addOriginstatus = akConfig.updateRuleTree(newVersion,propruleInfo_json)
    print_log("Status of adding the Origin {} to hostname {} is {}".format(originHostName,hostname,addOriginstatus))
    udpateStatus = udpateStatus and addOriginstatus
    return udpateStatus


def main(sheetName,startRow,endRow,changeID,addHostnameAppSec,accountSwitchKey=None):
    startRow = int(startRow)
    endRow = int(endRow)
    if startRow <= 0 or endRow <=0 or startRow > endRow:
        print("Invalid Values for startRow or endRow. Please try again!",file=sys.stderr)
        exit(1)
    try:
        sheet_instance = sheet.worksheet(sheetName)
    except:
        print("Wrong SheetName.Please Provide the correct sheet name and try again!",file=sys.stderr)
        exit(2)


    startRow = startRow-2
    endRow = endRow-2

    #Read Common Settings
    readCommonSettings(sheet)
    data = sheet_instance.get_all_records()
    #print(json.dumps(data,indent=2))
    
    def udpateprogressbar():
        progress_bar.update()

    certtoHostnameDict = {}
    hostnametoPropertyDict = {}
    hostnametoRowId = {}
    hostnametoSecurityConfig = {}
    missedconfigs = []

    for i in range(startRow,endRow+1):
        hostnametoRowId[data[i]['Hostname']] = i

    progress_bar = tqdm(total=endRow-startRow+1)
    for i in range(startRow,endRow+1):
        if data[i]['Edgehostname'] == '':
            edgeHostName = createEdgeHostName(data[i]['ContractId'],data[i]['GroupId'],data[i]['Hostname'],data[i]['CertEnrollmentId'],akhttp,accountSwitchKey)
            if edgeHostName != '':
                sheet_instance.update_cell(i+2, 11,edgeHostName) #Update the CP Code 
        else:
            print_log("EHN already present in the sheet !So skipping creating the EHN")
            print("EHN already present in the sheet !So skipping creating the EHN",file=sys.stderr)
        udpateprogressbar()
        print_log('*'*80)

    data = sheet_instance.get_all_records()
    progress_bar = tqdm(total=endRow-startRow+1)
    for i in range(startRow,endRow+1):
        if data[i]['CPCode'] == '':
            cpCode = createCPCode(data[i]['ContractId'],data[i]['GroupId'],data[i]['Hostname'],akhttp,accountSwitchKey)
            if cpCode != 0:
                sheet_instance.update_cell(i+2, 10,cpCode) #Update the CP Code 
        else:
            print_log("CPCode already present in the sheet !So skipping creating the CP Code")
            print("CPCode already present in the sheet !So skipping creating the CP Code",file=sys.stderr)

        udpateprogressbar()
        print_log('*'*80)

    data = sheet_instance.get_all_records()
    print_log("Just before updating the certhostnamedetails")
    for i in range(startRow,endRow+1):
        print_log(data[i])
        #Populating the SAN Addition Dict
        if data[i]['SAN Addition'] == '':
            if data[i]['CertEnrollmentId'] not in certtoHostnameDict:
                certtoHostnameDict[data[i]['CertEnrollmentId']] = [data[i]['Hostname']]
            else:
                certtoHostnameDict[data[i]['CertEnrollmentId']].append(data[i]['Hostname'])

        #Populating the ConfigtoHostnameDict
        if data[i]['Staging Activation'] != 'TRUE':
            if data[i]['Config'] not in hostnametoPropertyDict:
                hostnametoPropertyDict[data[i]['Config']] = [data[i]['Hostname']]
            else:
                hostnametoPropertyDict[data[i]['Config']].append(data[i]['Hostname'])

        #Populating the SAN Addition Dict
        if data[i]['SecurityConfigAddition'] == '':
            if data[i]['Security Config'] not in hostnametoSecurityConfig:
                hostnametoSecurityConfig[data[i]['Security Config']] = [data[i]['Hostname']]
            else:
                hostnametoSecurityConfig[data[i]['Security Config']].append(data[i]['Hostname'])
        
    
    print_log(hostnametoPropertyDict)
    print_log(certtoHostnameDict)
    print_log(hostnametoSecurityConfig)

    data = sheet_instance.get_all_records()
    for enrollmentID in certtoHostnameDict:
        addStatus = addSANtoCert(enrollmentID,certtoHostnameDict[enrollmentID],akhttp,accountSwitchKey)
        for i in range(startRow,endRow+1):
            if data[i]['Hostname'] in certtoHostnameDict[enrollmentID]:
                sheet_instance.update_cell(i+2, 12,addStatus) #Update the SAN Addition 

    for enrollmentID in certtoHostnameDict:
        dnsrecordsDict = getDVChallenges(akhttp,enrollmentID,accountSwitchKey)
        print(json.dumps(dnsrecordsDict,indent=2),file=sys.stderr)
        for record in dnsrecordsDict:
            udpaterecordstatus = updateGodaddyDomain(record,dnsrecordsDict[record])
            print_log("The status of adding record {} to DNSZone is {}".format(record,udpaterecordstatus))
            print("The status of adding record {} to DNSZone is {}".format(record,udpaterecordstatus),file=sys.stderr)

    #Add the Hostnames to the Config:

    for config in hostnametoPropertyDict.keys():
        akConfig = AkamaiProperty(edgercLocation,config,accountSwitchKey)
        newVersion = akConfig.createVersion(akConfig.getVersionofConfig())
        print_log(newVersion)

        #Addition of HostName
        udpateStatus = True
        hostnameIndicesforMarking = []

        for hostname in hostnametoPropertyDict[config]:
            contentProviderCode = data[hostnametoRowId[hostname]]['CPCode']
            edgeHostName = data[hostnametoRowId[hostname]]['Edgehostname']
            originHostName = data[hostnametoRowId[hostname]]['OriginHostName']

            hostnameIndicesforMarking.append(hostnametoRowId[hostname])

            print()
            print_log(hostname)
            print_log(edgeHostName)
            print_log(contentProviderCode)
            print_log(originHostName)

            udpateStatus = addHostNametoConfig(akConfig,newVersion,hostname,edgeHostName,config,udpateStatus)
            udpateStatus = addOriginCPCodetoConfig(akConfig,newVersion,hostname,contentProviderCode,originHostName,config,udpateStatus)

        emailList = getEmailNotificationList()
        print_log(emailList)

        versionStatus = akConfig.addVersionNotes(newVersion,changeID)
        if udpateStatus == False:
            missedconfigs.append(config)
        activationStatus = False
        if udpateStatus and versionStatus:
            activationStatus = akConfig.activateStaging(newVersion,changeID,emailList)
        print_log("Update Status :{}".format(udpateStatus))
        print_log("Version Status:{}".format(versionStatus))
        print_log("Activation Status:{}".format(activationStatus))
        print_log('*'*80)

        for index in hostnameIndicesforMarking:
            sheet_instance.update_cell(index+2, 13,activationStatus) #Update the SAN Addition


    #Update all the Hostnames to the Security Config        
    if addHostnameAppSec == 'True':
        for securityConfigId in hostnametoSecurityConfig:
            version = createNewSecConfigVersion(securityConfigId,akhttp,accountSwitchKey)
            addSecConfigStatus = addHostnametoSecConfig(securityConfigId,version,hostnametoSecurityConfig[securityConfigId],akhttp,accountSwitchKey)
            if addSecConfigStatus == True:
                '''stagingActivateStatus = activateStagingAppSecConfig(securityConfigId,version,akhttp,accountSwitchKey)
                finalsecStatus = addSecConfigStatus & stagingActivateStatus'''
                for i in range(startRow,endRow+1):
                    if data[i]['Hostname'] in hostnametoSecurityConfig[securityConfigId]:
                        sheet_instance.update_cell(i+2, 14,finalsecStatus) #Update the Hostname Addition to Security Config
            else:
                for i in range(startRow,endRow+1):
                    if data[i]['Hostname'] in hostnametoSecurityConfig[securityConfigId]:
                        sheet_instance.update_cell(i+2, 14,addSecConfigStatus) #Update the Hostname Addition to Security Config




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Times CDN Onboarding Tool.')
    # Storage migration
    parser.add_argument('--sheet', required=True, help='Sheet Name')
    parser.add_argument('--start', required=True, help='Starting Row Number')
    parser.add_argument('--end', required=True, help='End Row')
    parser.add_argument('--accountSwitchKey', default=None,help='Account SwitchKey')
    parser.add_argument('--ChangeID',required=True, help='ChangeID')
    parser.add_argument('--logfile', help='Log File Name')
    parser.add_argument('--addHostnameAppSec',default='False',help='Log File Name')

    args = parser.parse_args()


    curdir = os.getcwd()
    dirpath = os.path.dirname(curdir + '/logs')
    logfilepath = dirpath + "/"  + jobId+'.txt'

    if args.logfile:
        logfilepath = dirpath + "/logs/" + args.logfile

    sys.stdout = open(logfilepath, 'w+')

    main(args.sheet,args.start,args.end,args.ChangeID,args.addHostnameAppSec,args.accountSwitchKey)

'''
python onboard.py --sheet 'First Batch' --start 3 --end 3 --accountSwitchKey 1-6JHGX --ChangeID 'TimesPOCDemo1: Third Batch Hostnames Addition' --logfile onboard.txt --addHostnameAppSec False
python onboard.py --sheet 'First Batch' --start 3 --end 3 --accountSwitchKey 1-6JHGX --ChangeID 'TimesPOCDemo1: Third Batch Hostnames Addition' --logfile onboard.txt --addHostnameAppSec True

'''
