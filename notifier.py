import json
import platform
import random
import webbrowser
from datetime import datetime, time
from os import path, getenv, system
from time import sleep
from urllib.request import urlopen, Request
from enum import Enum
import sys
import requests
from dotenv import load_dotenv

platform = platform.system()
PLT_WIN = "Windows"
PLT_LIN = "Linux"
PLT_MAC = "Darwin"

class Methods(str, Enum):
    GET_SELENIUM = "GET_SELENIUM"
    GET_URLLIB = "GET_URLLIB"
    GET_API = "GET_API"

# Set up environment variables and constants. Do not modify this unless you know what you are doing!
load_dotenv()
USE_TWILIO = False
USE_SELENIUM = False
USE_DISCORD_HOOK = False
WEBDRIVER_PATH = path.normpath(getenv('WEBDRIVER_PATH'))
DISCORD_WEBHOOK_URL = getenv('DISCORD_WEBHOOK_URL')
TWILIO_TO_NUM = getenv('TWILIO_TO_NUM')
TWILIO_FROM_NUM = getenv('TWILIO_FROM_NUM')
TWILIO_SID = getenv('TWILIO_SID')
TWILIO_AUTH = getenv('TWILIO_AUTH')
ALERT_DELAY = int(getenv('ALERT_DELAY'))
MIN_DELAY = int(getenv('MIN_DELAY'))
MAX_DELAY = int(getenv('MAX_DELAY'))
OPEN_WEB_BROWSER = getenv('OPEN_WEB_BROWSER') == 'true'

with open('sites.json', 'r') as f:
    sites = json.load(f)

# Selenium Setup
if WEBDRIVER_PATH:
    USE_SELENIUM = True
    print("Enabling Selenium... ", end='')
    from selenium import webdriver
    from selenium.webdriver.firefox.options import Options

    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options, executable_path=WEBDRIVER_PATH)
    reload_count = 0
    print("Done!")

# Twilio Setup
if TWILIO_TO_NUM and TWILIO_FROM_NUM and TWILIO_SID and TWILIO_AUTH:
    USE_TWILIO = True
    print("Enabling Twilio... ", end='')
    from twilio.rest import Client

    client = Client(TWILIO_SID, TWILIO_AUTH)
    print("Done!")

# Discord Setup
if DISCORD_WEBHOOK_URL:
    USE_DISCORD_HOOK = True
    print('Enabled Discord Web Hook.')

# Platform specific settings
print("Running on {}".format(platform))
if platform == PLT_WIN:
    from win10toast import ToastNotifier

    toast = ToastNotifier()


def alert(site):
    product = site.get('name')
    print("{} IN STOCK".format(product))
    print(site.get('url'))
    if OPEN_WEB_BROWSER:
        webbrowser.open(site.get('url'), new=1)
    os_notification("{} IN STOCK".format(product), site.get('url'))
    sms_notification(site.get('url'))
    discord_notification(product, site.get('url'))
    sleep(ALERT_DELAY)


def os_notification(title, text):
    if platform == PLT_MAC:
        system("""
                  osascript -e 'display notification "{}" with title "{}"'
                  """.format(text, title))
        system('afplay /System/Library/Sounds/Glass.aiff')
        system('say "{}"'.format(title))
    elif platform == PLT_WIN:
        toast.show_toast(title, text, duration=5, icon_path="icon.ico")
    elif platform == PLT_LIN:
        try:
            icon_path = path.realpath('icon.ico')
            system('notify-send "{}" "{}" -i {}'.format(title, text, icon_path))
        except:
            # No system support for notify-send
            pass


def sms_notification(url):
    if USE_TWILIO:
        client.messages.create(to=TWILIO_TO_NUM, from_=TWILIO_FROM_NUM, body=url)


def discord_notification(product, url):
    if USE_DISCORD_HOOK:
        data = {
            "content": "{} in stock at {}".format(product, url),
            "username": "In Stock Alert!"
        }
        result = requests.post(DISCORD_WEBHOOK_URL, data=json.dumps(data), headers={"Content-Type": "application/json"})
        try:
            result.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
        else:
            print("Payload delivered successfully, code {}.".format(result.status_code))


def selenium_get(url):
    global driver
    global reload_count

    driver.get(url)
    http = driver.page_source

    reload_count += 1
    if reload_count == 10:
        reload_count = 0
        driver.close()
        driver.quit()
        driver = webdriver.Firefox(options=options, executable_path=WEBDRIVER_PATH)
    return http


def urllib_get(url):
    # for regular sites
    # Fake a Firefox client
    request = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    page = urlopen(request, timeout=30)
    html_bytes = page.read()
    html = html_bytes.decode("utf-8")
    return html


def nvidia_get(url, api_url):
    response = requests.get(api_url, timeout=5)
    item = response.json()
    if item['products']['product'][0]['inventoryStatus']['status'] != "PRODUCT_INVENTORY_OUT_OF_STOCK":
        alert(url)


def is_test():
    try:
        if sys.argv[1] == 'test':
            alert(sites[0])
            print("Test complete, if you received notification, you're good to go.")
            return True
    except:
        return False


def main():
    search_count = 0

    exit() if is_test() else False

    while True:
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("Starting search {} at {}".format(search_count, current_time))
        search_count += 1
        for site in sites:
            if site.get('enabled'):
                print("\tChecking {}...".format(site.get('name')))

                try:
                    if site.get('method') == Methods.GET_SELENIUM:
                        if not USE_SELENIUM:
                            continue
                        html = selenium_get(site.get('url'))
                    elif site.get('method') == Methods.GET_API:
                        if 'nvidia' in site.get('name').lower():
                            nvidia_get(site.get('url'), site.get('api'))
                        continue
                    else:
                        html = urllib_get(site.get('url'))
                except Exception as e:
                    print("\t\tConnection failed...")
                    print("\t\t{}".format(e))
                    continue
                keyword = site.get('keyword')
                alert_on_found = site.get('alert')
                index = html.upper().find(keyword.upper())
                if alert_on_found and index != -1:
                    alert(site)
                elif not alert_on_found and index == -1:
                    alert(site)

                base_sleep = 1
                total_sleep = base_sleep + random.uniform(MIN_DELAY, MAX_DELAY)
                sleep(total_sleep)


if __name__ == '__main__':
    main()
