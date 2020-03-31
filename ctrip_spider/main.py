import requests
import json
import base64
import execjs
import hashlib
from PIL import Image
import matplotlib.pyplot as plt
from io import BytesIO


class CTripSpider:
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

        with open('aes.js', 'r', encoding='utf-8') as f:
            source = f.read()
        external_runtime = execjs.get()
        self.context = external_runtime.compile(source)

        self.points = []

    def run(self):
        rid, V, ba = self.risk_inspect()
        token, big_image, small_image, ba = self.verify_slider(rid, V)
        value = self.click(big_image, small_image)
        token = self.verify_text(value, rid, V, ba, token)
        self.login(token)

    @staticmethod
    def encrypt(string):
        md = hashlib.md5()
        md.update(string.encode('utf-8'))
        result = md.hexdigest()
        return result

    def on_press(self, event):
        self.points.append((event.button, int(event.xdata), int(event.ydata)))

    def click(self, big_image, small_image):
        fig = plt.figure(1)
        plt.imshow(big_image)
        fig.canvas.mpl_connect('button_press_event', self.on_press)

        plt.figure(2)
        plt.imshow(small_image)
        plt.show()

        value = list()
        for i in self.points:
            value.append(i[1])
            value.append(i[2])
        return value

    def risk_inspect(self):
        O = {
            'ua': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
            'fp': None,
            'vid': None,
            'sfp': None,
            'svid': None,
            'guid': None,
            'h5_duid': None,
            'pc_duid': None,
            'hb_uid': None,
            'pc_uid': None,
            'h5_uid': None,
            'infosec_openid': None,
            'device_id': None,
            'client_id': None,
            'pid': None,
            'sid': None,
            'login_uid': None
        }
        db = {
            'resolution_width': 1366,
            'resolution_height': 768,
            'language': 'zh-CN'
        }
        V = self.context.call('aes', json.dumps(O, separators=(',', ':')))
        ba = self.context.call('aes', json.dumps(db, separators=(',', ':')))

        string = "appid=100008493&business_site=crm_login_online&version=2.5.16&dimensions={dimensions}&extend_param={extend_param}".format(
            dimensions=V, extend_param=ba)
        sign = self.encrypt(string)

        url = 'https://ic.ctrip.com/captcha/risk_inspect'
        params = {
            'extend_param': ba,
            'appid': '100008493',
            'business_site': 'crm_login_online',
            'version': '2.5.16',
            'dimensions': V,
            'sign': sign,
        }
        response = self.session.get(url=url, params=params)
        res = json.loads(response.text[5: -1])
        rid = res['result']['rid']
        return rid, V, ba

    def verify_slider(self, rid, V):
        ca = {
            'slidingTime': 580,
            'display': '1366x768',
            'keykoardTrack': [],
            'slidingTrack': [{'x': 570, 'y': 350}, {'x': 650, 'y': 350}, {'x': 700, 'y': 350}, {'x': 780, 'y': 350},
                             {'x': 860, 'y': 350}],
            'timezone': -480,
            'flashState': False,
            'language': 'zh-CN',
            'platform': 'Win32',
            'cpuClass': None,
            'hasSessStorage': True,
            'hasLocalStorage': True,
            'hasIndexedDB': True,
            'hasDataBase': True,
            'doNotTrack': False,
            'touchSupport': False,
            'mediaStreamTrack': True,
        }
        db = {
            'select_width': 280,
            'select_height': 200,
            'resolution_width': 1366,
            'resolution_height': 768,
            'language': 'zh-CN',
            'select_language': '',
        }
        e = self.context.call('aes', json.dumps(ca, separators=(',', ':')))
        ba = self.context.call('aes', json.dumps(db, separators=(',', ':')))

        string = "appid=100008493&business_site=crm_login_online&version=2.5.16&verify_msg={verify_msg}&dimensions={dimensions}&extend_param={extend_param}".format(
            verify_msg=e, dimensions=V, extend_param=ba)
        sign = self.encrypt(string)

        url = 'https://ic.ctrip.com/captcha/verify_slider'
        params = {
            'appid': '100008493',
            'business_site': 'crm_login_online',
            'rid': rid,
            'version': '2.5.16',
            'verify_msg': e,
            'dimensions': V,
            'extend_param': ba,
            'sign': sign,
        }
        response = self.session.get(url=url, params=params)
        res = json.loads(response.text[5: -1])
        token = res['result']['token']
        byte_stream = BytesIO(base64.b64decode(res['result']['risk_info']['process_value']['big_image']))
        big_image = Image.open(byte_stream)
        byte_stream = BytesIO(base64.b64decode(res['result']['risk_info']['process_value']['small_image']))
        small_image = Image.open(byte_stream)
        return token, big_image, small_image, ba

    def verify_text(self, value, rid, V, ba, token):
        ca = {
            'cpuClass': None,
            'display': '1366x768',
            'doNotTrack': False,
            'flashState': False,
            'hasDataBase': True,
            'hasIndexedDB': True,
            'hasLocalStorage': True,
            'hasSessStorage': True,
            'inputTime': 58000,
            'keykoardTrack': [],
            'language': 'zh-CN',
            'mediaStreamTrack': True,
            'platform': 'Win32',
            'timezone': -480,
            'touchSupport': False,
            'value': value
        }
        i = self.context.call('aes', json.dumps(ca, separators=(',', ':')))

        string = "appid=100008493&business_site=crm_login_online&version=2.5.16&verify_msg={verify_msg}&dimensions={dimensions}&extend_param={extend_param}&token={token}&captcha_type=SELECT".format(
            verify_msg=i, dimensions=V, extend_param=ba, token=token)
        sign = self.encrypt(string)

        url = 'https://ic.ctrip.com/captcha/verify_text'
        params = {
            'appid': '100008493',
            'token': token,
            'rid': rid,
            'business_site': 'crm_login_online',
            'version': '2.5.16',
            'captcha_type': 'SELECT',
            'verify_msg': i,
            'dimensions': V,
            'extend_param': ba,
            'sign': sign,
        }
        response = self.session.get(url=url, params=params)
        token = json.loads(response.text[5: -1])['result']['token']
        return token

    def login(self, token):
        url = 'https://passport.ctrip.com/gateway/api/soa2/12559/userValidate'
        headers = {
            'referer': 'https://passport.ctrip.com/user/login',
            'content-type': 'application/json; charset=UTF-8',
            'x-requested-with': 'XMLHttpRequest',
        }
        data = '{{"AccountHead":{{"Token":"{token}","SliderVersion":"2.5.16","Platform":"P","Extension":{{}}}},"Data":{{"accessCode":"7434E3DDCFF0EDA8","strategyCode":"63A70EA9BB38F5D","userName":"{username}","certificateCode":"{password}","extendedProperties":[{{"key":"LoginName","value":"{username}"}},{{"key":"Platform","value":"P"}},{{"key":"PageId","value":""}},{{"key":"rmsToken","value":""}},{{"key":"URL","value":"https://passport.ctrip.com/user/login"}},{{"key":"http_referer","value":""}}]}}}}'.format(
            token=token, username=self.username, password=self.password)
        response = self.session.post(url=url, headers=headers, data=data)
        print(response.text)


if __name__ == '__main__':
    CTripSpider('***', '***').run()
