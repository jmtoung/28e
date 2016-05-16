import json
from datetime import datetime, timedelta
from trading.GetAccount import GetAccount
from firebase import firebase

# initialize firebase 
firebase_url = 'https://theprofitlogger.firebaseio.com'
firebase = firebase.FirebaseApplication(firebase_url, None)

# get the last time we ran this script
response = firebase.get('/api_calls/ebay', 'update_fees_daily')

# initialize EndDate to now
EndDate=datetime.utcnow()

if response:
    print 'Last time we ran the script was %s' % response
    BeginDate = response
# if response is None, that means we haven't run this script before
else:
    BeginDate = EndDate - timedelta(days=4*28)
    BeginDate = BeginDate.isoformat() + 'Z'
    # clear fees in case they exist
    firebase.delete('/', 'fees')

# convert to ebay format
EndDate = EndDate.isoformat() + 'Z'
#"2016-01-16T19:14:06.000Z", 
#TestDate = datetime(year=2016, month=1, day=16, hour=19, minute=14, second=06)
#BeginDate = TestDate - timedelta(seconds=10)
#EndDate = TestDate + timedelta(seconds=10)

# now run GetAccount using the start and end dates
try:
    responses = GetAccount(AccountHistorySelection='BetweenSpecifiedDates',
                           BeginDate=BeginDate,
                           EndDate=EndDate)
    for i, response in enumerate(responses):
        response = response.dict()
        print 'PageNumber: %s' % (i + 1)
        print json.dumps(response, sort_keys=True, indent=5)
        
        if 'AccountEntries' in response and 'AccountEntry' in response['AccountEntries']:
            for entry in response['AccountEntries']['AccountEntry']:
                if entry['RefNumber'] == '0':
                    # parse month and year
                    Date = datetime.strptime( entry['Date'], "%Y-%m-%dT%H:%M:%S.%fZ" )
                    firebase.post('/fees/byDate/%s' % Date.strftime('%Y-%m'), entry)
                    
                else:
                    firebase.put('/fees/byRefNumber', entry['RefNumber'], entry)
                
except Exception as e:
    raise
else:
    print('successfully retrieved')
    
    # if GetAccount does not raise an exception, update the EndDate
    firebase.put('/api_calls/ebay', 'update_fees_daily', EndDate)
    print('successfully updated')