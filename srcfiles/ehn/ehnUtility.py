from ..common.commonutilities import print_log,getProductId,getehndomainSuffix,getIpVersion,getNetwork
import json
import sys


def createEdgeHostName(contractId,groupId,hostName,certEnrollmentId,akhttp,accountSwitchKey=None):
    try:
        params = {}
        if accountSwitchKey != None:
            params["accountSwitchKey"] = accountSwitchKey
        params["contractId"] = contractId
        params["groupId"] = groupId

        
        create_hostname = {
            "productId": getProductId(),
            "domainPrefix": hostName,
            "domainSuffix": getehndomainSuffix(),
            "secureNetwork": getNetwork(),
            "ipVersionBehavior": getIpVersion(),
            "certEnrollmentId": certEnrollmentId
        }

        hostname_data = json.dumps(create_hostname)
        headers = {'Content-Type': 'application/json'}
        ehn = hostName + '.' + getehndomainSuffix()
        #print_log(hostname_data)
        #print_log(headers)

        createEHNEndPoint = '/papi/v1/edgehostnames'
        status,createEHNJson = akhttp.postResult(createEHNEndPoint,hostname_data,headers,params)
        if status == 201:
            print_log(createEHNJson)
            print_log('Successfully created the Edgehostname {} for {}'.format(ehn,hostName))
            return ehn
        else:
            print_log('Failed to create the Edgehostname for {} and status code is {}.'.format(hostName,status))
            return ''
    except Exception as e:
        print('{}:Error Creating the Edgehostname for {}'.format(e,hostName),file=sys.stderr)
        print_log('{}:Error Creating the Edgehostname for {}'.format(e,hostName))
        exit(3)
