import json
from datetime import datetime, timedelta
from trading.GetOrders import GetOrders
from firebase import firebase

# initialize firebase 
firebase_url = 'https://theprofitlogger.firebaseio.com'
firebase = firebase.FirebaseApplication(firebase_url, None)

Now = datetime.utcnow()

# get the last time we ran the update orders
response = firebase.get('/api_calls/ebay', 'update_orders')

NumberOfDays = 0
if response:
    print 'Last time we updated orders was %s' % response
    response = datetime.strptime(response, "%Y-%m-%dT%H:%M:%S.%fZ")
    time_since_last_run = Now - response
    NumberOfDays = time_since_last_run.days
# if response is None, that means we haven't run this script before
else:
    NumberOfDays = 30
    # clear fees in case they exist
    firebase.delete('/', 'orders')

try:
    if NumberOfDays > 0:
        responses = GetOrders(NumberOfDays=NumberOfDays,
                              IncludeFinalValueFee=True
                             )

        for i, response in enumerate(responses):
            response = response.dict()
            print 'PageNumber: %s' % (i + 1)
            print json.dumps(response, sort_keys=True, indent=5)

            if 'OrderArray' in response and 'Order' in response['OrderArray']:
                for order in response['OrderArray']['Order']:
                    firebase.put('/orders', order['OrderID'], order)
except Exception as e:
    raise
else:
    print('successfully retrieved')
    
    # if GetAccount does not raise an exception, update the EndDate
    firebase.put('/api_calls/ebay', 'update_orders', Now.isoformat() + 'Z')
    print('successfully updated')