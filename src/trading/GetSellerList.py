import re
import sys
import json
import argparse
import datetime
from ebaysdk.exception import ConnectionError
from ebaysdk.trading import Connection as Trading
from firebase import firebase

# GetSellerList gets all a seller's listings regardless of whether the item sold
# new comment

class GetSellerList:
    
    def __init__(self,
                firebase_url
                ):
        
        self.firebase_url = firebase_url
        
        self.Trading = Trading()
        self.firebase = firebase.FirebaseApplication(self.firebase_url, None)
    
    def _parseGetAccount(self, response):
        AccountEntries = response.dict()['AccountEntries']['AccountEntry']
        
        for i, AccountEntry in enumerate(AccountEntries):
            refNumber = AccountEntry['RefNumber']
            # if refNumber is 0, it's not associated with an item
            if refNumber == '0':
                invoiceDate = response.dict()['AccountSummary']['InvoiceDate']
                invoiceDate_regex = re.match('^([0-9]{4}-[0-9]{2}-[0-9]{2})T', invoiceDate)
                if invoiceDate_regex:
                    invoiceDate = invoiceDate_regex.group(1)
                else:
                    raise Exception('invoice Date %s does not match' % invoiceDate)
                self.firebase.post('/fees/byInvoiceDate/%s' % invoiceDate, AccountEntry)
            else:
                self.firebase.put('/fees/byRefNumber', refNumber, AccountEntry)
        
    def getSellerList(self):
                
        PageNumber = 1
        NumExecutions = 1
        
        while True:
            try: 
                response = self.Trading.execute('GetSellerList', {
                    'EndTimeTo': '2016-04-20',
                    'EndTimeFrom': '2016-03-30',
                    'GranularityLevel': 'Coarse',
                    'Pagination': {'PageNumber' : str(PageNumber)}})
                print str(PageNumber)
                # safety measure to make sure we dont have an infinite loop
                NumExecutions += 1
                if NumExecutions > 10:
                    break
                        
                for i, item in enumerate(response.dict()['ItemArray']['Item']):
                    #print i, "\t", json.dumps(item)
                    isSold = 'X'
                    if 'HighBidder' in item['SellingStatus']:
                        isSold='*'
                        print i, "\t", isSold, "\t", item['ListingDetails']['EndTime'], "\t", item['Title'], "\t", item
                
                test = response.dict()
                test['ItemArray'] = None
                print json.dumps(test)
                
                if 'HasMoreEntries' in response.dict():
                    if response.dict()['HasMoreEntries'] == "true":
                        PageNumber += 1
                    else:
                        break    
                else:
                    break
                
            except ConnectionError as e:
                sys.stderr.write(json.dumps(e.response.dict()) + "\n")
                raise Exception

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--firebase_url', help='firebase url', default='https://theprofitlogger.firebaseio.com')
    
    args = parser.parse_args()
    
    getSellerList = GetSellerList(args.firebase_url)
    getSellerList.getSellerList()
