from commonutilities import print_log,getProductId,getehndomainSuffix,getIpVersion,getNetwork
import json
import sys

def createEdgeHostName(rowData,akhttp,accountSwitchKey=None):
    try:
        params = {}
        if accountSwitchKey:
            params["accountSwitchKey"] = accountSwitchKey
        params["contractId"] = rowData['ContractId']
        params["groupId"] = rowData['GroupId']

        
        create_hostname = {
            "productId": getProductId(),
            "domainPrefix": rowData['Hostname'],
            "domainSuffix": getehndomainSuffix(),
            "secureNetwork": getNetwork(),
            "ipVersionBehavior": getIpVersion(),
            "certEnrollmentId": rowData['CertEnrollmentId']
        }

        hostname_data = json.dumps(create_hostname)
        headers = {'Content-Type': 'application/json'}
        ehn = rowData['Hostname'] + '.' + getehndomainSuffix()
        #print_log(hostname_data)
        #print_log(headers)

        createEHNEndPoint = '/papi/v1/edgehostnames'
        status,createEHNJson = akhttp.postResult(createEHNEndPoint,hostname_data,headers,params)
        if status == 201:
            print_log(createEHNJson)
            print_log('Successfully created the Edgehostname {} for {}'.format(ehn,rowData['Hostname']))
            return ehn
        else:
            print_log('Failed to create the Edgehostname for {} and status code is {}.'.format(rowData['Hostname'],status))
            return ''
    except Exception as e:
        print('{}:Error Creating the Edgehostname for {}'.format(e,rowData['Hostname']),file=sys.stderr)
        print_log('{}:Error Creating the Edgehostname for {}'.format(e,rowData['Hostname']))
        exit(3)
