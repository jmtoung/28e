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

    if update_firebase and not firebase_url:
        raise Exception('if --update_firebase set to True, --firebase_url is required')

    fb = None
    if update_firebase:
        fb = firebase.FirebaseApplication(firebase_url, None)

    trading = Trading()
    num_executions = 0
    options['Pagination'] = { 'EntriesPerPage': '1000', 'PageNumber': 0 }
    has_more = True

    while has_more and num_executions < 10:
        try:
            options['Pagination']['PageNumber'] += 1
            response = trading.execute('GetAccount', options).dict()

            # safety measure to make sure we dont have an infinite loop
            num_executions += 1

            print 'PageNumber: %s' % options['Pagination']['PageNumber']
            print json.dumps(response, sort_keys=True, indent=5)

            if update_firebase:
                _add_account_entry_to_firebase(response, fb)

            has_more = response.get('HasMoreEntries') == "true"

        except ConnectionError as e:
            sys.stderr.write(json.dumps(e.response) + "\n")
            break

def _add_account_entry_to_firebase(response, fb):

    for entry in response['AccountEntries']['AccountEntry']:

        ref_number = entry['RefNumber']
        # if ref_number is 0, it's not associated with an item
        if ref_number == '0':
            invoice_date = response['AccountSummary']['InvoiceDate']
            invoice_date_regex = re.match('^([0-9]{4}-[0-9]{2}-[0-9]{2})T', invoice_date)
            if invoice_date_regex:
                invoice_date = invoice_date_regex.group(1)
            else:
                raise Exception('invoice Date %s does not match' % invoice_date)
            fb.post('/fees/byInvoiceDate/%s' % invoice_date, entry)
        else:
            fb.put('/fees/byRefNumber', ref_number, entry)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--AccountHistorySelection', type=str, choices=AccountHistorySelection_types, default=AccountHistorySelection_types[1])
    parser.add_argument('--InvoiceDate', type=str)
    parser.add_argument('--update_firebase', action="store_true")
    parser.add_argument('--firebase_url', help='firebase url', default='https://theprofitlogger.firebaseio.com')
    args = parser.parse_args()

    sys.exit(GetAccount(
        AccountHistorySelection=args.AccountHistorySelection,
        InvoiceDate=args.InvoiceDate,
        update_firebase=args.update_firebase,
        firebase_url=args.firebase_url
    ))
