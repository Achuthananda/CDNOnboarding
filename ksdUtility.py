from commonutilities import print_log,getEmailNotificationList
import json
import sys
import time


def getAppSecConfigStagingVersion(securityConfigId,akhttp,accountSwitchKey):
    try:
        getVersionEP = "/appsec/v1/configs/{}/versions?page=1&pageSize=25&detail=true".format(securityConfigId)
        params = {}
        if accountSwitchKey != None:
            params['accountSwitchKey'] = accountSwitchKey
            
        headers = {"accept": "application/json"}
        status,versionDetailjson = akhttp.getResult(getVersionEP,headers,params)
        if status == 200:
            if 'stagingActiveVersion' in versionDetailjson:
                return versionDetailjson['stagingActiveVersion']
            else:
                return 0
        else:
            print_log("The status of the get staging version is {}".format(status))
            return 0
    except Exception as e:
        print('{}:Error fetching the Staging Version of Security Policy'.format(e),file=sys.stderr)
        return 0
        

def getAppSecConfigProductionVersion(securityConfigId,akhttp,accountSwitchKey):
    try:
        getVersionEP = "/appsec/v1/configs/{}/versions?page=1&pageSize=25&detail=false".format(securityConfigId)
        params = {}
        if accountSwitchKey != None:
            params['accountSwitchKey'] = accountSwitchKey
            
        headers = {"accept": "application/json"}
        status,versionDetailjson = akhttp.getResult(getVersionEP,headers,params)
        if status == 200:
            if 'productionActiveVersion' in versionDetailjson:
                return versionDetailjson['productionActiveVersion']
            else:
                return 0
        else:
            print_log("The status of the get production version is {}".format(status))
            return 0
    except Exception as e:
        print('{}:Error fetching the Production Version of Security Policy'.format(e),file=sys.stderr)
        return 0


def getAppSecConfiglatestVersion(securityConfigId,akhttp,accountSwitchKey):
    try:
        getVersionEP = "/appsec/v1/configs/{}/versions?page=1&pageSize=25&detail=false".format(securityConfigId)
        params = {}
        if accountSwitchKey != None:
            params['accountSwitchKey'] = accountSwitchKey
            
        headers = {"accept": "application/json"}
        status,versionDetailjson = akhttp.getResult(getVersionEP,headers,params)
        if status == 200:
            if 'lastCreatedVersion' in versionDetailjson:
                return versionDetailjson['lastCreatedVersion']
            else:
                return 0
        else:
            print_log("The status of the get latest version is {}".format(status))
            return 0
    except Exception as e:
        print('{}:Error fetching the latest Version of Security Policy'.format(e),file=sys.stderr)
        return 0


def createNewSecConfigVersion(securityConfigId,akhttp,accountSwitchKey):
    try:
        stagingVersion = getAppSecConfigStagingVersion(securityConfigId,akhttp,accountSwitchKey)
        productionVersion = getAppSecConfigProductionVersion(securityConfigId,akhttp,accountSwitchKey)
        latestVersion = getAppSecConfiglatestVersion(securityConfigId,akhttp,accountSwitchKey)
        version = latestVersion
        if productionVersion > 0:
            version = productionVersion
        elif stagingVersion > 0:
            version = stagingVersion
        
        print_log("The base version considered to create new AppSec Config will be {}".format(version))

        cloneversionEP = '/appsec/v1/configs/{}/versions'.format(securityConfigId)
        params = {}
        if accountSwitchKey != None:
            params['accountSwitchKey'] = accountSwitchKey
        
        headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }

        payload = {
            "ruleUpdate": True,
            "createFromVersion": version
        }

        datajson = json.dumps(payload,indent=2)

        status,cloneConfigJson = akhttp.postResult(cloneversionEP,datajson,headers,params)
        if status == 201:
            newVersion = cloneConfigJson['version']
            print_log('Successfully created the new version of the App Sec Policy {}'.format(securityConfigId))
            return newVersion
        else:
            print_log(status)
            print_log("Failed to create the new version of the App Sec Policy")
            return 0
    except Exception as e:
        print('{}:Error create the new version of the App Sec Policy'.format(e),file=sys.stderr)
        return 0

def activateStagingAppSecConfig(securityConfigId,version,akhttp,accountSwitchKey):
    try:
        activateEP = '/appsec/v1/activations'
        params = {}
        if accountSwitchKey != None:
            params['accountSwitchKey'] = accountSwitchKey
        
        headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }

        emailList = getEmailNotificationList()
        emailArray = emailList[0].split(',')

        payload = {
            "activationConfigs": [
                {
                    "configId": securityConfigId,
                    "configVersion": version
                }
            ],
            "notificationEmails": emailArray,
            "network": "STAGING",
            "note": "Activatiion",
            "action":"ACTIVATE"
        }

        datajson = json.dumps(payload,indent=2)

        status,activationJson = akhttp.postResult(activateEP,datajson,headers,params)
        if status in [202,200]:
            print_log('Successfully activated to staging')
            return True
        else:
            print_log(status)
            print_log("Failed to activate App Sec Policy")
            return False
    except Exception as e:
        print('{}:Error activating the config'.format(e),file=sys.stderr)
        return False



def addHostnametoSecConfig(securityConfigId,version,hostNamesArray,akhttp,accountSwitchKey):
    try:
        addHostNameEP = '/appsec/v1/configs/{}/versions/{}/selected-hostnames'.format(securityConfigId,version)
        params = {}
        if accountSwitchKey != None:
            params['accountSwitchKey'] = accountSwitchKey
        
        headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }

        hostArrayVal = []
        for hostname in hostNamesArray:
            item = {}
            item['hostname'] = hostname
            hostArrayVal.append(item)

        payload = {
            "hostnameList": hostArrayVal,
            "mode": "append"
        }

        datajson = json.dumps(payload,indent=2)

        status,addHostnamesJson = akhttp.putResult(addHostNameEP,datajson,headers,params)
        if status == 200:
            print_log('Successfully Added the HostNames')
            return True
        else:
            print_log(status)
            print_log("Failed to add the Hostnames")
            return False
    except Exception as e:
        print('{}:Error adding the Hostnames to Security Policy'.format(e),file=sys.stderr)
        return False


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
