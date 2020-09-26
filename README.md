# Nvidia-Notify
Simple, quick to set up stock notification bot for Nvidia 3080 that I used to get my 3080. Less than 150 lines of code.

## Requirements
- Firefox (https://www.mozilla.org/en-US/firefox/download/thanks/)
- Some version of python3 installed on your computer (https://www.python.org/downloads/)
- pip to install the dependencies (https://pip.pypa.io/en/stable/installing/)
- A Twilio account (can be a trial account) (https://www.twilio.com/try-twilio)
- geckodriver (a Firefox webdriver, I used version 0.27.0) (https://github.com/mozilla/geckodriver/releases)

## How to set up
1. Clone/Download the notifier.py file and the icon.ico file and put them in the same folder
2. Open the .env file in a text editor and fill in the variables, without adding spaces or quotes.
	-	firefoxWebdriverExecutablePath -> full path to your downloaded gecko driver (shift right click and copy as path on windows)
	-	twilioToNumber -> phone number to send notification to
	-	twilioFromNumber -> twilio number generated that will send notifications
	-	twilioAuth -> twilio auth code for your account
	-	twilioSid -> twilio sid for your account
3. pip install dependencies
	-  `pip install -r requirements.txt` or `python -m pip install -r requirements.txt`
  - If not running on Windows 10, remove the win10toast from requirements, or ignore it if it fails to install
  
## How to Run

```
python notifier.py
```

### MacOS Troubleshooting

Make sure you have `NOTIFY_MAC` in the config section set to true

##### MacOS Python3 Info

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
pip3 install twilio
pip3 install -r requirements.txt
```

Do this for all the pip dependencies

##### MacOS Gecko Driver Security

The first time you run this script on a mac, the system will prevent you from using the gecko driver.  To allow this, open System Preferences > Security and Privacy and under the general tab, click the button to allow geckodriver to be run.  You will need to run the script at least once before you can do this.  The first time you run the script after allowing geckodriver the script will crash again, but it will not crash after that. 

## Feel free to submit any PRs or issues!!  
