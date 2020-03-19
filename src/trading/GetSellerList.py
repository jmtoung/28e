import re
import sys
import json
import argparse
import datetime

from ebaysdk.exception import ConnectionError
from ebaysdk.trading import Connection as Trading

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
                    
    trading = Trading()        
    options['Pagination'] = { 'EntriesPerPage': '200', 'PageNumber': 0 }
    has_more = True
    
    while has_more:
        options['Pagination']['PageNumber'] += 1
        
        try:
            response = trading.execute('GetSellerList', options)
        except ConnectionError as e:
            raise Exception('ConnectionError:\n%s' % json.dumps(e.response.dict(), sort_keys=True, indent=5))
        else:
            yield response

        has_more = response.dict().get('HasMoreEntries') == "true"

#def _add_item_to_firebase(response, fb):
#    
#    for item in response['ItemArray']['Item']:
#
#        itemID = item['ItemID']
#        
#        fb.put('/items', itemID, item)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--EndTimeFrom', type=str)
    parser.add_argument('--EndTimeTo', type=str)
    parser.add_argument('--GranularityLevel', type=str, choices=GranularityLevel_types)
    parser.add_argument('--IncludeVariations', action="store_true")
    parser.add_argument('--IncludeWatchCount', action="store_true")
    parser.add_argument('--StartTimeFrom', type=str)
    parser.add_argument('--StartTimeTo', type=str)
    args = parser.parse_args()

    sys.exit(GetSellerList(
        EndTimeFrom=args.EndTimeFrom,
        EndTimeTo=args.EndTimeTo,
        GranularityLevel=args.GranularityLevel,
        IncludeVariations=args.IncludeVariations,
        IncludeWatchCount=args.IncludeWatchCount,
        StartTimeFrom=args.StartTimeFrom,
        StartTimeTo=args.StartTimeTo
    ))