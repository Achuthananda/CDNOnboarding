from akamaihttp import AkamaiHTTPHandler
import os
import argparse
import json
import requests
from akamai.edgegrid import EdgeGridAuth, EdgeRc
from urllib.parse import urljoin


edgercLocation = '~/.edgerc'
edgercLocation = os.path.expanduser(edgercLocation)
akhttp = AkamaiHTTPHandler(edgercLocation,'default')

def createEnrollment(accountSwitchKey,contractId,fileName):
    try:
        createEnrollmentEP = '/cps/v2/enrollments'
        params = {}
        if accountSwitchKey:
            params['accountSwitchKey'] = accountSwitchKey
        params["contractId"] = contractId

        headers = {}
        headers['Content-Type'] = 'application/vnd.akamai.cps.enrollment.v10+json'
        headers['Accept'] = 'application/vnd.akamai.cps.enrollment-status.v1+json'
        params['Contract'] = contractId

        fp = open(fileName,'r')
        data = json.load(fp)

        datajson = json.dumps(data,indent=2)
        #print(datajson)

        status,createEnrollmentJson = akhttp.postResult(createEnrollmentEP,datajson,headers,params)
        if status == 202:
            #print(createEnrollmentJson)
            enrollmentId = createEnrollmentJson['enrollment'].split('/')[4]
            print('Successfully created the Enrollment and Enrollment Id is {}'.format(enrollmentId))
            return enrollmentId
        else:
            print("Failed to create the CPS Enrollment")
            return 0
    except Exception as e:
        print('{}:Error Creating the Enrollment {}'.format(e,rowData),file=sys.stderr)
        exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Times CDN Onboarding Tool.')
    # Storage migration
    parser.add_argument('--accountSwitchKey', help='Account SwitchKey')
    parser.add_argument('--contractId', help='ContractID')
    parser.add_argument('--file', help='File having the Cert Details')
    
    args = parser.parse_args()
    createEnrollment(args.accountSwitchKey,args.contractId,args.file)
   
'''
python createCert.py --accountSwitchKey B-3-16OEUR3 --contractId 3-16U194M --file enrollment_data.json
Ion Standard Beta Jam 4
'''


