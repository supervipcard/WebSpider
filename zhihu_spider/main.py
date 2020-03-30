import time
import json
import base64
import execjs
import requests
from urllib.parse import urlencode
from hashlib import sha1
import hmac

from requests_toolbelt import MultipartEncoder


class ZhiHuSpider:
    def __init__(self):
        with open('enc.js', 'r', encoding='utf8') as f:
            source = f.read()
        node = execjs.get('Node')  # PhantomJS/JScript
        self.context = node.compile(source)

        self.session = requests.Session()
        self.session.headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Host': 'www.zhihu.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
        }

    def login(self, username, password):
        self.signin_get()
        self.captcha_get()
        self.captcha_put()
        self.captcha_post()
        self.sign_in_post(username, password)

    def signin_get(self):
        url = 'https://www.zhihu.com/signin'
        self.session.get(url=url)

    def captcha_get(self):
        url = 'https://www.zhihu.com/api/v3/oauth/captcha?lang=en'
        headers = {
            'Referer': 'https://www.zhihu.com/signin',
            'x-requested-with': 'fetch',
            'X-Zse-83': '3_2.0',
        }
        response = self.session.get(url=url, headers=headers)
        print(response.text)

    def captcha_put(self):
        url = 'https://www.zhihu.com/api/v3/oauth/captcha?lang=en'
        headers = {
            'Origin': 'https://www.zhihu.com',
            'Referer': 'https://www.zhihu.com/signin',
            'x-requested-with': 'fetch',
            'X-Zse-83': '3_2.0',
        }
        response = self.session.put(url=url, headers=headers)
        print(response.text)
        img_base64 = json.loads(response.text)['img_base64']
        with open('captcha.jpg', 'wb') as f:
            f.write(base64.b64decode(img_base64))

    def captcha_post(self):
        input_text = input('请输入验证码：')
        url = 'https://www.zhihu.com/api/v3/oauth/captcha?lang=en'
        params = {'input_text': input_text}
        data = MultipartEncoder(fields=params, boundary='----WebKitFormBoundary')
        headers = {
            'Content-Type': data.content_type,
            'Origin': 'https://www.zhihu.com',
            'Referer': 'https://www.zhihu.com/signin',
            'x-requested-with': 'fetch',
        }
        response = self.session.post(url=url, headers=headers, data=data)
        print(response.text)

    def sign_in_post(self, username, password):
        client_id = 'c3cef7c66a1843f8b3a9e6a1e3160e20'
        timestamp = str(int(time.time() * 1000))
        sha = hmac.new(b'd1b964811afb40118a12068ff74a12f4', None, sha1)
        sha.update('password'.encode('utf8'))
        sha.update(client_id.encode('utf8'))
        sha.update('com.zhihu.web'.encode('utf8'))
        sha.update(timestamp.encode('utf8'))
        signature = sha.hexdigest()

        url = 'https://www.zhihu.com/api/v3/oauth/sign_in'
        headers = {
            'content-type': 'application/x-www-form-urlencoded',
            'Origin': 'https://www.zhihu.com',
            'Referer': 'https://www.zhihu.com/signin',
            'x-requested-with': 'fetch',
            'X-Zse-83': '3_2.0',
        }
        data = {
            'client_id': client_id,
            'grant_type': 'password',
            'timestamp': timestamp,
            'source': 'com.zhihu.web',
            'signature': signature,
            'username': '+86' + str(username),
            'password': password,
            'captcha': '',
            'lang': 'en',
            'utm_source': '',
            'ref_source': 'other_https://www.zhihu.com/signin'
        }
        string = urlencode(data)
        result = self.context.call('encrypt', string)
        response = self.session.post(url=url, headers=headers, data=result)
        print(response.text)


if __name__ == '__main__':
    ZhiHuSpider().login('***', '***')
