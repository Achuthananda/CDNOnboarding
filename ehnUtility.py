from commonutilities import print_log,getProductId,getehndomainSuffix,getIpVersion,getNetwork

def createEdgeHostName(rowData,akhttp,accountSwitchKey):
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
        "ipVersionBehavior": getIpVersion()
        "certEnrollmentId": rowData['certEnrollmentId']
    }

    hostname_data = json.dumps(create_hostname)

    createEHNEndPoint = '/papi/v1/edgehostnames'
    status,createEHNJson = prdHttpCaller.postResult(createEHNEndPoint,hostname_data,params)
    return status,createEHNJson
