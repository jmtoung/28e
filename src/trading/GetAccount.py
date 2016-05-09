import re
import sys
import json
import argparse
import datetime

from ebaysdk.exception import ConnectionError
from ebaysdk.trading import Connection as Trading

AccountHistorySelection_types = ('BetweenSpecifiedDates', 'LastInvoice', 'SpecifiedInvoice')

def GetAccount(
        AccountHistorySelection=None,
        BeginDate=None,
        EndDate=None,
        InvoiceDate=None
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
    options['Pagination'] = { 'EntriesPerPage': '2000', 'PageNumber': 0 }
    has_more = True

    while has_more:
        options['Pagination']['PageNumber'] += 1
        
        try:
            response = trading.execute('GetAccount', options)
        except ConnectionError as e:
            raise Exception('ConnectionError:\n%s ' % json.dumps(e.response.dict(), sort_keys=True, indent=5))
        else:
            yield response

        has_more = response.dict().get('HasMoreEntries') == "true"

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