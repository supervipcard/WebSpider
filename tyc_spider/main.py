import json
import hashlib
import requests


class TycSpider:
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
        challenge, gt = self.geetest_register()
        result = self.geetest_recognize(challenge, gt, 'https://www.tianyancha.com')
        self.login_post(result['challenge'], result['validate'])

    def geetest_register(self):
        url = 'https://www.tianyancha.com/verify/geetest.xhtml'
        headers = {
            'Content-Type': 'application/json; charset=UTF-8'
        }
        response = self.session.post(url=url, headers=headers)
        data = json.loads(response.text)['data']
        return data['challenge'], data['gt'],

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

    @staticmethod
    def encrypt(password):
        md = hashlib.md5()
        md.update(password.encode('utf-8'))
        result = md.hexdigest()
        return result

    def login_post(self, challenge, validate):
        url = 'https://www.tianyancha.com/cd/login.json'
        headers = {
            'Content-Type': 'application/json; charset=UTF-8',
        }
        data = {
            "mobile": self.username,
            "cdpassword": self.encrypt(self.password),
            "loginway": "PL",
            "autoLogin": True,
            "challenge": challenge,
            "validate": validate,
            "seccode": "{}|jordan".format(validate)
        }
        response = self.session.post(url=url, headers=headers, data=json.dumps(data, separators=(',', ':')))
        print(response.text)


if __name__ == '__main__':
    TycSpider('***', '***').login()
