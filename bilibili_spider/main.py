import json
import requests
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5


class BiliBiliSpider:
    def __init__(self, username, password):
        self.username = username
        self.password = password

        self.session = requests.Session()
        self.session.headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
        }

    def login(self):
        challenge, gt, key = self.geetest_register()
        result = self.geetest_recognize(challenge, gt, 'https://passport.bilibili.com/login')
        hash_value, public_key = self.get_key()
        password = self.encrypt(self.password, hash_value, public_key)
        self.login_post(password, result['challenge'], result['validate'], key)

    def geetest_register(self):
        url = 'https://passport.bilibili.com/web/captcha/combine?plat=6'
        response = self.session.get(url=url)
        data = json.loads(response.text)['data']['result']
        return data['challenge'], data['gt'], data['key']

    def geetest_recognize(self, challenge, gt, referer):
        url = 'https://ocr.wsxiangchen.com/backend/gcservice/'
        data = {
            "access_token": "***",
            "challenge": challenge,
            "gt": gt,
            "referer": referer
        }
        response = requests.post(url=url, data=data)
        result = json.loads(response.text)
        if result['code'] == 0:
            return result['data']
        else:
            raise Exception(result['message'])

    def get_key(self):
        url = 'https://passport.bilibili.com/login?act=getkey'
        response = self.session.get(url=url)
        data = json.loads(response.text)
        return data['hash'], data['key']

    @staticmethod
    def encrypt(password, hash_value, key):
        public_key = RSA.importKey(key)
        rsa = PKCS1_v1_5.new(public_key)
        result = base64.b64encode(rsa.encrypt((hash_value + password).encode("utf8"))).decode('utf8')
        return result

    def login_post(self, password, challenge, validate, key):
        url = 'https://passport.bilibili.com/web/login/v2'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'passport.bilibili.com',
            'Origin': 'https://passport.bilibili.com',
            'Referer': 'https://passport.bilibili.com/login',
        }
        data = {
            "captchaType": "6",
            "username": self.username,
            "password": password,
            "keep": "true",
            "key": key,
            "goUrl": "",
            "challenge": challenge,
            "validate": validate,
            "seccode": "{}|jordan".format(validate)
        }
        response = self.session.post(url=url, headers=headers, data=data)
        print(response.text)


if __name__ == '__main__':
    BiliBiliSpider('123456', '123456').login()
