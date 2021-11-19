import requests
from datetime import datetime

from database import SESSION, Users

def get_balance(adress):
    params = (
            ('module', 'account'),
            ('action', 'tokenbalance'),
            ('contractaddress', '0x079dd74cc214ac5f892f6a7271ef0722f6d0c2e6'),
            ('address', f'{adress}'),
            ('tag', 'latest'),
            ('apikey', 'TX8HVJ5VMY15GQDWM5PRWPXQK76T4RABAB'),
            )

    response = requests.get('https://api.bscscan.com/api', params=params).json()
    if response['result'] == "Invalid address format":
        return "wrong_adress"
    elif response['result'] == "0":
        return 'no nasadoge'
    else:
        return response['result']


def get_transaction_date(txn):
    params = (
        ('module', 'account'),
        ('action', 'txlistinternal'),
        ('txhash', f'{txn}'),
        ('apikey', 'TX8HVJ5VMY15GQDWM5PRWPXQK76T4RABAB'),
        )
    response = requests.get('https://api.bscscan.com/api', params=params).json()
    print(response)
    if response['result']:
        timestamp = int(response['result'][-1].get('timeStamp'))
        return datetime.fromtimestamp(timestamp)


def check_status():
    all_users = SESSION.query(Users).all()
    for user in all_users:
        print(user.raw_balance[:-9], int(get_balance(user.adress)[:-9]))
        if int(user.raw_balance[:-9]) > int(get_balance(user.adress)[:-9]):
            user.is_disqalified = True
            SESSION.commit()
    SESSION.close()
