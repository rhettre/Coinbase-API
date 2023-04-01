import http.client
import hmac
import hashlib
import json
import time
import base64
import uuid
from enum import Enum
import math

# Set API key and secret key to conenct to your Coinbase account
api_key = 'fFoAaKccC8ahVH5G'
api_secret = 'ojE8IWjpjSY192A0OgKLgzA34sWEFMB6'
creds = [api_key, api_secret]


class Side(Enum):
    BUY = 1
    SELL = 0


class Method(Enum):
    POST = 1
    GET = 0


def generate_client_order_id():
    return uuid.uuid4()


def coinbase_request(method, path, body):

    # Set URL and request path/api/v3/brokerage/accounts/"
    conn = http.client.HTTPSConnection("api.coinbase.com")

    # Generate timestamp
    timestamp = str(int(time.time()))
    message = timestamp + method + path.split('?')[0] + str(body)
    signature = hmac.new(creds[1].encode(
        'utf-8'), message.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()

    # Set headers
    headers = {
        "accept": "application/json",
        "CB-ACCESS-KEY": creds[0],
        "CB-ACCESS-SIGN": signature,
        "CB-ACCESS-TIMESTAMP": timestamp
    }

    # Send request
    conn.request(method, path, body, headers)

    # Get response
    res = conn.getresponse()
    data = res.read()

    # Parse response data as JSON
    response_data = json.loads(data.decode("utf-8"))

    # Print response data in a more readable format
    print(json.dumps(response_data, indent=2))
    return response_data


def placeLimitOrder(side, pair, size, limit_price):
    method = Method.POST.name
    path = f'/api/v3/brokerage/orders'
    payload = json.dumps({
        "client_order_id": str(generate_client_order_id()),
        "side": side,
        "product_id": pair,
        "order_configuration": {
            "limit_limit_gtc": {
                "post_only": False,
                "limit_price": limit_price,
                "base_size": size
            }
        }
    })
    coinbase_request(method, path, payload)

# Use this function to get all available product info


def getAllProductInfo():
    method = Method.GET.name
    path = f'/api/v3/brokerage/products'
    payload = ''
    response = coinbase_request(method, path, payload)
    for product in response['products']:
        print(product['product_id'])


def getProductInfo(pair):
    method = Method.GET.name
    path = f'/api/v3/brokerage/products/{pair}'
    payload = ''
    response = coinbase_request(method, path, payload)
    return {"price": response['price'],
            "quote_increment": response['quote_increment'],
            "base_increment": response['base_increment']}


def tester():
    # Your trading side (buy or sell)
    my_side = Side.SELL.name
    # Your trading pair
    my_trading_pair = "BTC-USD"
    # The USD or other base currency size of your order
    usd_order_size = 5
    # factor is used to set your limit order close to the spot price for quick execution to take advantage of the maker fee structure
    factor = .998
    if my_side == Side.SELL.name:
        factor = 1.002

    # --Calculated Fields | Do Not Change--
    productInfo = getProductInfo(my_trading_pair)
    quote_currency_price_increment = abs(
        round(math.log(float(productInfo['quote_increment']), 10)))
    base_currency_price_increment = abs(
        round(math.log(float(productInfo['base_increment']), 10)))
    # --------------------------------------

    # Your Limit Price
    my_limit_price = str(
        round(float(productInfo['price']) * factor, quote_currency_price_increment))
    # Your Order Size in the quoted currency (ie .0001 BTC)
    my_order_size = str(
        round(usd_order_size/float(my_limit_price), base_currency_price_increment))

    # Place the limit order
    placeLimitOrder(my_side, my_trading_pair, my_order_size, my_limit_price)

    # Print some information
    print(f'The spot price of {my_trading_pair} is ${productInfo["price"]}')
    print(f"Your limit price is {my_limit_price}")
    print(f"Your order size is {my_order_size}")

    return {
        'statusCode': 200,
        'body': json.dumps('End of script.')
    }


tester()
