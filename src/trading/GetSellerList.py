import re
import sys
import json
import argparse
import datetime

from ebaysdk.exception import ConnectionError
from ebaysdk.trading import Connection as Trading
from firebase import firebase

GranularityLevel_types = ('Coarse', 'Fine', 'Medium')

def GetSellerList(
        EndTimeFrom=None,
        EndTimeTo=None,
        GranularityLevel=None,
        IncludeVariations=False,
        IncludeWatchCount=False,
        StartTimeFrom=None,
        StartTimeTo=None,
        update_firebase=False,
        firebase_url=None
    ):
    
    options = {}
    
    if EndTimeFrom:
        options['EndTimeFrom'] = EndTimeFrom
    
    if EndTimeTo:
        options['EndTimeTo'] = EndTimeTo
    
    if GranularityLevel:
        options['GranularityLevel'] = GranularityLevel
    
    if IncludeVariations:
        options['IncludeVariations'] = str(IncludeVariations).lower()
    
    if IncludeWatchCount:
        options['IncludeWatchCount'] = str(IncludeWatchCount).lower()
    
    if StartTimeFrom:
        options['StartTimeFrom'] = StartTimeFrom
    
    if StartTimeTo:
        options['StartTimeTo'] = StartTimeTo
    
    if update_firebase and not firebase_url:
        raise Exception('if --update_firebase set to True, --firebase_url is required')
        
    fb = None
    if update_firebase:
        fb = firebase.FirebaseApplication(firebase_url, None)
        
    trading = Trading()        
    num_executions = 0
    options['Pagination'] = { 'EntriesPerPage': '200', 'PageNumber': 0 }
    has_more = True
    
    while has_more and num_executions < 10:
        options['Pagination']['PageNumber'] += 1
        
        try:
            response = trading.execute('GetSellerList', options).dict()
        except ConnectionError as e:
            sys.stderr.write(json.dumps(e.response.dict()) + "\n")
            break

        # safety measure to make sure we dont have an infinite loop
        num_executions += 1

        print 'PageNumber: %s' % options['Pagination']['PageNumber']
        print json.dumps(response, sort_keys=True, indent=5)

        if update_firebase:
            _add_item_to_firebase(response, fb)

        has_more = response.get('HasMoreEntries') == "true"

def _add_item_to_firebase(response, fb):
    
    for item in response['ItemArray']['Item']:

        itemID = item['ItemID']
        
        fb.put('/items', itemID, item)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--EndTimeFrom', type=str)
    parser.add_argument('--EndTimeTo', type=str)
    parser.add_argument('--GranularityLevel', type=str, choices=GranularityLevel_types)
    parser.add_argument('--IncludeVariations', action="store_true")
    parser.add_argument('--IncludeWatchCount', action="store_true")
    parser.add_argument('--StartTimeFrom', type=str)
    parser.add_argument('--StartTimeTo', type=str)
    parser.add_argument('--update_firebase', action="store_true")
    parser.add_argument('--firebase_url', help='firebase url', default='https://theprofitlogger.firebaseio.com')
    args = parser.parse_args()

    sys.exit(GetSellerList(
        EndTimeFrom=args.EndTimeFrom,
        EndTimeTo=args.EndTimeTo,
        GranularityLevel=args.GranularityLevel,
        IncludeVariations=args.IncludeVariations,
        IncludeWatchCount=args.IncludeWatchCount,
        StartTimeFrom=args.StartTimeFrom,
        StartTimeTo=args.StartTimeTo,
        update_firebase=args.update_firebase,
        firebase_url=args.firebase_url
    ))