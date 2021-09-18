from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time, random

def browser(url, width=1920, height=1080, script='', fullpage=False):
    img = f'img-{random.randint(10000, 99999)}'
    d = DesiredCapabilities.CHROME
    d['loggingPrefs'] = { 'browser':'ALL' }
    # options
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    #options.add_argument('--no-sandbox')
    options.add_argument('--ignore-certificate-errors')
    if fullpage:
        #options.add_argument('--start-maximized')
        print()
    else:
        options.add_argument(f"window-size={width},{height}")
    options.add_argument("user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0")

    driver = webdriver.Chrome(
        executable_path="/home/vsevolod/Рабочий стол/dev/selenium-bot/scripts/chromedriver",
        options=options,
        desired_capabilities=d
    )

    try:
        driver.get(url)
        time.sleep(5)
        script = driver.execute_script(script)
        if fullpage:
            h = driver.execute_script('return document.body.parentNode.scrollHeight')
            driver.set_window_size(width, h)
        screenshot = driver.save_screenshot(f"/img/{img}.png")
        print(str(screenshot))
        time.sleep(1)
        logs = ''

        for entry in driver.get_log('browser'):
            logs += str(entry)

        if screenshot != False:
            return {"img": str(img), "logs": str(logs), "script": str(script)}
        else:
            img = 'error'
            return {"img": str(img), "logs": 'error', "script": 'error'}

    except Exception as ex:
        print(f'Error: {ex}')
        img = 'error'
        return {"img": str(img), "logs": 'error', "script": f'{ex}'}
    finally:
        driver.close()
        driver.quit()

#browser('https://google.com', 1920, 1080, 'console.log("test");', True)
