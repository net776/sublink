import os
import time
import uuid
import urllib3

from base64 import b64decode
from Telegram_bot import send_message

import requests
import base64
import json
import pyaes
import binascii
from datetime import datetime

if __name__ == '__main__':
    # 获取环境变量
    地址 = os.environ['skr_a']
    请求数据 = os.environ['skr_c']
    密钥 = os.environ['skr_d']
    初始化向量 = os.environ['skr_e']

    # 请求头
    请求头 = {
        'accept': '/',
        'accept-language': 'zh-Hans-CN;q=1, en-CN;q=0.9',
        'appversion': '1.3.1',
        'user-agent': 'SkrKK/1.3.1 (iPhone; iOS 13.5; Scale/2.00)',
        'content-type': 'application/x-www-form-urlencoded',
        'Cookie': 'PHPSESSID=fnffo1ivhvt0ouo6ebqn86a0d4'
    }

    # AES解密函数
    def 解密(加密数据, 密钥, 初始化向量):
        aes = pyaes.AESModeOfOperationCBC(密钥, iv=初始化向量)
        解密数据 = b''.join(aes.decrypt(加密数据[i:i+16]) for i in range(0, len(加密数据), 16))
        return 解密数据[:-解密数据[-1]]

    # 发送POST请求
    响应 = requests.post(地址, headers=请求头, data=请求数据)
    订阅链接 = ''
    if 响应.status_code == 200:
        响应文本 = 响应.text.strip()
        解密后的数据 = binascii.unhexlify(响应文本)
        解密后的文本 = 解密(解密后的数据, 密钥.encode(), 初始化向量.encode())
        数据 = json.loads(解密后的文本)
        for 项目 in 数据['data']:
            ss链接 = f"aes-256-cfb:{项目['password']}@{项目['ip']}:{项目['port']}"
            base64编码 = base64.b64encode(ss链接.encode('utf-8')).decode('utf-8')
            完整链接 = f"ss://{base64编码}#{项目['title']}"
            订阅链接 += 完整链接 + '\n'
        print(订阅链接)
        with open("./links/skr", "w") as 文件:
            文件.write(base64.b64encode(订阅链接.encode()).decode())
        消息 = '#ss ' + '#订阅' + '\n' + datetime.now().strftime("%Y年%m月%d日%H:%M:%S") + '\n' + 'skr订阅每天自动更新：' + '\n' + 'https://raw.githubusercontent.com/mfbpn/TrojanLinks/master/links/skr'
        send_message(os.environ['chat_id'], 消息, os.environ['bot_token'])
