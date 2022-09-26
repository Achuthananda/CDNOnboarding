from akamaihttp import AkamaiHTTPHandler
import os
import argparse
import json
import requests
from commonutilities import print_log,getProductId,getEmailNotificationList
import uuid
import sys
from akamaiproperty import AkamaiProperty
import random
import string


edgercLocation = '~/.edgerc'
edgercLocation = os.path.expanduser(edgercLocation)
akhttp = AkamaiHTTPHandler(edgercLocation,'appsec')


'''def createEdgeHostName(accountSwitchKey,contractId,groupId,hostname,certEnrollmentId):
    try:
        params = {}
        if accountSwitchKey != None:
            params["accountSwitchKey"] = accountSwitchKey
        params["contractId"] = contractId
        params["groupId"] = groupId

        
        create_hostname = {
            "productId": 'prd_Fresca',
            "domainPrefix": hostname,
            "domainSuffix": 'edgesuite.net',
            "secureNetwork": 'STANDARD_TLS',
            "ipVersionBehavior": 'IPV6_COMPLIANCE',
            "certEnrollmentId": certEnrollmentId
        }

        hostname_data = json.dumps(create_hostname)
        headers = {'Content-Type': 'application/json'}
        ehn = hostname + '.' + 'edgesuite.net'
        #print_log(hostname_data)
        #print_log(headers)

        createEHNEndPoint = '/papi/v1/edgehostnames'
        status,createEHNJson = akhttp.postResult(createEHNEndPoint,hostname_data,headers,params)
        if status == 201:
            print_log(createEHNJson)
            print_log('Successfully created the Edgehostname {} for {}'.format(ehn,hostname))
            return ehn
        else:
            print_log('Failed to create the Edgehostname for {} and status code is {}.'.format(hostname,status))
            return ''
    except Exception as e:
        print('{}:Error Creating the Edgehostname for {}'.format(e,hostname),file=sys.stderr)
        print_log('{}:Error Creating the Edgehostname for {}'.format(e,hostname))
        exit(3)

def addHostNametoConfig(akConfig,newVersion,hostname,edgeHostName,config,udpateStatus):
    addhostnameStatus = akConfig.addHostname(newVersion,hostname,edgeHostName)
    print_log("Status of adding the hostname {} to config {} is {}".format(hostname,config,addhostnameStatus))
    udpateStatus = udpateStatus and addhostnameStatus
    return udpateStatus'''

'''def addOriginCPCodetoConfig(akConfig,newVersion,hostname,contentProviderCode,originHostName,config,udpateStatus):
    origin_data = ''
    with open('origin.json') as json_file:
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
    udpateStatus = udpateStatus and addOriginstatus
    return udpateStatus'''

'''def createCPCode(accountSwitchKey,contractId,groupId,cpCodeName):
    try:
        params = {}
        if accountSwitchKey != None:
            params["accountSwitchKey"] = accountSwitchKey
        params["contractId"] = contractId
        params["groupId"] = groupId


        create_cpcode = {
            "productId": 'prd_Fresca',
            "cpcodeName": cpCodeName
        }

        cpcode_data = json.dumps(create_cpcode)

        createCPCodeEndPoint = '/papi/v1/cpcodes'
        headers = {'Content-Type': 'application/json'}#,
                   #'PAPI-Use-Prefixes': True}

        print_log(cpcode_data)
        print_log(headers)

        status,createCPCodeJson = akhttp.postResult(createCPCodeEndPoint,cpcode_data,headers,params)
        if status == 201:
            print_log(createCPCodeJson)
            cpCode = createCPCodeJson['cpcodeLink'].split('?')[0].split('/')[4].split('_')[1]
            print_log('Successfully created the CP Code {} for {}'.format(cpCode,cpCodeName))
            return cpCode
        else:
            print_log('Failed to create the CP Code for {} and status code is {}.'.format(cpCodeName,status))
            return 0
    except Exception as e:
        print('{}:Error Creating the CP Code for {}'.format(e,cpCodeName),file=sys.stderr)
        print_log('{}:Error Creating the CP Code for {}'.format(e,cpCodeName))
        exit(3)'''



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


'''def addHostnameCPCode(accountSwitchKey,contractId,groupId,configName,certEnrollmentId):
    if accountSwitchKey != None:
        akConfig = AkamaiProperty(edgercLocation,configName,accountSwitchKey)
    else:
        akConfig = AkamaiProperty(edgercLocation,configName)

    newVersion = 1

    #Addition of HostName
    udpateStatus = True

    letters = string.ascii_letters
    policyPrefix = "".join(random.sample(letters,4))
    hostnameprefix = 'times' +policyPrefix


    edgeHostName = createEdgeHostName(accountSwitchKey,contractId,groupId,hostnameprefix,certEnrollmentId)

    hostname = 'jimmy.iamacmp.com'

    contentProviderCode = createCPCode(accountSwitchKey,contractId,groupId,hostname)
    originHostName = 'www.timesofindia.com'


    print_log(hostname)
    print_log(edgeHostName)
    print_log(contentProviderCode)
    print_log(originHostName)

    udpateStatus = True
    udpateStatus = addHostNametoConfig(akConfig,newVersion,hostname,edgeHostName,configName,udpateStatus)
    print_log('Update Status of the config is {}'.format(udpateStatus))
    udpateStatus = addOriginCPCodetoConfig(akConfig,newVersion,hostname,contentProviderCode,originHostName,configName,udpateStatus)
    print_log('Update Status of the config is {}'.format(udpateStatus))

    emailList = ['apadmana@akamai.com']
    print_log(emailList)
    if udpateStatus == True:
        versionStatus = akConfig.addVersionNotes(newVersion,"Pilot Version")
        print_log('Update Version Status of the config is {}'.format(versionStatus))
        activationStatus = False
        if udpateStatus and versionStatus:
            activationStatus = akConfig.activateStaging(newVersion,"Pilot Version",emailList)
            print_log('Activation Status of the config is {}'.format(activationStatus))
            return activationStatus
        else:
            print_log('Update Version Status of the config is {}'.format(versionStatus))
            return False
    else:
        return False'''



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

    if args.clone == True:
        cloneProperty(args.accountSwitchKey,args.contractId,args.groupId,args.propertyId,args.version,args.newPropertyName)
    else:
        propertyId = createNewConfig(args.accountSwitchKey,args.newPropertyName,args.contractId,args.groupId)
        if propertyId != 0:
            print('Succesfully Created the config and property Id is {}.'.format(propertyId),file=sys.stderr)
            '''addstatus = addHostnameCPCode(args.accountSwitchKey,args.contractId,args.groupId,args.newPropertyName,args.certEnrollmentId)
            if addstatus == True:
                print_log("Succesfully Activated the Cofig to Staging Network\n")
            else:
                print_log("Failed to Activate the Cofig to Staging Network\n")'''

    

'''

python cloneConfig.py --clone False --logfile configlog --accountSwitchKey 1-6JHGX --contractId ctr_1-1NC95D --groupId grp_223702 --newPropertyName salamanca9 --certEnrollmentId 158484
Akamai Professional Services


python cloneproperty.py --clone False --accountSwitchKey B-3-16OEUPX  --contractId ctr_3-16TWBVX --groupId grp_173720 --newPropertyName "salamanca"

python cloneproperty.py --clone True --accountSwitchKey B-3-16OEUPX  --contractId ctr_3-16TWBVX --groupId grp_173720 --propertyId prp_828730 --version 1 --newPropertyName "testnewproperty_acmp1234"

'''


