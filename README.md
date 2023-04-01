# Coinbase-API

This code requires a file called config.json in the directory that it is run. 

Config.json should include the following information:

-----START------

{
    "API_KEY": "",
    "API_SECRET": "",
    "DEPOSIT_ID": "",
    "PAYMENT_METHOD": "",
    "DEPOSIT_AMOUNT": 10,
    "DEPOSIT_CURRENCY": "USD",
    "BTC_ADDRESS": "",
    "WITHDRAW_CURRENCY": "BTC",
    "WITHDRAWAL_ID": ""
}


------END-------

API_KEY and API_SECRET are from your Coinbase Account

DEPOSIT_ID and PAYMENT_METHOD can be found by running list_payment_methods()

WITHDRAWAL_ID can be found by running list_accounts()
