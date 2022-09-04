from commonutilities import print_log
import json
import sys

def getDVChallenges(akhttp,enrollmentID,accountSwitchKey=None):
    try:
        dnsrecordsDict = {}
        headers = {"Accept":"application/vnd.akamai.cps.dv-history.v1+json"}
        dvChallengesEP = '/cps/v2/enrollments/{}/dv-history'.format(enrollmentID)
        params = {}
        if accountSwitchKey:
            params['accountSwitchKey'] = accountSwitchKey

        result = akhttp.getResult(dvChallengesEP,headers,params)
        if result[0] == 200:
            print_log("Succesfully Fetched the Challenges")
            #print(json.dumps(result[1],indent=2),file=sys.stderr)
            for domain in result[1]['results']:
                for children in domain['domainHistory']:
                    for challenge in children['challenges']:
                        if challenge['type'] == 'dns-01' and challenge['status'] == 'pending':
                            print_log("\nDNS Record:{}\nToken:{}".format(challenge['fullPath'],challenge['token']))
                            print("DNS Record:{}\nToken:{}".format(challenge['fullPath'],challenge['token']),file=sys.stderr)
                            print('*'*80,file=sys.stderr)
                            dnsrecordsDict[challenge['fullPath']] = challenge['token']
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

