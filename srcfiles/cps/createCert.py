from akamaihttp import AkamaiHTTPHandler
import os
import argparse
import json
import requests
from godaddypy import Client, Account
import time
import uuid
import sys
from commonutilities import print_log

import configparser

settingsconfig = configparser.ConfigParser()
settingsconfig.read('config.ini')
edgercLocation = settingsconfig['Edgerc']['location']
edgercLocation = os.path.expanduser(edgercLocation)
akhttp = AkamaiHTTPHandler(edgercLocation,settingsconfig['Edgerc']['section'])


def updateGodaddyDomain(record,value):
    acct = Account(api_key=settingsconfig['Godaddy']['api_key'],api_secret=settingsconfig['Godaddy']['api_secret'])
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


def getDVChallenges(enrollmentID,accountSwitchKey=None):
    try:
        challengeReceived = False
        while challengeReceived == False:
            time.sleep(10)
            print_log("Waiting for the DNS Challenges to be Received..")
            print("Waiting for the DNS Challenges to be Received..",file=sys.stderr)
            dnsrecordsDict = {}
            headers = {"Accept":"application/vnd.akamai.cps.dv-history.v1+json"}
            dvChallengesEP = '/cps/v2/enrollments/{}/dv-history'.format(enrollmentID)
            params = {}
            if accountSwitchKey != None:
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


def createEnrollment(accountSwitchKey,contractId,fileName):
    try:
        createEnrollmentEP = '/cps/v2/enrollments'
        params = {}
        if accountSwitchKey != None:
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
            print_log('Successfully created the Enrollment and Enrollment Id is {}'.format(enrollmentId))
            print('Successfully created the Enrollment and Enrollment Id is {}'.format(enrollmentId),file=sys.stderr)
            return enrollmentId
        else:
            print_log("Failed to create the CPS Enrollment")
            print("Status Code :{}\nFailed to create the CPS Enrollment".format(status),file=sys.stderr)
            return 0
    except Exception as e:
        print('{}:Error Creating the Enrollment'.format(e),file=sys.stderr)
        exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Times CDN Onboarding Tool.')
    # Storage migration

    parser.add_argument('--accountSwitchKey', default=None,help='Account SwitchKey')    
    parser.add_argument('--contractId', required=True,help='ContractID')
    parser.add_argument('--file', required=True,help='File having the Cert Details')
    parser.add_argument('--logfile', help='Log File Name')

    args = parser.parse_args()
    jobId = str(uuid.uuid1())
    logfilepath = ''

    curdir = os.getcwd()
    dirpath = os.path.dirname(curdir + '/logs')
    logfilepath = dirpath + "/"  + jobId+'.txt'

    if args.logfile:
        logfilepath = dirpath + "/" + args.logfile

    sys.stdout = open(logfilepath, 'w+')

    enrollmentId = createEnrollment(args.accountSwitchKey,args.contractId,args.file)
    if enrollmentId != 0:
        dnsrecordsDict = getDVChallenges(enrollmentId,args.accountSwitchKey)
        print(json.dumps(dnsrecordsDict,indent=2),file=sys.stderr)
        for record in dnsrecordsDict:
            udpaterecordstatus = updateGodaddyDomain(record,dnsrecordsDict[record])
            print_log("The status of adding record {} to DNSZone is {}".format(record,udpaterecordstatus))
            print("The status of adding record {} to DNSZone is {}".format(record,udpaterecordstatus),file=sys.stderr)
    else:
        print_log("Failed to Create the Enrollment Id!!")
        print("Failed to Create the Enrollment Id!!",file=sys.stderr)

   
'''
python createCert.py --logfile cpslog --accountSwitchKey 1-6JHGX --contractId 1-1NC95D --file enrollment_data.json
Akamai Professional Services

'''


