import asyncio
from pyppeteer import launch

script = '() =>{Object.defineProperties(navigator,{webdriver:{get:()=>undefined}})}'
executablePath = 'chrome.exe'
userDataDir = 'userDataDir'


def screen_size():
    """使用tkinter获取屏幕大小"""
    import tkinter
    tk = tkinter.Tk()
    width = tk.winfo_screenwidth()
    height = tk.winfo_screenheight()
    tk.quit()
    return {'width': width, 'height': height}


async def login(username, password):
    args = [
        '--start-maximized',  # 浏览器窗口最大化
        '--no-sandbox',  # 取消沙盒模式，沙盒模式权限小
        '--disable-infobars',  # 不显示信息栏，比如 Chrome 正受到自动化测试软件的控制
    ]
    browser = await launch(headless=False, autoClose=True, dumpio=True, args=args, executablePath=executablePath, userDataDir=userDataDir)

    page = await browser.newPage()  # 打开新标签页
    await page.setViewport(viewport=screen_size())
    await page.setExtraHTTPHeaders({'accept-language': 'zh-CN,zh;q=0.9'})
    await page.goto('https://login.taobao.com/member/login.jhtml')
    await page.evaluate(script)    # 将window.navigator.webdriver的值由True改为undefined

    await page.click('.ph-label')
    await page.type('#TPL_username_1', username, {'delay': 100})
    await page.type('#TPL_password_1', password, {'delay': 100})
    await page.waitFor(1000)

    try:
        await page.hover('#nc_1_n1z')
        await page.mouse.down()
        await page.mouse.move(2000, 0)
        await page.mouse.up()
    except:
        print('没有出现验证码')

    await page.waitFor(1000)
    await page.click('#J_SubmitStatic')
    await page.waitFor(5000)

    cookies = await page.cookies()
    content = await page.content()

    return cookies, content


def main():
    loop = asyncio.get_event_loop()
    cookies, content = loop.run_until_complete(login('***', '***'))
    print(cookies)


if __name__ == '__main__':
    main()
