import re
import sys
import json
import argparse
import datetime

from ebaysdk.exception import ConnectionError
from ebaysdk.trading import Connection as Trading
from firebase import firebase


class GetAccount:

    def __init__(self, firebase_url, invoiceDate = None):
        self.firebase_url = firebase_url
        self.Trading = Trading()
        self.firebase = firebase.FirebaseApplication(self.firebase_url, None)

    def _parseGetAccount(self, response):
        AccountEntries = response.dict()['AccountEntries']['AccountEntry']

        for i, AccountEntry in enumerate(AccountEntries):
            refNumber = AccountEntry['RefNumber']
            # if refNumber is 0, it's not associated with an item
            if refNumber == '0':
                invoiceDate = response.dict()['AccountSummary']['InvoiceDate']
                invoiceDate_regex = re.match('^([0-9]{4}-[0-9]{2}-[0-9]{2})T', invoiceDate)
                if invoiceDate_regex:
                    invoiceDate = invoiceDate_regex.group(1)
                else:
                    raise Exception('invoice Date %s does not match' % invoiceDate)
                self.firebase.post('/fees/byInvoiceDate/%s' % invoiceDate, AccountEntry)
            else:
                self.firebase.put('/fees/byRefNumber', refNumber, AccountEntry)

    def getInvoiceByInvoiceDate(self, invoiceDate):

        if not invoiceDate:
            raise Exception('getInvoiceByInvoiceDate requires invoiceDate')

        PageNumber = 1
        NumExecutions = 1

        while True:
            try:
                response = self.Trading.execute('GetAccount', {
                    'AccountHistorySelection': 'SpecifiedInvoice',
                    'InvoiceDate': '%sT06:59:59.000Z' % invoiceDate,
                    'Pagination': { 'EntriesPerPage': '1000', 'PageNumber': str(PageNumber) }
                })
                print str(PageNumber)
                # safety measure to make sure we dont have an infinite loop
                NumExecutions += 1
                if NumExecutions > 10:
                    break

                self._parseGetAccount(response)

                if 'HasMoreEntries' in response.dict():
                    if response.dict()['HasMoreEntries'] == "true":
                        PageNumber += 1
                    else:
                        break
                else:
                    break

            except ConnectionError as e:
                sys.stderr.write(json.dumps(e.response.dict()) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--firebase_url', help='firebase url', default='https://theprofitlogger.firebaseio.com')
    parser.add_argument('--invoice_date', help='invoice date', default='2016-02-29')
    args = parser.parse_args()

    getAccount = GetAccount(args.firebase_url, invoiceDate=args.invoice_date)
    getAccount.getInvoiceByInvoiceDate('2016-02-29')
