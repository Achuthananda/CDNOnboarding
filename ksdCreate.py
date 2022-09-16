from akamaihttp import AkamaiHTTPHandler
import os
import argparse
import json
import requests
from akamai.edgegrid import EdgeGridAuth, EdgeRc
from urllib.parse import urljoin
import sys


edgercLocation = '~/.edgerc'
edgercLocation = os.path.expanduser(edgercLocation)
akhttp = AkamaiHTTPHandler(edgercLocation,'appsec')

def listConfigs(accountSwitchKey):
    listep = '/appsec/v1/configs'
    #headers = {}
    params = {}
    if accountSwitchKey:
        params['accountSwitchKey'] = accountSwitchKey

    result = akhttp.getResult(listep,headers=None,params=params)
    if result[0] == 200:
        print(json.dumps(result[1],indent=2))

def createConfig(accountSwitchKey,configName,contractId,groupId):
    try:
        createConfigEP = '/appsec/v1/configs'
        params = {}
        if accountSwitchKey:
            params['accountSwitchKey'] = accountSwitchKey
        
        
        headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }
        payload = {
            "name": configName,
            "description": "Test",
            "contractId": contractId,
            "groupId": groupId,
            "hostnames": [
                "dbarban.www.akamaiflowershop.com"
            ]
        }
        datajson = json.dumps(payload,indent=2)

        status,createAppSecConfigJson = akhttp.postResult(createConfigEP,datajson,headers,params)
        if status == 201:
            #print(createEnrollmentJson)
            configId = createAppSecConfigJson['configId']
            print('Successfully created the App Sec Config and Config Id is {}'.format(configId))
            return configId
        else:
            print(status)
            print("Failed to create the App Sec Config")
            return 0
    except Exception as e:
        print('{}:Error create the App Sec Config'.format(e),file=sys.stderr)
        return 0

    return configId

def renameConfig(accountSwitchKey,configId,configName,description):
    try:
        renameEP = '/appsec/v1/configs/{configId}'.format(configId)
        params = {}
        if accountSwitchKey:
            params['accountSwitchKey'] = accountSwitchKey
        
        rename_payload = {
            "description": description,
            "name": configName
        }
        headers = {}
        datajson = json.dumps(rename_payload,indent=2)
        status,createAppSecConfigJson = akhttp.putResult(createConfigEP,datajson,headers,params)
        if status == 200:
            print('Successfully renamed the App Sec Config to {} and Config Id is {}'.format(configName,configId))
            return True
        else:
            print("Failed to rename the App Sec Config")
            return False
    except Exception as e:
        print('{}:Error renaming the App Sec Config'.format(e),file=sys.stderr)
        return False


def createSecurityPolicy(accountSwitchKey,configId,version,securityPolicyName):
    try:
        createSPEP = '/appsec/v1/configs/{}/versions/{}/security-policies'.format(configId,version)
        params = {}
        if accountSwitchKey:
            params['accountSwitchKey'] = accountSwitchKey
        
        
        headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }
        payload = {
            "policyName": securityPolicyName,
            "policyPrefix": "bt17"
        }

        datajson = json.dumps(payload,indent=2)

        status,createAppSecPolicyJson = akhttp.postResult(createSPEP,datajson,headers,params)
        if status == 200:
            #print(createEnrollmentJson)
            policyId = createAppSecPolicyJson['policyId']
            print('Successfully created the App Sec Policy {} and  Id is {}'.format(securityPolicyName,policyId))
            return policyId
        else:
            print(status)
            print("Failed to create the App Sec Policy")
            return 0
    except Exception as e:
        print('{}:Error create the App Sec Policy'.format(e),file=sys.stderr)
        return 0

    return configId


def createAppSecConfig(accountSwitchKey,name,contractId,groupId,securityPolicyName):
    #Create a new Configuration
    #Rename the Configuration
    try:
        configId = createConfig(accountSwitchKey,name,contractId,groupId)
        createSecurityPolicy(accountSwitchKey,configId,1,securityPolicyName)


    except Exception as e:
        print('{}:Error Creating the Enrollment'.format(e),file=sys.stderr)
        exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Times CDN Onboarding Tool.')
    # Storage migration
    parser.add_argument('--accountSwitchKey', help='Account SwitchKey')
    parser.add_argument('--name', help='Name of the AppSec Config')
    parser.add_argument('--contractId', help='ContractID')
    parser.add_argument('--groupId', help='groupId')
    parser.add_argument('--securityPolicyName', help='securityPolicyName')
    #parser.add_argument('--file', help='File having the Cert Details')
    
    args = parser.parse_args()
    createAppSecConfig(args.accountSwitchKey,args.name,args.contractId,args.groupId,args.securityPolicyName)
   
'''
python ksdCreate.py --accountSwitchKey 1-6JHGX --name TestAchuthApi21 --groupId 19293 --contractId 1-1NC95D --securityPolicyName FirstPolicy
Akamai Professional Services
'''


