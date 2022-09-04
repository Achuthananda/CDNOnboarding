from commonutilities import print_log,getProductId
import json
import sys

def createCPCode(rowData,akhttp,accountSwitchKey):
    try:
        params = {}
        if accountSwitchKey:
            params["accountSwitchKey"] = accountSwitchKey
        params["contractId"] = rowData['ContractId']
        params["groupId"] = rowData['GroupId']


        create_cpcode = {
            "productId": getProductId(),
            "cpcodeName": rowData['Hostname']
        }

        cpcode_data = json.dumps(create_cpcode)

        createCPCodeEndPoint = '/papi/v1/cpcodes'
        headers = {'Content-Type': 'application/json',
                   'PAPI-Use-Prefixes': True}

        print_log('test1')
        status,createCPCodeJson = akhttp.postResult(createCPCodeEndPoint,cpcode_data,headers,params)
        if status == 202:
            print_log(createCPCodeJson)
            print_log('Successfully created the CP Code for {}'.format(rowData['Hostname']))
            cpCode = createCPCodeJson['cpcodeLink'].split('?')[0].split('/')[4].split('_')[1]
            return cpCode
        else:
            print_log('Failed to create the CP Code for {} and status code is {}.'.format(rowData['Hostname'],status))
            return 0
    except:
        print('Error Creating the CP Code for {}'.format(rowData),file=sys.stderr)
        print_log('Error Creating the CP Code for {}'.format(rowData['Hostname']))
        exit(3)
