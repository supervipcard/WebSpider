import re
import json
import execjs
import requests
from PIL import Image, ImageChops
from io import BytesIO


class QZoneSpider:
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
        self.ua = 'TW96aWxsYS81LjAgKFdpbmRvd3MgTlQgNi4xOyBXaW42NDsgeDY0KSBBcHBsZVdlYktpdC81MzcuMzYgKEtIVE1MLCBsaWtlIEdlY2tvKSBDaHJvbWUvNzAuMC4zNTM4LjExMCBTYWZhcmkvNTM3LjM2'

    def run(self):
        cap_cd, salt, sess, sid = self.get_args()
        websig, arg = self.cap_union_new_show(sess, sid, cap_cd)
        vsig, y = self.cap_union_new_getsig(sess, sid, cap_cd)
        bg, fullbg = self.cap_union_new_getcapbysig(sess, cap_cd, vsig)
        x = self.get_pos(bg, fullbg)
        randstr, ticket = self.cap_union_new_verify(x, y, sess, sid, cap_cd, vsig, arg, websig)
        self.login(salt, randstr, ticket)

    def get_args(self):
        # 获取cap_cd和salt
        url = 'https://ssl.ptlogin2.qq.com/check'
        params = {
            'regmaster': '',
            'pt_tea': '2',
            'pt_vcode': '1',
            'uin': self.username,
            'appid': '549000912',
            'u1': 'https://qzs.qq.com/qzone/v5/loginsucc.html?para=izone',
        }
        response = self.session.get(url=url, params=params)
        result = eval(re.match(r'ptui_checkVC(.*?)$', response.text).group(1))
        cap_cd = result[1]
        salt = result[2]

        # 获取sess和sid
        url = 'https://ssl.captcha.qq.com/cap_union_prehandle'
        params = {
            'aid': '549000912',
            'captype': '',
            'curenv': 'inner',
            'protocol': 'https',
            'clientype': '2',
            'disturblevel': '',
            'apptype': '2',
            'ua': self.ua,
            'uid': self.username,
            'cap_cd': cap_cd,
        }
        response = self.session.get(url=url, params=params)
        result = json.loads(response.text[1: -1])
        sess = result['sess']
        sid = result['sid']
        return cap_cd, salt, sess, sid

    def cap_union_new_show(self, sess, sid, cap_cd):
        """验证码初始化"""
        url = 'https://ssl.captcha.qq.com/cap_union_new_show'
        params = {
            'aid': '549000912',
            'captype': '',
            'curenv': 'inner',
            'protocol': 'https',
            'clientype': '2',
            'disturblevel': '',
            'apptype': '2',
            'ua': self.ua,
            'sess': sess,
            'sid': sid,
            'uid': self.username,
            'cap_cd': cap_cd,
        }
        response = self.session.get(url=url, params=params)
        response.encoding = 'utf-8'
        websig = re.search(r'websig:"(.*?)",', response.text).group(1)
        arg = re.search(r'cdata:.*?,"(.*?)":', response.text).group(1)
        return websig, arg

    def cap_union_new_getsig(self, sess, sid, cap_cd):
        """刷新验证码"""
        url = 'https://ssl.captcha.qq.com/cap_union_new_getsig'
        params = {
            'aid': '549000912',
            'captype': '',
            'curenv': 'inner',
            'protocol': 'https',
            'clientype': '2',
            'disturblevel': '',
            'apptype': '2',
            'ua': self.ua,
            'sess': sess,
            'sid': sid,
            'uid': self.username,
            'cap_cd': cap_cd,
        }
        response = self.session.get(url=url, params=params)
        result = json.loads(response.text)
        return result['vsig'], result['inity']

    def cap_union_new_getcapbysig(self, sess, cap_cd, vsig):
        """获取验证码图片"""
        url = 'https://ssl.captcha.qq.com/cap_union_new_getcapbysig'
        params = {
            'aid': '549000912',
            'captype': '',
            'curenv': 'inner',
            'protocol': 'https',
            'clientype': '2',
            'disturblevel': '',
            'apptype': '2',
            'ua': self.ua,
            'sess': sess,
            'uid': self.username,
            'cap_cd': cap_cd,
            'vsig': vsig,
            'img_index': 1
        }
        response = self.session.get(url=url, params=params)
        byte_stream = BytesIO(response.content)
        bg = Image.open(byte_stream)
        bg.save('bg.jpg')

        params['img_index'] = 0
        response = self.session.get(url=url, params=params)
        byte_stream = BytesIO(response.content)
        fullbg = Image.open(byte_stream)
        fullbg.save('fullbg.jpg')
        return bg, fullbg

    def get_pos(self, bg, fullbg):
        """获取图片缺口坐标"""
        image = ImageChops.difference(bg, fullbg)

        x = 0
        for i in range(0, image.width):
            count = 0
            for j in range(0, image.height):
                pixel = image.getpixel((i, j))
                if pixel[0] < 10 and pixel[1] < 10 and pixel[2] < 10:
                    continue
                else:
                    count += 1
            if count >= 60:
                x = i-20
                break
        return x

    def cap_union_new_verify(self, x, y, sess, sid, cap_cd, vsig, arg, websig):
        """验证"""
        with open('tdc.js', 'r', encoding='utf-8') as f:
            source = f.read()
        phantom = execjs.get('PhantomJS')
        context = phantom.compile(source)
        value = context.call('get_value')

        url = 'https://ssl.captcha.qq.com/cap_union_new_verify'
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        }
        data = {
            'aid': '549000912',
            'captype': '',
            'curenv': 'inner',
            'protocol': 'https',
            'clientype': '2',
            'disturblevel': '',
            'apptype': '2',
            'ua': self.ua,
            'sess': sess,
            'sid': sid,
            'uid': self.username,
            'cap_cd': cap_cd,
            'vsig': vsig,
            'ans': '{x},{y};'.format(x=x, y=y),
            'cdata': '1',
            'subcapclass': '13',
            arg: value,
            'websig': websig,
            'vlg': '0_1_1',
        }
        response = self.session.post(url=url, headers=headers, data=data)
        response.encoding = 'utf-8'
        print(response.text)
        result = json.loads(response.text)
        return result['randstr'], result['ticket']

    def login(self, salt, randstr, ticket):
        with open('rsa.js', 'r', encoding='utf-8') as f:
            source = f.read()
        phantom = execjs.get('PhantomJS')
        context = phantom.compile(source)
        p = context.call('get_pass', self.password, salt, randstr)

        url = 'https://ssl.ptlogin2.qq.com/login'
        params = {
            'u': self.username,
            'verifycode': randstr,
            'pt_vcode_v1': '1',
            'pt_verifysession_v1': ticket,
            'p': p,
            'pt_randsalt': '2',
            'u1': 'https://qzs.qzone.qq.com/qzone/v5/loginsucc.html?para=izone',
            'ptredirect': '0',
            'h': '1',
            't': '1',
            'g': '1',
            'from_ui': '1',
            'ptlang': '2052',
            'js_type': '1',
            'login_sig': '',
            'pt_uistyle': '40',
            'aid': '549000912',
            'daid': '5',
            'has_onekey': '1',
        }
        response = self.session.get(url=url, params=params)
        print(response.text)


if __name__ == '__main__':
    QZoneSpider('123456', '123456').run()
