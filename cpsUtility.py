from commonutilities import print_log,getProductId,getehndomainSuffix,getIpVersion,getNetwork
import json
import sys

def geEnrollment(enrollmentId,akhttp,accountSwitchKey):
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

def addSANtoCert(rowData,akhttp,accountSwitchKey):
    try:
        print_log("Adding the SAN to the cert!")
        certenrollmentbody = geEnrollment(rowData['CertEnrollmentId'],akhttp,accountSwitchKey)
        print(json.dumps(result[1],indent=2),file=sys.stderr)
    except Exception as e:
        print_log(e)

