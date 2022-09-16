from akamaihttp import AkamaiHTTPHandler
import os
import argparse
import json
import requests
from akamai.edgegrid import EdgeGridAuth, EdgeRc
from urllib.parse import urljoin

edgerc = EdgeRc('/Users/apadmana/.edgerc')
section = 'papi'
baseurl = 'https://%s' % edgerc.get(section, 'host')
s = requests.Session()
s.auth = EdgeGridAuth.from_edgerc(edgerc, section)

edgercLocation = '~/.edgerc'
edgercLocation = os.path.expanduser(edgercLocation)
akhttp = AkamaiHTTPHandler(edgercLocation,'papi')


def createNewConfig(accountSwitchKey,propertyName,contractId,groupId):
    try:
        params = {}
        if accountSwitchKey:
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
            print(createConfigJson)
            newpropetyId = createConfigJson['propertyLink'].split('?')[0].split('/')[4].split('_')[1]
            print('Successfully created the Config {}'.format(newpropetyId))
            return newpropetyId
        else:
            print('Failed to create the Clone the config and status code is {}.'.format(status))
            return 0
    except:
        print('Failed to create the config and status code is {}.'.format(status))
        return 0


def cloneProperty(accountSwitchKey,contractId,groupId,propertyId,version,newPropertyName):
    version = int(version)
    params = {}
    if accountSwitchKey:
        params["accountSwitchKey"] = accountSwitchKey
    params["contractId"] = contractId
    params["groupId"] = groupId


    clone_payload = {
        "cloneFrom": {
            #"cloneFromVersionEtag": "27b4ec45918df9a918764c944043765576f7c9a1",
            "copyHostnames": False,
            "propertyId": propertyId,
            "version": version
        },
        "productId": "prd_Fresca",
        "propertyName": newPropertyName
    }

    clone_data = json.dumps(clone_payload)
    print(clone_data)
    print(params)

    cloneConfigEndPoint = '/papi/v1/properties/'
    headers = {
        "accept": "application/json",
        "PAPI-Use-Prefixes": "true",
        "content-type": "application/json"
    }

    status,createConfigJson = akhttp.postResult(cloneConfigEndPoint,clone_data,headers,params)
    if status == 201:
        print(createConfigJson)
        newpropetyId = createConfigJson['propertyLink'].split('?')[0].split('/')[4].split('_')[1]
        print('Successfully created the Config {}'.format(newpropetyId))
        return newpropetyId
    else:
        print('Failed to create the Clone the config and status code is {}.'.format(status))
        return 0



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Times CDN Onboarding Tool.')
    # Storage migration
    parser.add_argument('--accountSwitchKey', help='Account SwitchKey')
    parser.add_argument('--contractId', help='ContractID')
    parser.add_argument('--groupId', help='GroupId')
    parser.add_argument('--propertyId', help='PropertyId')
    parser.add_argument('--version', help='Version')
    parser.add_argument('--newPropertyName', help='newPropertyName')
    parser.add_argument('--clone', help='Clone')

    
    args = parser.parse_args()
    if args.clone == True:
        cloneProperty(args.accountSwitchKey,args.contractId,args.groupId,args.propertyId,args.version,args.newPropertyName)
    else:
        createNewConfig(args.accountSwitchKey,args.newPropertyName,args.contractId,args.groupId)


    

'''

python cloneproperty.py --clone False --accountSwitchKey B-3-16OEUPX  --contractId ctr_3-16TWBVX --groupId grp_173720 --newPropertyName "salamanca"

python cloneproperty.py --clone True --accountSwitchKey B-3-16OEUPX  --contractId ctr_3-16TWBVX --groupId grp_173720 --propertyId prp_828730 --version 1 --newPropertyName "testnewproperty_acmp1234"

'''


