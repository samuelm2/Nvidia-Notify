**CHECK PINNED ISSUES - NVIDIA API Is frequently down, this is a known issue and is on NVIDIA's end. If you get timeout issues, best course of action is to wait it out. Check [HERE](https://github.com/samuelm2/Nvidia-Notify/issues/18) for more info.**

# Nvidia-Notify
Simple, quick to set up stock notification bot for Nvidia 3080 that I used to get my 3080. Less than 250 lines of code.

[Check the Wiki!](https://github.com/samuelm2/Nvidia-Notify/wiki) - We'll post frequently asked questions, tips, and other useful info there.

## Requirements
- [Firefox](https://www.mozilla.org/en-US/firefox/download/thanks/)
- [Python 3](https://www.python.org/downloads/) (not python 2.x!)
- [pip](https://pip.pypa.io/en/stable/installing/) (to handle installing dependencies)
- [geckodriver](https://github.com/mozilla/geckodriver/releases) (a Firefox webdriver, I used version 0.27.0)

## Optional Components
- SMS Support: [A Twilio account](https://www.twilio.com/try-twilio) (can be a trial account)
- Discord Notifications via Webhooks: [Discord Webhook guide here](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks)

## How to set up
1. Clone/Download the notifier.py file and the icon.ico file and put them in the same folder
2. Download geckodriver
3. Open the .env file in a text editor and fill in the variables.
    -   Windows users can place `geckodriver.exe` in the same folder as the script. Otherwise, update `WEBDRIVER_PATH`
	-	refer to the .env file for instructions on specific values.
	-   Many features are optional, you can leave them blank if you don't want to use them.
4. pip install dependencies
	-  `pip install -r requirements.txt` or `python -m pip install -r requirements.txt`
    - If running windows, use `win-requirements.txt` instead.
    - On some Linux/Mac systems, you may need to use `python3` and `pip3` instead of `python` and `pip`, respectively.
5. You can open `notifier.py` in a text editor and modify the list of pages that get scanned.

## How to Run

```
python notifier.py
```

Note that on some linux and mac systems, you may have to use the following instead:
```
python3 notifier.py
```

## Testing if Notifications Work (Twilio/Discord)

```
python notifier.py test
```
*replace 'python' with 'python3' if that is how your system is configured*

## MacOS Python3 Info

MacOS typically has Python 2 installed on the path as `python` by default. If you do not have Python 3 on your system,
the easiest way to install is to get it from HomeBrew (https://brew.sh/)

Once you have brew installed, you can install Python 3 by running this:

```
brew install python3
```

When installed in this way, you will normally need to run it as `python3` instead of `python`

```
python3 notifier.py
```

You will also need to install your pip dependencies with pip3 instead of pip like so:

```
pip3 install -r requirements.txt
```


##### MacOS Gecko Driver Security

The first time you run this script on a mac, the system will prevent you from using the gecko driver.  To allow this, open System Preferences > Security and Privacy and under the general tab, click the button to allow geckodriver to be run.  You will need to run the script at least once before you can do this.  The first time you run the script after allowing geckodriver the script will crash again, but it will not crash after that.


## Configuring the websites to check

If you are in the mood you can change or add your own websites to check stock for.

They are defined in a JSON file, named `sites.json`. It includes several of the most popular sites and searches.

The `site.json` file can be found [here](https://github.com/samuelm2/Nvidia-Notify/blob/master/sites.json).

| Field  | Value | Description  |
|---|---|---|
| url     | valid url | The url of the site, including the query string params specific to the site for narrowing results, specifying a product number, specific filtering options, etc...
| api     | valid url | The api url to use, this is specific to Nvidia.  The method `GET_API` is required
| keyword | text | The keyword that you're looking for in the html of the website
| alert   | true or false | If true, it will alert when the keyword is found in the html. If false, it will alert if the keyword is NOT found in the html
| method  | GET_SELENIUM, GET_URLLIB, or GET_API | Which method is used to fetch data from the site.
| name    | text | A nickname for the alert to use.
| enabled | true or false | Whether the site will be checked. Useful for example, when testing your addition, and disabling the rest so you can quickly see the results.

An example:

```json
  {
    "url": "https://www.newegg.com/p/pl?d=rtx+3080&N=100007709%20601357247",
    "keyword": "Add to cart",
    "alert": true,
    "method": "GET_URLLIB",
    "name": "Newegg 3080",
    "enabled": true
  }
```

## Feel free to submit any PRs or issues!!
