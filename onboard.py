# Import required modules
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import argparse
import datetime
import time
import uuid
from tqdm import tqdm
import sys,os
from cpCodeUtility import createCPCode
from ehnUtility import createEdgeHostName
from cpsUtility import addSANtoCert,getDVChallenges,updateGodaddyDomain
from akamaihttp import AkamaiHTTPHandler
from commonutilities import print_log,readCommonSettings


edgercLocation = '~/.edgerc'
edgercLocation = os.path.expanduser(edgercLocation)
akhttp = AkamaiHTTPHandler(edgercLocation,'default')

jobId = str(uuid.uuid1())
logfilepath = ''


scope = ["https://spreadsheets.google.com/feeds", 
        'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", 
         "https://www.googleapis.com/auth/drive"]
 
 
# Assign credentials ann path of style sheet
creds = ServiceAccountCredentials.from_json_keyfile_name("/Users/apadmana/Achuth/code_base/AkamaiInteralGit/CustomerCode/India/Times/GsheetKeys/creds.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Times Onboarding")


    
def addHostNametoCert(rowData,akhttp,accountSwitchKey):
    print_log("Now adding the Hostname to Certificate")
    

def main(sheetName,startRow,endRow,accountSwitchKey=None):
    startRow = int(startRow)
    endRow = int(endRow)
    if startRow <= 0 or endRow <=0 or startRow > endRow:
        print("Invalid Values for startRow or endRow. Please try again!",file=sys.stderr)
        exit(1)
    try:
        sheet_instance = sheet.worksheet(sheetName)
    except:
        print("Wrong SheetName.Please Provide the correct sheet name and try again!",file=sys.stderr)
        exit(2)


    startRow = startRow-2
    endRow = endRow-2

    #Read Common Settings
    readCommonSettings(sheet)
    data = sheet_instance.get_all_records()
    #print(json.dumps(data,indent=2))
    
    progress_bar = tqdm(total=endRow-startRow+1)
    def udpateprogressbar():
        progress_bar.update()

    certtoHostnameDict = {}

    for i in range(startRow,endRow+1):
        print_log(data[i])
        if data[i]['SAN Addition'] == '':
            if data[i]['CertEnrollmentId'] not in certtoHostnameDict:
                certtoHostnameDict[data[i]['CertEnrollmentId']] = [data[i]['Hostname']]
            else:
                certtoHostnameDict[data[i]['CertEnrollmentId']].append(data[i]['Hostname'])

        if data[i]['CPCode'] == '':
            cpCode = createCPCode(data[i],akhttp,accountSwitchKey)
            if cpCode != 0:
                sheet_instance.update_cell(i+2, 9,cpCode) #Update the CP Code 
        else:
            print_log("CPCode already present in the sheet !So skipping creating the CP Code")
            print("CPCode already present in the sheet !So skipping creating the CP Code",file=sys.stderr)
    
        if data[i]['Edgehostname'] == '':
            edgeHostName = createEdgeHostName(data[i],akhttp,accountSwitchKey)
            if edgeHostName != '':
                sheet_instance.update_cell(i+2, 10,edgeHostName) #Update the CP Code 
        else:
            print_log("EHN already present in the sheet !So skipping creating the EHN")
            print("EHN already present in the sheet !So skipping creating the EHN",file=sys.stderr)
        time.sleep(1)
        udpateprogressbar()
        print_log('*'*80)


    for enrollmentID in certtoHostnameDict:
        addStatus = addSANtoCert(enrollmentID,certtoHostnameDict[enrollmentID],akhttp,accountSwitchKey)
        for i in range(startRow,endRow+1):
            if data[i]['Hostname'] in certtoHostnameDict[enrollmentID]:
                sheet_instance.update_cell(i+2, 11,addStatus) #Update the SAN Addition 
        #getDVChallenges(enrollmentID)
        ##UpdateZoneFile(records)

    for enrollmentID in certtoHostnameDict:
        dnsrecordsDict = getDVChallenges(akhttp,enrollmentID,accountSwitchKey)
        print(json.dumps(dnsrecordsDict,indent=2),file=sys.stderr)
        for record in dnsrecordsDict:
            udpaterecordstatus = updateGodaddyDomain(record,dnsrecordsDict[record])
            print_log("The status of adding record {} to DNSZone is {}".format(record,udpaterecordstatus))
            print("The status of adding record {} to DNSZone is {}".format(record,udpaterecordstatus),file=sys.stderr)


    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Times CDN Onboarding Tool.')
    # Storage migration
    parser.add_argument('--sheet', required=True, help='Sheet Name')
    parser.add_argument('--start', required=True, help='Starting Row Number')
    parser.add_argument('--end', required=True, help='End Row')
    parser.add_argument('--accountSwitchKey', help='Account SwitchKey')
    parser.add_argument('--logfile', help='Log File Name')

    args = parser.parse_args()

    curdir = os.getcwd()
    dirpath = os.path.dirname(curdir + '/logs')
    logfilepath = dirpath + "/"  + jobId+'.txt'
    
    if args.logfile:
        logfilepath = dirpath + "/" + args.logfile

    sys.stdout = open(logfilepath, 'w')
    main(args.sheet,args.start,args.end,args.accountSwitchKey)


'''
python onboard.py --sheet 'First Batch' --start 5 --end 5 --accountSwitchKey B-3-16OEUPX --logfile file.txt
'''
