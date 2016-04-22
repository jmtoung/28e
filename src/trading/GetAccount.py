import datetime
from ebaysdk.exception import ConnectionError
from ebaysdk.trading import Connection as Trading
import json

try:
    api = Trading()
    response = api.execute('GetAccount', { 'AccountHistorySelection': 'SpecifiedInvoice',
                                          'InvoiceDate': '2016-01-31T06:59:59.000Z'
                                          })
    
    AccountEntries = response.dict()['AccountEntries']['AccountEntry']
    
    fh = open('test_GetAccount.txt', 'wb')
    
    for i, AccountEntry in enumerate(AccountEntries):
        print type(AccountEntry)
        fh.write("\t".join([str(i), json.dumps(AccountEntry)]) + "\n")
    


except ConnectionError as e:
    print(e)
    print(e.response.dict())