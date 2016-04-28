import re
import sys
import json
import argparse
import datetime

from ebaysdk.exception import ConnectionError
from ebaysdk.trading import Connection as Trading
from firebase import firebase


def _get_invoice_by_Date(firebase_url, invoice_date=None):
    if not invoice_date:
        raise Exception('get_invoice_by_invoice_Date requires invoice_date')

    trading = Trading()
    fb = firebase.FirebaseApplication(firebase_url, None)
    page_number = 1
    num_executions = 1

    while True:
        print 'Getting account for date %s' % invoice_date
        try:
            response = trading.execute('GetAccount', {
                'AccountHistorySelection': 'SpecifiedInvoice',
                'InvoiceDate': '%sT06:59:59.000Z' % invoice_date,
                'Pagination': { 'EntriesPerPage': '1000', 'PageNumber': str(page_number) }
            })

            # safety measure to make sure we dont have an infinite loop
            num_executions += 1
            if num_executions > 10:
                break

            _parse_get_account(fb, response)

            has_more = response.dict().get('HasMoreEntries') == "true"
            if has_more:
                page_number += 1
            else:
                break

        except ConnectionError as e:
            sys.stderr.write(json.dumps(e.response.dict()) + "\n")

def _parse_get_account(fb, response):
    account_entries = response.dict()['AccountEntries']['AccountEntry']

    for entry in account_entries:
        print 'Sending account entry {0} to Firebase...'.format(entry.get('ItemID'))

        ref_number = entry['RefNumber']
        # if ref_number is 0, it's not associated with an item
        if ref_number == '0':
            invoice_date = response.dict()['AccountSummary']['InvoiceDate']
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
    parser.add_argument('--firebase_url', help='firebase url', default='https://theprofitlogger.firebaseio.com')
    parser.add_argument('--invoice_date', help='invoice date', default='2016-02-29')
    args = parser.parse_args()

    # what about args.invoice_date?
    _get_invoice_by_Date(args.firebase_url, '2016-02-29')
