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
2. Open the python file in a text editor and fill in these 5 variables. They have descriptions for what they should be. Then save the file	
	-	firefoxWebdriverExecutablePath
	-	twilioToNumber
	-	twilioFromNumber
	-	twilioAuth
	-	twilioSid
3. pip install any dependencies you don't have
	-  `pip install twilio`
	- `pip install selenium`
	- `pip install win10toast`
## How to Run
`python notifier.py`

## Feel free to submit any PRs or issues!!  
