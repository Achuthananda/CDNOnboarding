from ..common.akamaihttp import AkamaiHTTPHandler
import os
import argparse
import json
import requests
from ..common.commonutilities import print_log,getProductId,getEmailNotificationList
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
    #parser.add_argument('--certEnrollmentId', required=True,help='Certificate Enrollment Id')
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
    else:
        print_log("Creating the config")
        propertyId = createNewConfig(args.accountSwitchKey,args.newPropertyName,args.contractId,args.groupId)
        if propertyId != 0:
            print('Succesfully Created the config and property Id is {}.'.format(propertyId),file=sys.stderr)
            '''addstatus = addHostnameCPCode(args.accountSwitchKey,args.contractId,args.groupId,args.newPropertyName,args.certEnrollmentId)
            if addstatus == True:
                print_log("Succesfully Activated the Cofig to Staging Network\n")
            else:
                print_log("Failed to Activate the Cofig to Staging Network\n")'''
    

'''

python cloneConfig.py --clone False --logfile configlog --accountSwitchKey 1-6JHGX --contractId ctr_1-1NC95D --groupId grp_223702 --newPropertyName TimesTemplate
python cloneConfig.py --clone True --logfile cloneconfiglog --accountSwitchKey 1-6JHGX --contractId ctr_1-1NC95D --groupId grp_223702 --propertyId prp_838658 --version 1 --newPropertyName TimesCloneConfig

Akamai Professional Services


python cloneproperty.py --clone False --accountSwitchKey B-3-16OEUPX  --contractId ctr_3-16TWBVX --groupId grp_173720 --newPropertyName "salamanca"


'''


