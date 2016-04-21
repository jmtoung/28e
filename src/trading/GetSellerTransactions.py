import datetime
from ebaysdk.exception import ConnectionError
from ebaysdk.trading import Connection as Trading

try:
    api = Trading()
    response = api.execute('GetSellerTransactions')
    
    fh = open('output.txt', 'wb')
    transactions = response.dict()['TransactionArray']['Transaction']
    header = ['i', 'PayPalEmailAddress', 'TransactionPrice', 'BuyerName', 'ItemID', 'ItemName']
    
    fh.write("\t".join(header) + "\n")
    for i, transaction in enumerate(transactions):
        result = [i]
        result.append(transaction['PayPalEmailAddress'])
        result.append(transaction['TransactionPrice']['value'])
        name = 'NA'
        if 'Name' in transaction['Buyer']['BuyerInfo']['ShippingAddress']:
            name = transaction['Buyer']['BuyerInfo']['ShippingAddress']['Name']
        result.append(name)
        itemID = transaction['Item']['ItemID']
        result.append(itemID)
        try:
            response2 = api.execute('GetItem', {'ItemID': itemID})
            for y in response2.dict()['Item']:
                print "****\t", "\t", "\t", y, response2.dict()['Item'][y]
            result.append(response2.dict()['Item']['Title'])
        except ConnectionError as e:
            print(e)
            print(e.response.dict())
        for x in transaction:
            print "\t", x, "\t", transaction[x]
        result = [str(x) for x in result]
        fh.write("\t".join(result) + "\n")
#    assert(response.reply.ack == 'Success')
#    assert(type(response.reply.timestamp) == datetime.datetime)
#    assert(type(response.reply.searchResult.item) == list)

#    item = response.reply.searchResult.item[0]
#    assert(type(item.listingInfo.endTime) == datetime.datetime)
#    assert(type(response.dict()) == dict)

except ConnectionError as e:
    print(e)
    print(e.response.dict())