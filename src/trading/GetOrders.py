import re
import sys
import json
import argparse
import datetime

from ebaysdk.exception import ConnectionError
from ebaysdk.trading import Connection as Trading
from firebase import firebase

DetailLevel_types = set('ReturnAll',)
def GetOrders(
        CreateTimeFrom=None,
        CreateTimeTo=None,
        IncludeFinalValueFee=False,
        ModTimeFrom=None,
        ModTimeTo=None,
        NumberOfDays=None,
        OrderID=None,
        DetailLevel=None,
        update_firebase=False,
        firebase_url=None
    ):

    options = {}
    if CreateTimeFrom:
        options['CreateTimeFrom'] = CreateTimeFrom
    if CreateTimeTo:
        options['CreateTimeTo'] = CreateTimeTo
    
    if IncludeFinalValueFee:
        options['IncludeFinalValueFee'] = str(IncludeFinalValueFee).lower()
    
    if ModTimeFrom:
        options['ModTimeFrom'] = ModTimeFrom
    if ModTimeTo:
        options['ModTimeTo'] = ModTimeTo
    
    if NumberOfDays:
        options['NumberOfDays'] = int(NumberOfDays)
    
    if OrderID:
        options['OrderIDArray'] = { 'OrderID': OrderID }
    
    if DetailLevel:
        options['DetailLevel'] = DetailLevel
        
    options['Pagination'] = { 'EntriesPerPage': '1000', 'PageNumber': 1 }
    
    if update_firebase:
        if not firebase_url:
            raise Exception('if --update_firebase set to True, --firebase_url is required')
        
    trading = Trading()
    
    fb = None
    if update_firebase:
        fb = firebase.FirebaseApplication(firebase_url, None)
        
    page_number = 1
    num_executions = 1
    
    while True:
        try:
            response = trading.execute('GetOrders', options)

            # safety measure to make sure we dont have an infinite loop
            num_executions += 1
            if num_executions > 10:
                break

            print 'PageNumber: %s' % options['Pagination']['PageNumber']
            print json.dumps(response.dict(), sort_keys=True, indent=5)
            
            if update_firebase:
                _add_order_to_firebase(response, fb)

            has_more = response.dict().get('HasMoreEntries') == "true"
            if has_more:
                options['Pagination']['PageNumber'] += 1
            else:
                break

        except ConnectionError as e:
            sys.stderr.write(json.dumps(e.response.dict()) + "\n")
            break

def _add_order_to_firebase(response, fb):
    
    for order in response.dict()['OrderArray']['Order']:
        OrderID = order['OrderID']
        
        fb.put('/orders', OrderID, order)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--CreateTimeFrom', type=str)
    parser.add_argument('--CreateTimeTo', type=str)
    parser.add_argument('--IncludeFinalValueFee', action="store_true")
    parser.add_argument('--ModTimeFrom', type=str)
    parser.add_argument('--ModTimeTo', type=str)
    parser.add_argument('--NumberOfDays', type=int)
    parser.add_argument('--OrderID', type=str, nargs="*")
    parser.add_argument('--DetailLevel', type=str, choices=DetailLevel_types)
    parser.add_argument('--update_firebase', action="store_true")
    parser.add_argument('--firebase_url', help='firebase url', default='https://theprofitlogger.firebaseio.com')
    args = parser.parse_args()

    sys.exit(GetOrders(
        CreateTimeFrom=args.CreateTimeFrom,
        CreateTimeTo=args.CreateTimeTo,
        IncludeFinalValueFee=args.IncludeFinalValueFee,
        ModTimeFrom=args.ModTimeFrom,
        ModTimeTo=args.ModTimeTo,
        NumberOfDays=args.NumberOfDays,
        OrderID=args.OrderID,
        DetailLevel=args.DetailLevel,
        update_firebase=args.update_firebase,
        firebase_url=args.firebase_url
    ))