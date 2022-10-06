from ..common.commonutilities import print_log
from ..common.akamaihttp import AkamaiHTTPHandler
import json
import sys

import configparser
import os

settingsconfig = configparser.ConfigParser()
settingsconfig.read('config.ini')
edgercLocation = settingsconfig['Edgerc']['location']
edgercLocation = os.path.expanduser(edgercLocation)
akhttp = AkamaiHTTPHandler(edgercLocation,settingsconfig['Edgerc']['section'])



def createEdgeHostName(contractId,groupId,hostName,certEnrollmentId,accountSwitchKey=None):
    try:
        params = {}
        if accountSwitchKey != None:
            params["accountSwitchKey"] = accountSwitchKey
        params["contractId"] = contractId
        params["groupId"] = groupId

        
        create_hostname = {
            "productId": settingsconfig['Common']['product_id'],
            "domainPrefix": hostName,
            "domainSuffix": settingsconfig['Common']['ehn_domain_suffix'],
            "secureNetwork": settingsconfig['Common']['network'],
            "ipVersionBehavior": settingsconfig['Common']['ipversion'],
            "certEnrollmentId": certEnrollmentId
        }

        hostname_data = json.dumps(create_hostname)
        headers = {'Content-Type': 'application/json'}
        ehn = hostName + '.' + settingsconfig['Common']['ehn_domain_suffix']
        #print_log(hostname_data)
        #print_log(headers)

        createEHNEndPoint = '/papi/v1/edgehostnames'
        status,createEHNJson = akhttp.postResult(createEHNEndPoint,hostname_data,headers,params)
        if status == 201:
            print('Successfully created the Edgehostname {} for {}'.format(ehn,hostName),file=sys.stderr)
            print_log('Successfully created the Edgehostname {} for {}'.format(ehn,hostName))
            return ehn
        else:
            print_log('Failed to create the Edgehostname for {} and status code is {}.'.format(hostName,status))
            print('Failed to create the Edgehostname for {} and status code is {}.'.format(hostName,status),file=sys.stderr)
            return ''
    except Exception as e:
        print('{}:Error Creating the Edgehostname for {}'.format(e,hostName),file=sys.stderr)
        print_log('{}:Error Creating the Edgehostname for {}'.format(e,hostName))
        return ''
        exit(3)
