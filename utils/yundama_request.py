import os
import json

import requests


class YDMRequest:
    API_URL = 'http://api.yundama.com/api.php'
    USERNAME = os.environ['YUNDAMA_USERNAME']
    PASSWORD = os.environ['YUNDAMA_PASSWORD']
    APP_ID = os.environ['YUNDAMA_APP_ID']
    APP_KEY = os.environ['YUNDAMA_APP_KEY']

    @classmethod
    def balance(cls):
        """查询余额"""
        res = requests.post(cls.API_URL, data={
            'method': 'balance',
            'username': cls.USERNAME,
            'password': cls.PASSWORD,
            'appid': cls.APP_ID,
            'appkey': cls.APP_KEY
        })
        json_res = json.loads(res.text)
        if json_res['ret'] == 0:
            return json_res['balance']
        return None

    @classmethod
    def login(cls):
        res = requests.post(cls.API_URL, data={
            'method': 'login',
            'username': cls.USERNAME,
            'password': cls.PASSWORD,
            'appid': cls.APP_ID,
            'appkey': cls.APP_KEY
        })
        json_res = json.loads(res.text)
        if json_res['ret'] == 0:
            return json_res['uid']
        return None

    @classmethod
    def decode(cls, filename: str, code_type: int, timeout: int = 60):
        """识别验证码"""
        files = {'file': open(filename, 'rb')}
        res = requests.post(cls.API_URL, files=files, data={
            'method': 'upload',
            'username': cls.USERNAME,
            'password': cls.PASSWORD,
            'appid': cls.APP_ID,
            'appkey': cls.APP_KEY,
            'codetype': str(code_type),
            'timeout': str(timeout)
        })
        json_res = json.loads(res.text)
        print(f'decode result = {json_res}')
        if json_res['ret'] == 0:
            return json_res['text']
        return None

