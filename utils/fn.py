'''
By: unorz
'''
import time
import hashlib
import base64
import os
import pyaes
import requests
from urllib.parse import quote
from Telegram_bot import send_message

def get_request_key(t, i, k):
    ts = str(t)
    r = [5,11,11,8,27,12,9,21] if t & 1 != 0 else [16,8,10,12,26,11,2,18]
    key = i[r[0]]+i[r[1]]+ts[r[2]]+i[r[3]]+i[r[4]]+ts[r[5]]+i[r[6]]+i[r[7]]
    key += k[int(ts[11])] if len(k) else i[int(ts[11])]
    return key

def get_decrypt_key(t, i, k):
    ts = str(t)
    r = [5,11,11,8,27,12,9,21] if t & 1 != 0 else [16,8,10,12,26,11,2,18]
    key = i[r[0]]+i[r[1]]+ts[r[2]]+i[r[3]]+i[r[4]]+ts[r[5]]+i[r[6]]+i[r[7]]
    key += k[r[0]]+k[r[1]]+ts[r[2]]+k[r[3]]+k[r[4]]+ts[r[5]]+k[r[6]]+k[r[7]]
    return key

def timestamp():
    return int(time.time() * 1000)

def gen_req_id():
    t = int(time.time() / 1800)
    return hashlib.md5(f'req_id_{t}'.encode()).hexdigest()

def gen_serial_num():
    t = int(time.time() * 1000)
    return hashlib.md5(f'serial_num_{t}'.encode()).hexdigest()

def aes_decrypt(key, text):
    textbytes = base64.b64decode(text)
    decrypter = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(key.encode(), b'A-16-Byte-String'))
    plainbytes = decrypter.feed(textbytes)
    plainbytes += decrypter.feed()
    return plainbytes.decode('utf-8')

def prepare_params(params):
    params['clientModel'] = 'V1936A'
    params['clientType'] = 'Android'
    params['promoteChannel'] = 'S100'
    params['rankVersion'] = '10'
    params['version'] = 'v2.0.4'
    params = dict(sorted(params.items()))
    param_str = ''
    for k in params.keys():
        param_str += f'{k}={params[k]}&'
    param_str = param_str.rstrip('&')
    sign_key = get_request_key(params['requestTimestamp'], params['requestId'], params.get('token', ''))
    params['sign'] = hashlib.md5(f'{param_str}{sign_key}'.encode()).hexdigest()
    return params

session = requests.Session()
session.trust_env = False

headers = {
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Linux; U; Android 7.1.2; zh-cn; V1936A Build/N2G47O) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30',
    'Content-Type': 'application/x-www-form-urlencoded'
}
url1 = os.environ['fn_url']
url2 = os.environ['fn_url2']
url3 = os.environ['fn_url3']
def login(serial):
    try:
        params = prepare_params({
            'requestId': gen_req_id(),
            'requestTimestamp': timestamp(),
            'serialNumber': serial
        })
        response = session.post(url1, headers=headers, data=params)
        response.raise_for_status()
        return response.json().get('data').get('token')
    except Exception as e:
        print(f'登录失败：{e}')

def node_list(serial, token):
    try:
        params = prepare_params({
            'requestId': gen_req_id(),
            'requestTimestamp': timestamp(),
            'serialNumber': serial,
            'token': token,
            'vipType': 'vip'
        })
        response = session.post(url2, headers=headers, data=params)
        response.raise_for_status()
        return response.json().get('data')
    except Exception as e:
        print(f'获取节点列表失败：{e}')

def node_detail(serial, token, node_id):
    try:
        t = timestamp()
        rid = gen_req_id()
        params = prepare_params({
            'requestId': rid,
            'requestTimestamp': t,
            'serialNumber': serial,
            'token': token,
            'nodeId': node_id
        })
        response = session.post(url3, headers=headers, data=params)
        response.raise_for_status()
        data = response.json().get('data')
        key = get_decrypt_key(t, rid, token)
        info = aes_decrypt(key, data.get('content')).split(',')
        trojan = f'trojan://{info[3]}@{info[1]}:{info[2]}?security=tls&type=tcp&headerType=none&allowInsecure=1#{quote(data.get("name"))}'
        Trojan += trojan + '\n'
        # print(trojan)
    print(Trojan)
    with open("./links/fn", "w") as f:
    f.write(base64.b64encode(Trojan.encode()).decode())
    # message = '#vless ' + '#订阅' + '\n' + datetime.now().strftime("%Y年%m月%d日%H:%M:%S") + '\n' + 'sd订阅每天自动更新：' + '\n' + 'https://raw.githubusercontent.com/mfbpn/sublink/master/links/sd'
    # send_message(os.environ['chat_id'], message, os.environ['bot_token'])
    except Exception as e:
        print(f'获取节点信息失败：{e}')

if __name__ == "__main__":
    serial = gen_serial_num()
    token = login(serial)
    if token:
        nodes = node_list(serial, token)
        for node in nodes:
            node_detail(serial, token, node.get('id'))

