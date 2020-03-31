import json
import execjs
import base64
import requests

from weibo_spider.cnn.client import Caller


class WeiBoSpider:
    def __init__(self, username, password):
        self.username = username
        self.password = password

        with open('rsa.js', 'r', encoding='utf8') as f:
            source = f.read()
        external_runtime = execjs.get()
        self.context = external_runtime.compile(source)

        self.session = requests.Session()
        self.headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
        }
        self.caller = Caller()

    def login(self):
        first_login_result = self.first_login(self.prelogin())
        print(first_login_result)
        if first_login_result['retcode'] == '0':
            second_login_result = self.second_login(first_login_result['ticket'])
            print(second_login_result)
        else:
            raise Exception(first_login_result['reason'])

    def prelogin(self):
        url = 'https://login.sina.com.cn/sso/prelogin.php'
        params = {
            'entry': 'weibo',
            'su': base64.b64encode(self.username.encode('utf8')),
            'rsakt': 'mod',
            'checkpin': '1',
            'client': 'ssologin.js(v1.4.19)',
        }
        response = self.session.get(url=url, params=params)
        return json.loads(response.text)

    def get_captcha(self, pcid):
        """获取和自动识别验证码图片"""
        url = 'https://login.sina.com.cn/cgi/pin.php?p={}'.format(pcid)
        response = self.session.get(url=url)
        with open('captcha.jpg', 'wb') as f:
            f.write(response.content)
        return self.caller.run(response.content)

    def first_login(self, prelogin_result):
        servertime = prelogin_result['servertime']
        pcid = prelogin_result['pcid']
        nonce = prelogin_result['nonce']
        pubkey = prelogin_result['pubkey']
        rsakv = prelogin_result['rsakv']

        door = self.get_captcha(pcid)
        # door = input('请输入验证码：')

        sp = self.context.call('f1', pubkey, servertime, nonce, self.password)

        url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'
        data = {
            'entry': 'weibo',
            'gateway': '1',
            'from': '',
            'savestate': '7',
            'qrcode_flag': 'false',
            'useticket': '1',
            'pagerefer': '',
            'pcid': pcid,
            'door': door,
            'vsnf': '1',
            'su': base64.b64encode(self.username.encode('utf8')),
            'service': 'miniblog',
            'servertime': servertime + 100,
            'nonce': nonce,
            'pwencode': 'rsa2',
            'rsakv': rsakv,
            'sp': sp,
            'sr': '1440*900',
            'encoding': 'UTF-8',
            'cdult': '2',
            'domain': 'weibo.com',
            'prelt': '48',
            'returntype': 'TEXT',
        }
        response = self.session.post(url=url, data=data)
        return json.loads(response.text)

    def second_login(self, ticket):
        url = 'https://passport.weibo.com/wbsso/login'
        params = {
            'ticket': ticket,
            'client': 'ssologin.js(v1.4.19)',
        }
        response = self.session.get(url=url, params=params)
        return json.loads(response.text.strip()[1: -2])


if __name__ == '__main__':
    WeiBoSpider('***', '***').login()
