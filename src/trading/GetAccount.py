import re
import sys
import json
import argparse
import datetime

from ebaysdk.exception import ConnectionError
from ebaysdk.trading import Connection as Trading
from firebase import firebase

AccountHistorySelection_types = ('BetweenSpecifiedDates', 'LastInvoice', 'SpecifiedInvoice')

def GetAccount(
        AccountHistorySelection=None,
        BeginDate=None,
        EndDate=None,
        InvoiceDate=None,
        update_firebase=False,
        firebase_url=None
    ):

    options = {}
    # make sure AccountHistorySelection is provided and is valid
    if AccountHistorySelection not in AccountHistorySelection_types:
        raise Exception('--AccountHistorySelection is required; valid types are %s' % " ".join(AccountHistorySelection_types))
    options['AccountHistorySelection'] = AccountHistorySelection

    if AccountHistorySelection=="BetweenSpecifiedDates":
        if not (BeginDate and EndDate):
            raise Exception('--BeginDate and --EndDate are required if --AccountHistorySelection is BetweenSpecifiedDates')
        options['BeginDate'] = BeginDate
        options['EndDate'] = EndDate
    elif AccountHistorySelection=="SpecifiedInvoice":
        if not InvoiceDate:
            raise Exception('--InvoiceDate is required if --AccountHistorySelection is SpecifiedInvoice')
        options['InvoiceDate'] = InvoiceDate

    trading = Trading()
    num_executions = 0
    options['Pagination'] = { 'EntriesPerPage': '1000', 'PageNumber': 0 }
    has_more = True

    while has_more and num_executions < 10:
        options['Pagination']['PageNumber'] += 1
        
        try:
            response = trading.execute('GetAccount', options).dict()
        except ConnectionError as e:
            raise Exception(json.dumps(e.response.dict(), sort_keys=True, indent=5))
            break

        # safety measure to make sure we dont have an infinite loop
        num_executions += 1

        print 'PageNumber: %s' % options['Pagination']['PageNumber']
        print json.dumps(response, sort_keys=True, indent=5)

        has_more = response.get('HasMoreEntries') == "true"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--AccountHistorySelection', type=str, choices=AccountHistorySelection_types)
    parser.add_argument('--BeginDate', type=str)
    parser.add_argument('--EndDate', type=str)
    parser.add_argument('--InvoiceDate', type=str)
    args = parser.parse_args()

    sys.exit(GetAccount(
        AccountHistorySelection=args.AccountHistorySelection,
        BeginDate=args.BeginDate,
        EndDate=args.EndDate,
        InvoiceDate=args.InvoiceDate
    ))