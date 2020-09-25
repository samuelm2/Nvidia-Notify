from urllib.request import urlopen, Request
import json
import requests
from win10toast import ToastNotifier
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

import webbrowser
import time
import random
from datetime import datetime

'''
Template for adding a new website to check:

The key is the url of the website you want to check

The Value is a tuple of size 4 with the following values:
    0. The substring that you're looking for in the html of the website
    1. If this is True, it will alert when the substring is found in the html. If False, it will alert if the substring is NOT found in the HTML
    2. If this is True, it will use Selenium/FireFox to get the HTML from the website. This is useful when a website is a jsx page instead of static HTML (ex. BestBuy).
    3. A nickname for the alert to use.
'''
urlKeyWords = {
    "https://www.nvidia.com/en-us/geforce/graphics-cards/30-series/rtx-3080/" : ("Out Of Stock", False, True, 'Nvidia'),
    "https://www.evga.com/products/productlist.aspx?type=0&family=GeForce+30+Series+Family&chipset=RTX+3080" : ("AddCart", True, False, 'EVGA'),
    # "https://www.evga.com/products/productlist.aspx?type=0&family=GeForce+16+Series+Family&chipset=GTX+1650+Super" : ("AddCart", True, False, 'EVGATest'),
    "https://www.newegg.com/p/pl?d=rtx+3080&N=100007709%20601357247" : ("Add to cart", True, False, 'Newegg'),
    "https://www.bhphotovideo.com/c/search?q=3080&filters=fct_category%3Agraphic_cards_6567" : ("Add to Cart", True, False, 'BandH'),
    "https://www.bestbuy.com/site/searchpage.jsp?st=3080" : ("cart.svg", True, True, "BestBuy"),
    # "https://www.bestbuy.com/site/searchpage.jsp?st=tv" : ("cart.svg", True, True, "BestBuyTest")
    "https://www.amazon.com/stores/page/6B204EA4-AAAC-4776-82B1-D7C3BD9DDC82?ingress=0" : (">Add to Cart<", True, False, 'Amazon')
    # "https://store.asus.com/us/item/202009AM160000001" : (">Buy Now<", True, False, 'ASUS')
}

# Download the geckodriver from https://github.com/mozilla/geckodriver/releases, and then put the path to the executable in this rstring.
# I used version 0.27.0
firefoxWebdriverExecutablePath = r'INSERT EXECUTABLE PATH HERE'
discordWebhookUrl = "INSERT WEBHOOK URL HERE"

# If you want text notifications, you'll need to have a Twilio account set up (Free Trial is fine)
# Both of these numbers should be strings, in the format '+11234567890' (Not that it includes country code)


options = Options()
options.headless = True
toast = ToastNotifier()
driver = webdriver.Firefox(options=options, executable_path=firefoxWebdriverExecutablePath)
numReloads = 0


def alert(url):
    print("3080 IN STOCK")
    print(url)
    webbrowser.open(url, new=1)
    toast.show_toast("3080 IN STOCK", url, duration=5, icon_path="icon.ico")
    data = {}
    # for all params, see https://discordapp.com/developers/docs/resources/webhook#execute-webhook
    data["content"] = "3080 in stock at {0}".format(url)
    data["username"] = "In Stock Alert!"
    result = requests.post(discordWebhookUrl, data=json.dumps(data), headers={"Content-Type": "application/json"})

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))
    time.sleep(60)


def seleniumGet(url):
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


def urllibGet(url):
    # for regular sites
    # Fake a Firefox client
    request = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    page = urlopen(request, timeout=30)
    html_bytes = page.read()
    html = html_bytes.decode("utf-8")
    return html


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
                if info[2]:
                    html = seleniumGet(url)
                else:
                    html = urllibGet(url)
            except Exception as e:
                print("Connection failed...")
                print(e)
                continue
            keyWord = info[0]
            alertOnFound = info[1]
            index = html.find(keyWord)
            if alertOnFound and index != -1:
                alert(url)
            elif not alertOnFound and index == -1:
                alert(url)

        baseSleepAmt = 1
        totalSleep = baseSleepAmt + random.uniform(0, 10)
        # print("Sleeping for {} seconds".format(totalSleep))
        time.sleep(totalSleep)


if __name__ == '__main__':
    main()
