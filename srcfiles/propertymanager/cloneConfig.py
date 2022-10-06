from ..common.akamaihttp import AkamaiHTTPHandler
import os
import argparse
import json
import requests
from ..common.commonutilities import print_log,getProductId,getEmailNotificationList
from ..ehn.ehnUtility import createEdgeHostName
from ..cpcode.cpCodeUtility import createCPCode
import uuid
import sys
from akamaiproperty import AkamaiProperty
import random
import string

import configparser

settingsconfig = configparser.ConfigParser()
settingsconfig.read('config.ini')
edgercLocation = settingsconfig['Edgerc']['location']
edgercLocation = os.path.expanduser(edgercLocation)
akhttp = AkamaiHTTPHandler(edgercLocation,settingsconfig['Edgerc']['section'])
emailList = settingsconfig['Common']['emailnotification']
emailArray = emailList.split(',')


def addHostNametoConfig(akConfig,newVersion,hostname,edgeHostName):
    addhostnameStatus = akConfig.addHostname(newVersion,hostname,edgeHostName)
    print_log("Status of adding the hostname {} to config is {}".format(hostname,addhostnameStatus))
    return addhostnameStatus

def addOriginCPCodetoConfig(akConfig,newVersion,hostname,contentProviderCode,originHostName):
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
    #print_log(propruleInfo_json)
    
    addOriginstatus = akConfig.updateRuleTree(newVersion,propruleInfo_json)
    print_log("Status of adding the Origin {} to hostname {} is {}".format(originHostName,hostname,addOriginstatus))
    return addOriginstatus



def createNewConfig(accountSwitchKey,propertyName,contractId,groupId):
    try:
        params = {}
        if accountSwitchKey != None:
            params["accountSwitchKey"] = accountSwitchKey
        params["contractId"] = contractId
        params["groupId"] = groupId

        create_data={"productId": 'prd_Fresca',"propertyName": propertyName}
        create_data = json.dumps(create_data)


        createConfigEndPoint = '/papi/v1/properties/'
        headers = {
            "accept": "application/json",
            "PAPI-Use-Prefixes": "true",
            "content-type": "application/json"
        }

        status,createConfigJson = akhttp.postResult(createConfigEndPoint,create_data,headers,params)
        if status == 201:
            print_log(createConfigJson)
            newpropetyId = createConfigJson['propertyLink'].split('?')[0].split('/')[4].split('_')[1]
            print_log('Successfully created the Config {}'.format(newpropetyId))
            return newpropetyId
        else:
            print_log('Failed to create the config and status code is {}.'.format(status))
            print('Failed to create the config and status code is {}.'.format(status),file=sys.stderr)
            return 0
    except:
        print('Failed to create the config and status code is {}.'.format(status),file=sys.stderr)
        return 0

