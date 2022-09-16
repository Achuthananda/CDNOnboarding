import time
import sys
import datetime

productId = ''
ehndomainsuffix = ''
network = ''
ipversion = ''
emailNotification = []


def readCommonSettings(sheet):
    global productId
    global ehndomainsuffix
    global network
    global ipversion
    global emailNotification

    cmnsheet = sheet.worksheet('Common Settings')
    numRows = cmnsheet.row_count
    productId = cmnsheet.row_values(1)[1]
    ehndomainsuffix = cmnsheet.row_values(2)[1]
    network = cmnsheet.row_values(3)[1]
    ipversion = cmnsheet.row_values(4)[1]
    emailNotificationTemp = cmnsheet.row_values(5)[1]
    emailNotification = [emailNotificationTemp]

    print_log('ProductID:{}'.format(productId))
    print_log('EHNDomainSuffix:{}'.format(ehndomainsuffix))
    print_log('Network:{}'.format(network))
    print_log('IPVersion:{}'.format(ipversion))
    print_log(emailNotification)

def getProductId():
    global productId
    return productId

def getehndomainSuffix():
    global ehndomainsuffix
    return ehndomainsuffix

def getNetwork():
    global network
    return network

def getIpVersion():
    global ipversion
    return ipversion

def getEmailNotificationList():
    global emailNotification
    return emailNotification

def print_log(args):
    now = str(datetime.datetime.now().isoformat()) + 'Z'
    print(now, end = ':')
    print(args, flush=True)