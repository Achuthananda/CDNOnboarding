from akamaihttp import AkamaiHTTPHandler
import os
import argparse
import json



def cloneProperty(accountSwitchKey,contractId,groupId,propertyId,version,newPropertyName):
    edgercLocation = '~/.edgerc'
    edgercLocation = os.path.expanduser(edgercLocation)
    akhttp = AkamaiHTTPHandler(edgercLocation,'papi')

    version = int(version)
    params = {}
    if accountSwitchKey:
        params["accountSwitchKey"] = accountSwitchKey
    params["contractId"] = contractId
    params["groupId"] = groupId


    clone_payload = {
        "cloneFrom": {
            "copyHostnames": True,
            "propertyId": propertyId,
            "version": version
        },
        "productId": "prd_Fresca",
        "propertyName": newPropertyName
    }

    clone_data = json.dumps(clone_payload)
    print(clone_data)
    print(params)

    cloneConfigEndPoint = '/papi/v1/properties'
    headers = {'Content-Type': 'application/json'}

    status,createConfigJson = akhttp.postResult(cloneConfigEndPoint,clone_data,headers,params)
    if status == 201:
        print(createConfigJson)
        newpropetyId = createCPCodeJson['propertyLink'].split('?')[0].split('/')[4].split('_')[1]
        print_log('Successfully created the Config {} for {}'.format(newpropetyId))
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
    parser.add_argument('--newPropertyName', help='Version')

    
    args = parser.parse_args()


    cloneProperty(args.accountSwitchKey,args.contractId,args.groupId,args.propertyId,args.version,args.newPropertyName)

'''
python cloneproperty.py --accountSwitchKey B-3-16OEUPX  --contractId ctr_3-16TWBVX --groupId grp_173720 --propertyId prp_10860903 --version 1 --newPropertyName "testnewproperty_acmp"
'''


