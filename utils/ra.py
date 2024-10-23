import requests
import json
import base64
import random
import string
import urllib.parse
import os
from Telegram_bot import send_message

def uuid_a():
    characters = string.ascii_lowercase + string.digits
    random_string = ''.join(random.choice(characters) for i in range(8))
    return random_string

def register(base_url, register):
    register_url = f"{base_url}/auth/register"
    headers = {
        'user-agent': 'Dart/3.5 (dart:io)',
        'accept-language': 'en-US',
        'accept-encoding': 'gzip',
        'host': 'api.radial.velolink.us',
        'authorization': 'Bearer ',
        'content-type': 'application/json',
    }
    response = requests.post(register_url, headers=headers, json=register_data)
    if response.status_code == 200:
        token=response.json()['data']
    else:
        token = None
    return token

def post_data(base_url, token, endpoint, json_data):
    global SS_link
    
    if token is None:
        print("Failed to login")
        return
    url = f"{base_url}{endpoint}"
    tt=f'Bearer {token}'
    headers = {
        'user-agent': 'Dart/3.5 (dart:io)',
        'accept-language': 'en-US',
        'accept-encoding': 'gzip',
        'content-length': '12',
        'device': 'iPhone',
        'host': 'api.radial.velolink.us',
        'authorization': tt,
        'content-type': 'application/json',
    }
    response = requests.post(url, data=json.dumps(json_data), headers=headers)
    for item in response.json()['data']:
        node = item['node']
        attributes = item['attributes']
        link_format = "{method}:{password}@{hostname}:{port}".format(
            method=attributes['method'],
            password=attributes['passwd'],
            hostname=node['address'],
            port=attributes['port'])
        ss_link_unencoded = "ss://" + base64.urlsafe_b64encode(link_format.encode()).decode()
        ss_link = ss_link_unencoded + "#" + urllib.parse.quote(node['name'])
        SS_link += ss_link + '\n'
        # print(ss_link)
    
    
if __name__ == "__main__":
    SS_link = ''
    pws = uuid_a()
    email = f"{pws}@163.com"
    base_url = "https://api.radial.velolink.us"
    register_data = {'email': email, 'password': pws, 'invite': ""}
    token = register(base_url, register_data)
    try:
        for i in range(1,7):
            json_data = {"region": i}
            endpoint = "/user/node/credential"
            post_data(base_url, token, endpoint, json_data)
    except Exception as e:
        print(e)
    print(SS_link)
    with open("./links/ra", "w") as f:
        f.write(base64.b64encode(SS_link.encode()).decode())
    message = '#SS ' + '#订阅' + '\n' + datetime.now().strftime("%Y年%m月%d日%H:%M:%S") + '\n' + 'RA订阅每天自动更新：' + '\n' + 'https://raw.githubusercontent.com/mfbpn/sublink/master/links/fn'
    send_message(os.environ['chat_id'], message, os.environ['bot_token'])

