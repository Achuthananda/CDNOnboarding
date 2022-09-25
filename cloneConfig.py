from akamaihttp import AkamaiHTTPHandler
import os
import argparse
import json
import requests
from commonutilities import print_log


edgercLocation = '~/.edgerc'
edgercLocation = os.path.expanduser(edgercLocation)
akhttp = AkamaiHTTPHandler(edgercLocation,'papi')


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
            print_log('Failed to create the Clone the config and status code is {}.'.format(status))
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
            "copyHostnames": False,
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
        print_log('Successfully created the Config {}'.format(newpropetyId))
        return newpropetyId
    else:
        print('Failed to create the Clone the config and status code is {}.'.format(status),file=sys.stderr)
        return 0



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Times CDN Onboarding Tool.')

    parser.add_argument('--accountSwitchKey', default=None,help='Account SwitchKey')    
    parser.add_argument('--contractId', required=True,help='ContractID')
    parser.add_argument('--groupId', required=True,help='groupId')
    parser.add_argument('--propertyId', required=True,help='PropertyId')
    parser.add_argument('--version', required=True,help='Version')
    parser.add_argument('--newPropertyName',required=True, help='newPropertyName')
    parser.add_argument('--clone', default=True,help='Clone')
    parser.add_argument('--logfile', help='Log File Name')

    args = parser.parse_args()
    jobId = str(uuid.uuid1())
    logfilepath = ''

    curdir = os.getcwd()
    dirpath = os.path.dirname(curdir + '/logs')
    logfilepath = dirpath + "/"  + jobId+'.txt'

    if args.logfile:
        logfilepath = dirpath + "/" + args.logfile

    sys.stdout = open(logfilepath, 'w')

    if args.clone == True:
        cloneProperty(args.accountSwitchKey,args.contractId,args.groupId,args.propertyId,args.version,args.newPropertyName)
    else:
        createNewConfig(args.accountSwitchKey,args.newPropertyName,args.contractId,args.groupId)


    

'''

python cloneproperty.py --clone False --accountSwitchKey B-3-16OEUPX  --contractId ctr_3-16TWBVX --groupId grp_173720 --newPropertyName "salamanca"

python cloneproperty.py --clone True --accountSwitchKey B-3-16OEUPX  --contractId ctr_3-16TWBVX --groupId grp_173720 --propertyId prp_828730 --version 1 --newPropertyName "testnewproperty_acmp1234"

'''


