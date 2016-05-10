import re
import sys
import json
import argparse
import datetime

from ebaysdk.exception import ConnectionError
from ebaysdk.trading import Connection as Trading

DetailLevel_types = set('ReturnAll',)

def GetOrders(
        CreateTimeFrom=None,
        CreateTimeTo=None,
        IncludeFinalValueFee=False,
        ModTimeFrom=None,
        ModTimeTo=None,
        NumberOfDays=None,
        OrderID=None,
        DetailLevel=None
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
                    
    trading = Trading()
    options['Pagination'] = { 'EntriesPerPage': '1000', 'PageNumber': 0 }
    has_more = True
    
    while has_more:
        options['Pagination']['PageNumber'] += 1
        
        try:
            response = trading.execute('GetOrders', options)
        except ConnectionError as e:
            raise Exception('ConnectionError:\n%s' % json.dumps(e.response.dict(), sort_keys=True, indent=5))
        else:
            yield response

        has_more = response.get('HasMoreEntries') == "true"

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
    args = parser.parse_args()

    sys.exit(GetOrders(
        CreateTimeFrom=args.CreateTimeFrom,
        CreateTimeTo=args.CreateTimeTo,
        IncludeFinalValueFee=args.IncludeFinalValueFee,
        ModTimeFrom=args.ModTimeFrom,
        ModTimeTo=args.ModTimeTo,
        NumberOfDays=args.NumberOfDays,
        OrderID=args.OrderID,
        DetailLevel=args.DetailLevel
    ))