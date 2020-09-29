from os import path, getenv, system
from urllib.request import urlopen, Request
import platform
import json
import webbrowser
from time import sleep
import random
from datetime import datetime, time
import sys
from dotenv import load_dotenv
import requests

platform = platform.system()
PLT_WIN = "Windows"
PLT_LIN = "Linux"
PLT_MAC = "Darwin"
GET_SELENIUM = 0
GET_URLLIB = 1
GET_API = 2


# CONFIG SECTION BELOW --------------------------------------------------------

'''
Template for adding a new website to check:

The key is the url of the website you want to check

The Value is a tuple of size 4 with the following values:
    0. The substring that you're looking for in the html of the website, OR the API URL for the site.
    1. If this is True, it will alert when the substring is found in the html. If False, it will alert if the substring is NOT found in the HTML
    2. Set this to GET_SELENIUM, GET_URLLIB, or GET_API to choose which method is used to fetch data from the site. USE_SELENIUM is useful for jsx pages.
    3. A nickname for the alert to use. This is displayed in alerts.
'''

url_keywords = {
    "https://www.nvidia.com/en-us/geforce/graphics-cards/30-series/rtx-3080/": ("https://api-prod.nvidia.com/direct-sales-shop/DR/products/en_us/USD/5438481700", False, GET_API, 'Nvidia 3080', ),
    "https://www.nvidia.com/en-us/geforce/graphics-cards/30-series/rtx-3090/": ("https://api-prod.nvidia.com/direct-sales-shop/DR/products/en_us/USD/5438481600,5443202600", False, GET_API, 'Nvidia 3090', ),
    "https://www.evga.com/products/productlist.aspx?type=0&family=GeForce+30+Series+Family&chipset=RTX+3080": ("AddCart", True, GET_URLLIB, 'EVGA 3080'),
    # "https://www.evga.com/products/productlist.aspx?type=0&family=GeForce+16+Series+Family&chipset=GTX+1650+Super": ("AddCart", True, GET_URLLIB, 'EVGATest'),
    "https://www.newegg.com/p/pl?d=rtx+3080&N=100007709%20601357247": ("Add to cart", True, GET_URLLIB, 'Newegg 3080'),
    "https://www.bhphotovideo.com/c/search?q=3080&filters=fct_category%3Agraphic_cards_6567": ("Add to Cart", True, GET_URLLIB, 'BandH 3080'),
    "https://www.bestbuy.com/site/searchpage.jsp?st=3080": ("cart.svg", True, GET_SELENIUM, "BestBuy 3080"),
    # "https://www.bestbuy.com/site/searchpage.jsp?st=tv": ("cart.svg", True, GET_SELENIUM, "BestBuyTest")
    "https://www.amazon.com/stores/page/6B204EA4-AAAC-4776-82B1-D7C3BD9DDC82?ingress=0": (">Add to Cart<", True, GET_URLLIB, 'Amazon 3080')
    # "https://store.asus.com/us/item/202009AM160000001": (">Buy Now<", True, GET_URLLIB, 'ASUS')
}

# END OF CONFIG SECTION -------------------------------------------------------


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


def alert(url):
    product = url_keywords[url][3]
    print("{} IN STOCK".format(product))
    print(url)
    if OPEN_WEB_BROWSER:
        webbrowser.open(url, new=1)
    os_notification("{} IN STOCK".format(product), url)
    sms_notification(url)
    discord_notification(product, url)
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
        # Feel free to add something here :)
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
    if sys.argv[1] == 'test':
        alert("https://www.nvidia.com/en-us/geforce/graphics-cards/30-series/rtx-3080/")
        print("Test complete, if you received notification, you're good to go.")
        return True

def main():
    search_count = 0
    
    exit() if is_test() else False

    while True:
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("Starting search {} at {}".format(search_count, current_time))
        search_count += 1
        for url, info in url_keywords.items():
            print("\tChecking {}...".format(info[3]))

            try:
                if info[2] == GET_SELENIUM:
                    if not USE_SELENIUM:
                        continue
                    html = selenium_get(url)
                elif info[2] == GET_API:
                    if 'nvidia' in info[3].lower():
                        nvidia_get(url, info[0])
                    continue
                else:
                    html = urllib_get(url)
            except Exception as e:
                print("\t\tConnection failed...")
                print("\t\t{}".format(e))
                continue
            keyword = info[0]
            alert_on_found = info[1]
            index = html.upper().find(keyword.upper())
            if alert_on_found and index != -1:
                alert(url)
            elif not alert_on_found and index == -1:
                alert(url)

        base_sleep = 1
        total_sleep = base_sleep + random.uniform(MIN_DELAY, MAX_DELAY)
        sleep(total_sleep)


if __name__ == '__main__':
    main()
