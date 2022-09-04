import time
import datetime

productId = ''
ehndomainsuffix = ''
network = ''
ipversion = ''

def readCommonSettings(sheet):
    cmnsheet = sheet.worksheet('Common Settings')
    numRows = cmnsheet.row_count
    productId = cmnsheet.row_values(1)[1]
    ehndomainsuffix = cmnsheet.row_values(2)[1]
    network = cmnsheet.row_values(3)[1]
    ipversion = cmnsheet.row_values(4)[1]

    print_log('ProductID:{}'.format(productId))
    print_log('EHNDomainSuffix:{}'.format(ehndomainsuffix))
    print_log('Network:{}'.format(network))
    print_log('IPVersion:{}'.format(ipversion))

def getProductId():
    return productId

def getehndomainSuffix():
    return ehndomainsuffix

def getNetwork():
    return network

def getIpVersion():
    return ipversion

def print_log(args):
    now = str(datetime.datetime.now().isoformat()) + 'Z'
    print(now, end = ':')
    print(args, flush=True)