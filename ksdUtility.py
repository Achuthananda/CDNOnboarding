from commonutilities import print_log
import json
import sys
import time


def createSecurityPolicy(akhttp,accountSwitchKey,configId,version,securityPolicyName):
    try:
        createSPEP = '/appsec/v1/configs/{}/versions/{}/security-policies'.format(configId,version)
        params = {}
        if accountSwitchKey:
            params['accountSwitchKey'] = accountSwitchKey
        
        
        headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }

        letters = string.ascii_letters
        policyPrefix = "".join(random.sample(letters,3))

        payload = {
            "policyName": securityPolicyName,
            "policyPrefix": policyPrefix
        }

        datajson = json.dumps(payload,indent=2)

        status,createAppSecPolicyJson = akhttp.postResult(createSPEP,datajson,headers,params)
        if status == 200:
            #print(createEnrollmentJson)
            policyId = createAppSecPolicyJson['policyId']
            print_log('Successfully created the App Sec Policy {} and  Id is {}'.format(securityPolicyName,policyId))
            return policyId
        else:
            print_log(status)
            print_log("Failed to create the App Sec Policy")
            return 0
    except Exception as e:
        print('{}:Error create the App Sec Policy'.format(e),file=sys.stderr)
        return 0

    return configId
