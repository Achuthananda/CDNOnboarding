from commonutilities import print_log
import json
import sys
from godaddypy import Client, Account
import time


def updateGodaddyDomain(record,value):
    acct = Account(api_key='fYg34SGLy3kW_SJ27b4RYXKbAWRPA5ht4na',api_secret='RfKhXguQjptQd6fzkWVXpW')
    godaddyclient = Client(acct)
    recordArrTemp = record.split('.')
    if recordArrTemp[-1] == '':
        recordArr = recordArrTemp[:-3]
    else:
        recordArr = recordArrTemp[:-2]
    recordname = '.'.join(recordArr)
    if godaddyclient.add_record('iamacmp.com', {'data':value,'name':recordname,'ttl':600, 'type':'TXT'}) == True:
        print_log("Created a TXT record for  Succesfully for {}".format(record))
        return True
    else:
        print("Failed to create the TXT Record for {}".format(record))
        return False


def getDVChallenges(akhttp,enrollmentID,accountSwitchKey=None):
    try:
        challengeReceived = False
        while challengeReceived == False:
            time.sleep(1)
            print_log("Waiting for the DNS Challenges to be Received..")
            print("Waiting for the DNS Challenges to be Received..",file=sys.stderr)
            dnsrecordsDict = {}
            headers = {"Accept":"application/vnd.akamai.cps.dv-history.v1+json"}
            dvChallengesEP = '/cps/v2/enrollments/{}/dv-history'.format(enrollmentID)
            params = {}
            if accountSwitchKey:
                params['accountSwitchKey'] = accountSwitchKey

            result = akhttp.getResult(dvChallengesEP,headers,params)
            if result[0] == 200:
                print(json.dumps(result[1],indent=2))
                for domain in result[1]['results']:
                    for children in domain['domainHistory']:
                        for challenge in children['challenges']:
                            if challenge['type'] == 'dns-01' and challenge['status'] == 'pending':
                                challengeReceived = True 
                                print_log("DNS Challenges Received for {}".format(challenge['fullPath']))                         
                                print_log("\nDNS Record:{}\nToken:{}".format(challenge['fullPath'],challenge['responseBody']))
                                print("DNS Record:{}\nToken:{}".format(challenge['fullPath'],challenge['responseBody']),file=sys.stderr)
                                print('*'*80,file=sys.stderr)
                                dnsrecordsDict[challenge['fullPath']] = challenge['responseBody']
                if challengeReceived:
                    return dnsrecordsDict
        else:
            print_log("Failed to Fetch the Challenges {}".format(enrollmentId))
            return {}
    except Exception as e:
        print_log(e)


def geEnrollment(enrollmentId,akhttp,accountSwitchKey=None):
    try:
        cpsEP = '/cps/v2/enrollments/{}'.format(enrollmentId)
        params = {}
        if accountSwitchKey:
            params['accountSwitchKey'] = accountSwitchKey

        headers = {"Accept": "application/vnd.akamai.cps.enrollment.v11+json"}

        result = akhttp.getResult(cpsEP,headers,params)
        if result[0] == 200:
            print_log("Succesfully Fetched the Enrollment {}".format(enrollmentId))
            return result[1]
        else:
            print_log("Failed to Fetchthe Enrollment {}".format(enrollmentId))
            return {}
    except Exception as e:
        print_log(e)
        print(e)
        exit(4)

def addSANtoCert(enrollmentID,sansList,akhttp,accountSwitchKey):
    try:
        print_log("Adding the SAN to the cert!")
        certenrollmentbody = geEnrollment(enrollmentID,akhttp,accountSwitchKey)

        params = {}
        if accountSwitchKey:
            params['accountSwitchKey'] = accountSwitchKey

        for san in sansList:
            certenrollmentbody['csr']['sans'].append(san)

        print_log(json.dumps(certenrollmentbody,indent=2))
        
        csr_data = json.dumps(certenrollmentbody) 

        updateEnrollmentEP = '/cps/v2/enrollments/{}'.format(enrollmentID)
        headers = {
            "Accept": "application/vnd.akamai.cps.enrollment-status.v1+json",
            "Content-Type": "application/vnd.akamai.cps.enrollment.v11+json"
        }

        status,updateEnrollmentJson = akhttp.putResult(updateEnrollmentEP,csr_data,headers,params)
        if status == 202:
            #print_log(updateEnrollmentJson)
            print_log('Successfully added the SANs Cert ID {}'.format(enrollmentID))
            return True
        else:
            print_log('Failed to add the the SANs for Cert ID {}'.format(enrollmentID))
            return False

    except Exception as e:
        print_log(e)
        print(e)
        return False

