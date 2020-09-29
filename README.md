# ig-profie-scraper
[![made-with-python](https://img.shields.io/badge/Made%20With-Python-blue)](https://www.python.org/)
[![GitHub license](https://img.shields.io/github/license/404notfound-3/ig-profile-scraper)](#License)
[![GitHub stars](https://img.shields.io/github/stars/404notfound-3/ig-profile-scraper)](https://github.com/404notfound-3/ig-profile-scraper/stargazers)
[![CodeFactor](https://www.codefactor.io/repository/github/404notfound-3/ig-profile-scraper/badge/master)](https://www.codefactor.io/repository/github/404notfound-3/ig-profile-scraper/overview/master)
[![GitHub last commit](https://img.shields.io/github/last-commit/404notfound-3/ig-profile-scraper)](https://github.com/404notfound-3/ig-profile-scraper/commits/master)
[![GitHub issues](https://img.shields.io/github/issues/404notfound-3/ig-profile-scraper)](https://github.com/404notfound-3/ig-profile-scraper/issues)
![welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat)
![GitHub repo size](https://img.shields.io/github/repo-size/404notfound-3/ig-profile-scraper)

![ig-profile-scraper](readme_media/logo.png)

Fetch and save real time data anonymously from any Instagram profile without using official API.

# Table of Content

1. [Prerequisites](#Prerequisites)
2. [Installation](#Installation-and-Setup)
3. [Features](#Features)
4. [License](#License)

# Prerequisites

Before you continue, ensure you have met the following requirements.

1. You are using a Linux or Windows OS Machine.
2. You have installed latest version of [Python](https://www.python.org/), [Firefox](https://www.mozilla.org/en-US/firefox/) and [Geckodriver](https://github.com/mozilla/geckodriver/releases).
3. You have installed and running latest version of [Tor](https://torprojest.org) listening on SOCKSPort 9050.
4. You have installed xvfb (only for linux).

# Installation and Setup
You can get step by step detailed Installation steps [here](readme_media/INSTALLATION.md) for both windows and linux.

* Git clone or Download [this project](https://github.com/404notfound-3/ig-profile-scraper) and run below command in project directory.
    ```
    pip install -r requirements.txt
    ```

* Open up `config.py` in your favourite [text editor](https://github.com/404notfound-3/rpad) and
    * Replace timezone according to your country or state.
        ```
        TIMEZONE = timezone("Asia/Kolkata")
        ```
    * Add your temporary insta ids in ids dictonary.
        ```
        ids = {
            "<USERNAME_OR_EMAIL_HERE>" : "<PASSWORD_HERE>",
            "<USERNAME_OR_EMAIL_HERE>" : "<PASSWORD_HERE>"
        }
        ```
    * Add usernames of profiles which you want to scrape in the list of usernames.
        ```
        usernames = ["<USERNAME1>", "<USERNAME2>"]
        ```

    * Add your Slack webhook URL to get notified about errors and exceptions while running this scraper.
        ```
        slack = Slack(url = "<<ADD_YOUR_SLACK_WEBHOOK_URL_HERE>>")
        ```

<!-- * Edit torrc file and Restart Tor service (only for linux).
    ```
    sudo echo -e "SOCKSPort 9050\nControlPort 9051\n$(cat /etc/tor/torrc)" > /etc/tor/torrc
    sudo service tor restart
    ``` -->
Congratulations! you are ready to go, now run `windows.py` or `linux.py`.  Ping [me](https://facebook.com/404notfound.3) if ever face any error.


# Features
1. Profile Scraping
    * Full Name and Biography (Both encoded with utf-8)
    * Followers and Following
    * Number of public posts and owned media
    * Is user's account private, business, verified, has channel, joined recently
    * Profile page ID
    * Conneced FB page
    * Externel URL

2. Save data to an unique csv file in output folder.
3. Check for existing csv file and will create a new file if old one dosen't exist.
4. Random sleep time (to create a little randomness).
5. Autologin and auto logout (to switch ids after every 8 hours).
6. Automatic browser screenshots in `ss_log/browser` folder.
7. Slack webhook Integration to get error notifications
8. Tor connectivity and public ip check

# License
Project License can be found [here](https://github.com/404notfound-3/ig-profile-scraper/blob/master/LICENSE)

MIT © [Rahul Meena](https://facebook.com/404notfound.3)