from urllib.request import urlopen, Request
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

import json
import requests
import webbrowser
import time
import random
from datetime import datetime

from twilio.rest import Client

GET_SELENIUM = 0
GET_URLLIB = 1
GET_API = 2


### CONFIG SECTION BELOW ------------------------------------------------------

'''
Template for adding a new website to check:

The key is the url of the website you want to check

The Value is a tuple of size 4 with the following values:
    0. The substring that you're looking for in the html of the website, OR the API URL for the site.
    1. If this is True, it will alert when the substring is found in the html. If False, it will alert if the substring is NOT found in the HTML
    2. Set this to GET_SELENIUM, GET_URLLIB, or GET_API to choose which method is used to fetch data from the site. USE_SELENIUM is useful for jsx pages.
    3. A nickname for the alert to use. This is displayed in alerts.
'''

USE_TWILIO = True
USE_DISCORD = True
NOTIFY_MAC = False

urlKeyWords = {
    "https://www.nvidia.com/en-us/geforce/graphics-cards/30-series/rtx-3080/" : ("https://api-prod.nvidia.com/direct-sales-shop/DR/products/en_us/USD/5438481700", False, GET_API, 'Nvidia 3080', ),
    "https://www.nvidia.com/en-us/geforce/graphics-cards/30-series/rtx-3090/" : ("https://api-prod.nvidia.com/direct-sales-shop/DR/products/en_us/USD/5438481600,5443202600", False, GET_API, 'Nvidia 3090', ),
    "https://www.evga.com/products/productlist.aspx?type=0&family=GeForce+30+Series+Family&chipset=RTX+3080" : ("AddCart", True, GET_URLLIB, 'EVGA 3080'),
    # "https://www.evga.com/products/productlist.aspx?type=0&family=GeForce+16+Series+Family&chipset=GTX+1650+Super" : ("AddCart", True, False, 'EVGATest'),
    "https://www.newegg.com/p/pl?d=rtx+3080&N=100007709%20601357247" : ("Add to cart", True, GET_URLLIB, 'Newegg 3080'),
    "https://www.bhphotovideo.com/c/search?q=3080&filters=fct_category%3Agraphic_cards_6567" : ("Add to Cart", True, GET_URLLIB, 'BandH 3080'),
    "https://www.bestbuy.com/site/searchpage.jsp?st=3080" : ("cart.svg", True, GET_SELENIUM, "BestBuy"),
    # "https://www.bestbuy.com/site/searchpage.jsp?st=tv" : ("cart.svg", True, GET_SELENIUM, "BestBuyTest")
    "https://www.amazon.com/stores/page/6B204EA4-AAAC-4776-82B1-D7C3BD9DDC82?ingress=0" : (">Add to Cart<", True, GET_URLLIB, 'Amazon 3080')
    # "https://store.asus.com/us/item/202009AM160000001" : (">Buy Now<", True, False, 'ASUS')
}

# Download the geckodriver from https://github.com/mozilla/geckodriver/releases, and then put the path to the executable in this rstring.
# I used version 0.27.0
firefoxWebdriverExecutablePath = r'INSERT EXECUTABLE PATH HERE'

# If you want to send alerts to discord via webhooks, place the webhook URL here
if USE_DISCORD:
    discordWebhookUrl = "INSERT DISCORD WEBHOOK URL HERE"

# If you want text notifications, you'll need to have a Twilio account set up (Free Trial is fine)
# Both of these numbers should be strings, in the format '+11234567890' (Not that it includes country code)
if USE_TWILIO:
    twilioToNumber = '+12223334444'
    twilioFromNumber = '+15556667777'
    twilioSid =  '## INSERT TWILIO SID HERE ##'
    twilioAuth = '## INSERT TWILIO AUTH HERE ##'
    client = Client(twilioSid, twilioAuth)

if NOTIFY_MAC:
    import os
else:
    from win10toast import ToastNotifier
    toast = ToastNotifier()

### END OF CONFIG SECTION -----------------------------------------------------

options = Options()
options.headless = True
driver = webdriver.Firefox(options=options, executable_path=firefoxWebdriverExecutablePath)
numReloads = 0

def alert(url):
    product = urlKeyWords[url][3]
    print("{} IN STOCK".format(product))
    print(url)
    webbrowser.open(url, new=1)
    if NOTIFY_MAC:
        mac_alert("{} IN STOCK".format(product), url)
    else:
        toast.show_toast("{} IN STOCK".format(product), url, duration=5, icon_path="icon.ico")
    if USE_TWILIO:
        message = client.messages.create(to=twilioToNumber, from_=twilioFromNumber, body=url)
    if USE_DISCORD:
        data = {}
        # for all params, see https://discordapp.com/developers/docs/resources/webhook#execute-webhook
        data["content"] = "{} in stock at {}".format(product, url)
        data["username"] = "In Stock Alert!"
        result = requests.post(discordWebhookUrl, data=json.dumps(data), headers={"Content-Type": "application/json"})

        try:
            result.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
        else:
            print("Payload delivered successfully, code {}.".format(result.status_code))
    time.sleep(60)

def mac_alert(title, text):
    os.system("""
              osascript -e 'display notification "{}" with title "{}"'
              """.format(text, title))
    os.system('afplay /System/Library/Sounds/Glass.aiff')
    os.system('say "{}"'.format(title))
    return

def selenium_get(url):
    # for jsp sites
    # test url : https://www.bestbuy.com/site/searchpage.jsp?st=3080
    global driver
    global numReloads

    driver.get(url)
    http = driver.page_source

    numReloads += 1
    if numReloads == 10:
        numReloads = 0
        driver.close()
        driver.quit()
        driver = webdriver.Firefox(options=options, executable_path=firefoxWebdriverExecutablePath)
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
    response = requests.get(api_url)
    item = response.json()

    print(item['products']['product'][0]['inventoryStatus']['status'])
    if item['products']['product'][0]['inventoryStatus']['status'] != "PRODUCT_INVENTORY_OUT_OF_STOCK":
        alert(url)

def main():
    numSearches = 0
    while True:
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("Starting search {} at {}".format(numSearches, current_time))
        numSearches += 1
        for url, info in urlKeyWords.items():
            print("\tChecking {}...".format(info[3]))

            try:
                if info[2] == GET_SELENIUM:
                    html = selenium_get(url)
                if info[2] == GET_API:
                    if 'nvidia' in info[3].lower():
                        nvidia_get(url, info[0])
                    continue
                else:
                    html = urllib_get(url)
            except Exception as e:
                print("Connection failed...")
                print(e)
                continue
            keyWord = info[0]
            alertOnFound = info[1]
            index = html.upper().find(keyWord.upper())
            if alertOnFound and index != -1:
                alert(url)
            elif not alertOnFound and index == -1:
                alert(url)

        baseSleepAmt = 1
        totalSleep = baseSleepAmt + random.uniform(1, 11)
        # print("Sleeping for {} seconds".format(totalSleep))
        time.sleep(totalSleep)


if __name__ == '__main__':
    main()