def cloneProperty(accountSwitchKey,contractId,groupId,propertyId,version,newPropertyName):
    version = int(version)
    params = {}
    if accountSwitchKey != None:
        params["accountSwitchKey"] = accountSwitchKey
    params["contractId"] = contractId
    params["groupId"] = groupId


    clone_payload = {
        "cloneFrom": {
            #"cloneFromVersionEtag": "27b4ec45918df9a918764c944043765576f7c9a1",
            "copyHostnames": True,
            "propertyId": propertyId,
            "version": version
        },
        "productId": "prd_Fresca",
        "propertyName": newPropertyName
    }

    clone_data = json.dumps(clone_payload)
    print_log(clone_data)
    print_log(params)

    cloneConfigEndPoint = '/papi/v1/properties/'
    headers = {
        "accept": "application/json",
        "PAPI-Use-Prefixes": "true",
        "content-type": "application/json"
    }

    status,createConfigJson = akhttp.postResult(cloneConfigEndPoint,clone_data,headers,params)
    if status == 201:
        print_log(createConfigJson)
        newpropetyId = createConfigJson['propertyLink'].split('?')[0].split('/')[4].split('_')[1]
        print_log('Successfully Cloned the Config {}'.format(newpropetyId))
        return newpropetyId
    else:
        print('Failed to  Clone the config and status code is {}.'.format(status),file=sys.stderr)
        return 0



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Times CDN Onboarding Tool.')

    parser.add_argument('--accountSwitchKey', default=None,help='Account SwitchKey')    
    parser.add_argument('--contractId', required=True,help='ContractID')
    parser.add_argument('--groupId', required=True,help='groupId')
    parser.add_argument('--propertyId', required=False,help='PropertyId')
    parser.add_argument('--version', required=False,help='Version')
    parser.add_argument('--newPropertyName',required=False, help='newPropertyName')
    parser.add_argument('--clone', default=True,help='Clone')
    parser.add_argument('--certEnrollmentId', required=True,help='Certificate Enrollment Id')
    parser.add_argument('--hostName', required=True,help='Hostname to Onboard')
    parser.add_argument('--originHostname', required=True,help='Origin Hostname to Onboard')
    parser.add_argument('--logfile', help='Log File Name')


    args = parser.parse_args()
    jobId = str(uuid.uuid1())
    logfilepath = ''

    curdir = os.getcwd()
    dirpath = os.path.dirname(curdir + '/logs')
    logfilepath = dirpath + "/"  + jobId+'.txt'

    if args.logfile:
        logfilepath = dirpath + "/logs/" + args.logfile

    sys.stdout = open(logfilepath, 'w+')


    if args.clone == 'True':
        print_log('Cloning the config')
        propertyId = cloneProperty(args.accountSwitchKey,args.contractId,args.groupId,args.propertyId,args.version,args.newPropertyName)
        if propertyId != 0:
            print('Succesfully Cloned the config and property Id is {}.'.format(propertyId),file=sys.stderr)

            ehn = createEdgeHostName(args.contractId,args.groupId,args.hostName,args.certEnrollmentId,args.accountSwitchKey)
            cpCode = createCPCode(args.contractId,args.groupId,args.hostName,args.accountSwitchKey)
            akConfig = AkamaiProperty(edgercLocation,args.newPropertyName, args.accountSwitchKey)
            print_log(ehn)
            print_log(cpCode)
            if ehn != '' and cpCode != 0:
                hostnameAdditionStatus = addHostNametoConfig(akConfig,1,args.hostName,ehn)
                originAddition = addOriginCPCodetoConfig(akConfig,1,args.hostName,int(cpCode),args.originHostname)
                if originAddition == True:
                    versionStatus = akConfig.addVersionNotes(1,"Adding {}".format(args.hostName))
                    activationStatus = False
                    if versionStatus:
                        activationStatus = akConfig.activateStaging(1,"Adding {}".format(args.hostName),emailArray)
                    print_log("Update Status :{}".format(originAddition))
                    print_log("Version Status:{}".format(versionStatus))
                    print_log("Activation Status:{}".format(activationStatus))
                    print_log('*'*80)

                    if activationStatus == True:
                        print_log("Succesfully Started Activation the Config to Staging Network\n")
                    else:
                        print_log("Failed to Activate the Config to Staging Network\n")

    else:
        print_log("Creating the config")
        propertyId = createNewConfig(args.accountSwitchKey,args.newPropertyName,args.contractId,args.groupId)
        if propertyId != 0:
            print('Succesfully Created the config and property Id is {}.'.format(propertyId),file=sys.stderr)
        else:
            print('Failed to Create the config and property Id is {}.'.format(propertyId),file=sys.stderr)
    

'''

python -m srcfiles.propertymanager.cloneConfig --clone False --logfile configlog --accountSwitchKey 1-6JHGX --contractId ctr_1-1NC95D --groupId grp_223702 --newPropertyName GotTemplate6 --hostName cerseilannister.iamacmp.com --certEnrollmentId 159501

python -m srcfiles.propertymanager.cloneConfig --clone True --logfile configlog --accountSwitchKey 1-6JHGX --contractId ctr_1-1NC95D --groupId grp_223702 --propertyId prp_838658 --version 1 --newPropertyName GotTemplate16 --hostName varys.iamacmp.com --certEnrollmentId 159511 --originHostname timesofindia.indiatimes.com



python cloneConfig.py --clone True --logfile cloneconfiglog --accountSwitchKey 1-6JHGX --contractId ctr_1-1NC95D --groupId grp_223702 --propertyId prp_838658 --version 1 --newPropertyName TimesCloneConfig

Akamai Professional Services


python cloneproperty.py --clone False --accountSwitchKey B-3-16OEUPX  --contractId ctr_3-16TWBVX --groupId grp_173720 --newPropertyName "salamanca"


'''


