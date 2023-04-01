import http.client
import hmac
import hashlib
import json
import time
import uuid
from enum import Enum
import math

# Load sensitive information from config.json
with open('config.json') as config_file:
    config = json.load(config_file)

api_key = config['API_KEY']
api_secret = config['API_SECRET']
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
    conn = http.client.HTTPSConnection("api.coinbase.com")
    timestamp = str(int(time.time()))
    message = timestamp + method + path.split('?')[0] + str(body)
    signature = hmac.new(creds[1].encode(
        'utf-8'), message.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()

    headers = {
        "accept": "application/json",
        "CB-ACCESS-KEY": creds[0],
        "CB-ACCESS-SIGN": signature,
        "CB-ACCESS-TIMESTAMP": timestamp
    }

    conn.request(method, path, body, headers)
    res = conn.getresponse()
    data = res.read()
    response_data = json.loads(data.decode("utf-8"))

    print(json.dumps(response_data, indent=2))
    return response_data


def place_limit_order(side, pair, size, limit_price):
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


def get_all_product_info():
    method = Method.GET.name
    path = f'/api/v3/brokerage/products'
    payload = ''
    response = coinbase_request(method, path, payload)
    for product in response['products']:
        print(product['product_id'])


def get_product_info(pair):
    method = Method.GET.name
    path = f'/api/v3/brokerage/products/{pair}'
    payload = ''
    response = coinbase_request(method, path, payload)
    return {"price": response['price'],
            "quote_increment": response['quote_increment'],
            "base_increment": response['base_increment']}


def tester():
    my_side = Side.SELL.name
    my_trading_pair = "BTC-USD"
    usd_order_size = 5
    factor = .998 if my_side == Side.SELL.name else 1.002

    product_info = get_product_info(my_trading_pair)
    quote_currency_price_increment = abs(
        round(math.log(float(product_info['quote_increment']), 10)))
    base_currency_price_increment = abs(
        round(math.log(float(product_info['base_increment']), 10)))

    my_limit_price = str(
        round(float(product_info['price']) * factor, quote_currency_price_increment))
    my_order_size = str(
        round(usd_order_size/float(my_limit_price), base_currency_price_increment))

    place_limit_order(my_side, my_trading_pair, my_order_size, my_limit_price)

    print(f'The spot price of {my_trading_pair} is ${product_info["price"]}')
    print(f"Your limit price is {my_limit_price}")
    print(f"Your order size is {my_order_size}")

    return {
        'statusCode': 200,
        'body': json.dumps('End of script.')
    }


tester()
