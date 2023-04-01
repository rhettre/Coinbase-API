import json
import hmac
import hashlib
import time
import requests
from requests.auth import AuthBase

# Load sensitive information from config.json
with open('config.json') as config_file:
    config = json.load(config_file)

API_KEY = config['API_KEY']
API_SECRET = config['API_SECRET']
DEPOSIT_ID = config['DEPOSIT_ID']
PAYMENT_METHOD = config['PAYMENT_METHOD']
DEPOSIT_AMOUNT = config['DEPOSIT_AMOUNT']
DEPOSIT_CURRENCY = config['DEPOSIT_CURRENCY']
BTC_ADDRESS = config['BTC_ADDRESS']
WITHDRAW_CURRENCY = config['WITHDRAW_CURRENCY']
WITHDRAWAL_ID = config['WITHDRAWAL_ID']

# Coinbase API Endpoints
DEPOSIT_ENDPOINT = f'https://api.coinbase.com/v2/accounts/{DEPOSIT_ID}/deposits'
WITHDRAW_ENDPOINT = f'https://api.coinbase.com/v2/accounts/{WITHDRAWAL_ID}/transactions'
PAYMENT_METHOD_ENDPOINT = 'https://api.coinbase.com/v2/payment-methods'
ACCOUNTS_ENDPOINT = 'https://api.coinbase.com/v2/accounts'

# Authenticate with Coinbase API


class CoinbaseWalletAuth(AuthBase):
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key

    def __call__(self, request):
        timestamp = str(int(time.time()))
        message = timestamp + request.method + \
            request.path_url + (request.body or '')
        signature = hmac.new(self.secret_key.encode(),
                             message.encode(), hashlib.sha256).hexdigest()

        request.headers.update({
            'CB-ACCESS-SIGN': signature,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
        })
        return request

# Function to List Payment Methods - need this for getting Account_ID and Payment_Method


def list_payment_methods():
    auth = CoinbaseWalletAuth(API_KEY, API_SECRET)
    response = requests.get(PAYMENT_METHOD_ENDPOINT, auth=auth)
    data = response.json()

    payment_methods = [{
        'id': item['fiat_account']['id'] if item['type'] == 'fiat_account' else item['id'],
        'name': item['name'],
        'currency': item['currency'],
        'type': item['type'],
        'description': (item['limits']['buy'][0]['description']
                        if 'limits' in item and 'buy' in item['limits'] and item['limits']['buy']
                        else None)
    } for item in data['data']]

    for method in payment_methods:
        print(method)

# Function to Deposit USD


def deposit_fiat(amount):
    auth = CoinbaseWalletAuth(API_KEY, API_SECRET)
    data = {
        'type': 'deposit',
        'amount': amount,
        'currency': DEPOSIT_CURRENCY,
        'payment_method': PAYMENT_METHOD
    }

    response = requests.post(DEPOSIT_ENDPOINT, data=data, auth=auth)
    if response.status_code == 201:
        print(
            f'You deposited {amount} {DEPOSIT_CURRENCY} into your Coinbase account!')
        print(response.json())
        return response.json()
    else:
        raise Exception(f'Error: {response.text}')

# Function to List Accounts - need this for getting WITHDRAWAL_ID


def list_accounts(starting_after=None):
    auth = CoinbaseWalletAuth(API_KEY, API_SECRET)
    url = f"{ACCOUNTS_ENDPOINT}?starting_after={starting_after}" if starting_after else ACCOUNTS_ENDPOINT

    response = requests.get(url, auth=auth)
    data = response.json()

    active_accounts = [account for account in data['data']
                       if float(account['balance']['amount']) > 0]

    print_custom_accounts(active_accounts)

    if data['pagination']['next_starting_after']:
        list_accounts(starting_after=data['pagination']['next_starting_after'])


def print_custom_accounts(accounts):
    for account in accounts:
        print(f"WITHDRAWAL_ID: {account['id']}")
        print(f"Name: {account['name']}")
        print(f"Amount: {account['balance']['amount']}")

        native_balance = account['native_balance']
        print(
            f"Native Balance: {native_balance['amount']} {native_balance['currency']}\n")


def withdraw_crypto(amount):
    auth = CoinbaseWalletAuth(API_KEY, API_SECRET)
    data = {
        'type': 'send',
        'to': BTC_ADDRESS,
        'amount': amount,
        'currency': WITHDRAW_CURRENCY
    }

    response = requests.post(WITHDRAW_ENDPOINT, data=data, auth=auth)
    if response.status_code == 201:
        print(
            f'You withdrew {amount} {WITHDRAW_CURRENCY} from your Coinbase account!')
        print(response.json())
        return response.json()
    else:
        raise Exception(f'Error: {response.text}')


def lambda_handler(event, context):
    list_payment_methods()
    deposit_fiat(DEPOSIT_AMOUNT)
    list_accounts()
    withdraw_crypto(.0005)
