import json
import hmac
import hashlib
import time
import requests
from requests.auth import AuthBase

API_KEY = 'fFoAaKccC8ahVH5G'
API_SECRET = 'ojE8IWjpjSY192A0OgKLgzA34sWEFMB6'

#Get ACCOUNT_ID and PAYMENT_METHOD from calling list_payment_methods 
DEPOSIT_ID = '9983c084-c335-52d2-b582-15cc5f5c64e8'
PAYMENT_METHOD = '66134e1a-7978-59bd-acff-2c0c5223a995'

#Amount to deposit and your currency
DEPOSIT_AMOUNT = 10
DEPOSIT_CURRENCY = 'USD'

#Withdrawal Information
BTC_ADDRESS = '31rsoW7vgP8WDqrxEZabdYSVq6VG6xSQjR'
WITHDRAW_CURRENCY = 'BTC'
WITHDRAWAL_ID = '062a2a7e-1067-5358-b5b3-8e27e598d7a1'

#Coinbase API Endpoints
DEPOSIT_ENDPOINT = f'https://api.coinbase.com/v2/accounts/{DEPOSIT_ID}/deposits'
WITHDRAW_ENDPOINT = f'https://api.coinbase.com/v2/accounts/{WITHDRAWAL_ID}/transactions'
PAYMENT_METHOD_ENDPOINT = 'https://api.coinbase.com/v2/payment-methods'
ACCOUNTS_ENDPOINT = 'https://api.coinbase.com/v2/accounts'



#Authenticate with Coinbase API
class CoinbaseWalletAuth(AuthBase):
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key

    def __call__(self, request):
        timestamp = str(int(time.time()))
        message = timestamp + request.method + request.path_url + (request.body or '')
        signature = hmac.new(self.secret_key.encode(), message.encode(), hashlib.sha256).hexdigest()

        request.headers.update({
            'CB-ACCESS-SIGN': signature,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
        })
        return request

#Function to List Accounts - need this for getting WITHDRAWAL_ID
def list_accounts(starting_after=None):
    auth = CoinbaseWalletAuth(API_KEY, API_SECRET)
    url = f"{ACCOUNTS_ENDPOINT}?starting_after={starting_after}" if starting_after else ACCOUNTS_ENDPOINT

    response = requests.get(url, auth=auth)
    data = response.json()

    active_accounts = [account for account in data['data'] if float(account['balance']['amount']) > 0]

    print_custom_accounts(active_accounts)

    if data['pagination']['next_starting_after']:
        list_accounts(starting_after=data['pagination']['next_starting_after'])

def print_custom_accounts(accounts):
    for account in accounts:
        print(f"WITHDRAWAL_ID: {account['id']}")
        print(f"Name: {account['name']}")
        print(f"Amount: {account['balance']['amount']}")

        native_balance = account['native_balance']
        print(f"Native Balance: {native_balance['amount']} {native_balance['currency']}\n")

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
        print(f'You withdrew {amount} {WITHDRAW_CURRENCY} from your Coinbase account!')
        print(response.json())
        return response.json()
    else:
        raise Exception(f'Error: {response.text}')

def lambda_handler(event, context):
    deposit_fiat(DEPOSIT_AMOUNT)
    
#list_accounts()
withdraw_crypto(.0005)