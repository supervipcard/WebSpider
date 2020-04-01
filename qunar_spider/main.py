import requests
import execjs
import time
import re
from lxml import etree


def js_replace(string):
    group1 = re.search(r'.*;(.*);}\)\(window\);', string).group(1)[2: -1]
    group1 = 'var aa=' + group1 + ';'

    group2 = "var text=aa+'#'+'1563758680124#{{version}}#1m5e2vw#1dekk86#Mozilla50WindowsNT61Win64x64AppleWebKit53736KHTMLlikeGeckoChrome7003538110Safari53736##nw_140_p0_140_o#1563758685053#3#ucenter.login#https://user.qunar.com/passport/login.jsp#GMT+8#none#Win7';"

    group3 = re.search(r",(\w)=function\(aa,bb\){var re='';", string).group(1)
    group3 = 'return {}(text);}}'.format(group3)

    string = re.sub(r'^\(function\(\w\)', 'function target()', string)

    repl = ''.join((group1, group2, group3))
    result = re.sub(r'if\(!.*$', repl, string)
    return result


def login(username, password):
    session = requests.Session()
    session.headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
    }

    url = 'https://user.qunar.com/passport/login.jsp'
    response = session.get(url=url)
    html = etree.HTML(response.text)
    vcode_url = html.xpath('//img[@id="vcodeImg"]/@src')[0]

    response = session.get(url=vcode_url)
    with open(r'captcha.jpg', 'wb') as f:
        f.write(response.content)

    url = 'https://rmcsdf.qunar.com/js/df.js?org_id=ucenter.login&js_type=0'
    headers = {
        'Referer': 'https://user.qunar.com/passport/login.jsp'
    }
    response = session.get(url=url, headers=headers)
    session_id = re.search(r'sessionId=(.*?)&', response.text).group(1)

    url = 'https://user.qunar.com/passport/addICK.jsp?ssl'
    headers = {
        'Referer': 'https://user.qunar.com/passport/login.jsp'
    }
    session.get(url=url, headers=headers)

    url = 'https://rmcsdf.qunar.com/api/device/challenge.json'
    headers = {
        'Referer': 'https://user.qunar.com/passport/login.jsp',
    }
    params = {
        'callback': 'callback_{}'.format(str(int(time.time() * 1000))),
        'sessionId': session_id,
        'domain': 'qunar.com',
        'orgId': 'ucenter.login',
    }
    response = session.get(url=url, headers=headers, params=params)

    node = execjs.get('Node')
    string = js_replace(response.text)
    getpass = node.compile(string)
    answer = getpass.call('target')

    session.cookies.set('QN271', session_id)

    url = 'https://rmcsdf.qunar.com/api/device/answer.json'
    headers = {
        'Referer': 'https://user.qunar.com/passport/login.jsp',
    }
    params = {
        'callback': 'callback_{}'.format(str(int(time.time() * 1000))),
        'sessionId': session_id,
        'answer': answer
    }
    session.get(url=url, headers=headers, params=params)

    vcode = input('请输入验证码：')
    url = 'https://user.qunar.com/passport/loginx.jsp'
    headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Referer': 'https://user.qunar.com/passport/login.jsp',
    }
    data = {
        'loginType': '0',
        'username': username,
        'password': password,
        'remember': '1',
        'vcode': vcode,
    }
    response = session.post(url=url, headers=headers, data=data)
    print(response.text)


if __name__ == '__main__':
    login('***', '***')
