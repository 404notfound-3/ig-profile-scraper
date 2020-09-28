import csv
import time
import json
import random
import pickle
from stem import Signal
from requests import get
from pytz import timezone
from datetime import datetime
from selenium import webdriver
from slack_webhook import Slack
from traceback import format_exc
from os import popen, path, system
from bs4 import BeautifulSoup as bs
from stem.control import Controller
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile


URL = "https://instagram.com/{}/" ## Instagram URL
SOCKSPort = 9050 ## Tor SOCKS listner port
ControlPort = 9051 ## Tor control listner port
OUTPUT_FOLDER = "./output/" ## Output Folder path
TimeZone = "Asia/Kolkata"

## dict of temporary instagram ids
ids = {
    "temp/fake_id1" : "password",
    "temp/fake_id2" : "password"
}
## list of instagram usernames to scrape/monitor.
usernames = ["<<ADD_INSTAGRAM_USERNAMES_IN_THIS_LIST>>"]

## Waking up Tor executables, Paste full PATH here of tor.exe in your system or skip this if you are using linux.
system(r"C:\Program Files (x86)\Tor Browser\Browser\TorBrowser\Tor\tor.exe -f .\etc\torrc")

## Slack webhook, This will help you to get notified about errors and exceptions.
slack = Slack(url = "<<ADD_YOUR_SLACK_WEBHOOK_URL_HERE>>")

## Proxies for request over Tor
proxies = {
    "http" : f"socks5h://localhost:{SOCKSPort}",
    "https": f"socks5h://localhost:{ControlPort}"
}

## to verify Tor connectivity
def check_tor_conn():
    title = str(bs(get("https://check.torproject.org", proxies = proxies).text, "html.parser").title).split("\n")[2]
    if "Congratulations." in title:
        print("\nTor Connectivity Verified")
        slack.post(text = "\nTor Connectivity Verified")
    elif "not using Tor" in title:
        print("\nTor is not Connected, Try 'sudo service tor restart'. Aborting...")
        slack.post(text = "\nTor is not Connected, Try 'sudo service tor restart'. Aborting...")
        exit()
check_tor_conn()

## Creating a firefox profile and adding some privacy and security prefrences.
profile = FirefoxProfile()
profile.set_preference("places.history.enabled", False)
profile.set_preference("privacy.clearOnShutdown.offlineApps", True)
profile.set_preference("privacy.clearOnShutdown.passwords", True)
profile.set_preference("privacy.clearOnShutdown.siteSettings", True)
profile.set_preference("privacy.sanitize.sanitizeOnShutdown", True)
profile.set_preference("signon.rememberSignons", False)
profile.set_preference("network.cookie.lifetimePolicy", 2)
profile.set_preference("network.dns.disablePrefetch", True)
profile.set_preference("network.http.sendRefererHeader", 0)
profile.set_preference("network.proxy.type", 1)
profile.set_preference("network.proxy.socks_version", 5)
profile.set_preference("network.proxy.socks", '127.0.0.1')
profile.set_preference("network.proxy.socks_port", SOCKSPort) ## Replace local PORT value if your Tor service is running on another port.
profile.set_preference("network.proxy.socks_remote_dns", True)
profile.set_preference("permissions.default.image", 2) ## I Disabled image loading, because it will speed up our scraping.

## Starting firefox browser using profile we created above.
browser = webdriver.Firefox(firefox_profile = profile)
browser.delete_all_cookies() ## just in case if your browser...


## this function will take a soup as input and will return some valuable data.
def parse_data(page_source_soup):
    data = {}
    body = page_source_soup.find("body")
    script = body.find("script", text=lambda t: t.startswith("window._sharedData"))
    script_json = script.string.split(" = ", 1)[1].rstrip(";")
    script_json = json.loads(script_json)
    data["full_name"] = str(script_json["entry_data"]["ProfilePage"][0]["graphql"]["user"]["full_name"].encode())
    data["biography"] = str(script_json["entry_data"]["ProfilePage"][0]["graphql"]["user"]["biography"].encode())
    data["followers"] = str(script_json["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_followed_by"]["count"])
    data["following"] = str(script_json["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_follow"]["count"])

    ## change timezone according to your country or state.
    now = datetime.now(timezone(TimeZone))
    data["date"], data["time"], data["weekday"] = now.strftime("%d/%m/%Y"), now.strftime("%H:%M:%S"), now.strftime("%A")
    data["is_private"] = str(script_json["entry_data"]["ProfilePage"][0]["graphql"]["user"]["is_private"])
    data["is_business_account"] = str(script_json["entry_data"]["ProfilePage"][0]["graphql"]["user"]["is_business_account"])
    data["is_verified"] = str(script_json["entry_data"]["ProfilePage"][0]["graphql"]["user"]["is_verified"])
    data["logging_page_id"] = script_json["entry_data"]["ProfilePage"][0]["logging_page_id"]
    data["id"] = script_json["entry_data"]["ProfilePage"][0]["graphql"]["user"]["id"]
    data["has_channel"] = str(script_json["entry_data"]["ProfilePage"][0]["graphql"]["user"]["has_channel"])
    data["has_blocked_viewer"] = str(script_json["entry_data"]["ProfilePage"][0]["graphql"]["user"]["has_blocked_viewer"])
    data["joined_recently"] = str(script_json["entry_data"]["ProfilePage"][0]["graphql"]["user"]["is_joined_recently"])
    data["external_url"] = str(script_json["entry_data"]["ProfilePage"][0]["graphql"]["user"]["external_url"])
    data["external_url_linkshimmed"] = str(script_json["entry_data"]["ProfilePage"][0]["graphql"]["user"]["external_url_linkshimmed"])
    data["connected_fb_page"] = str(script_json["entry_data"]["ProfilePage"][0]["graphql"]["user"]["connected_fb_page"])
    data["edge_felix_video_timeline"] = str(script_json["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_felix_video_timeline"]["count"])
    data["edge_owner_to_timeline_media"] = str(script_json["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["count"])
    data["edge_saved_media"] = str(script_json["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_saved_media"]["count"])
    data["edge_media_collections"] = str(script_json["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_media_collections"]["count"])

    ## All values below for further data analysis
    data["viewerId"] = script_json["config"]["viewerId"]
    data["csrf_token"] = script_json["config"]["csrf_token"]
    data["device_id"] = script_json["device_id"]
    data["platform"] = script_json["platform"]
    data["rollout_hash"] = script_json["rollout_hash"]
    data["nonce"] = script_json["nonce"]
    return data

## will return parsed html to parse_data function above.
def scrape_data(username):
    browser.get(URL.format(username))
    return parse_data(bs(browser.page_source, "html.parser"))

## This function will take data dictonary in input and will save all of data "smartly" in a csv file. 
def check_csv_file(data, filename):
    ## If the csv file exist or you're this code again this will check for your existing data in 
    if path.isfile(OUTPUT_FOLDER + filename):
        with open(OUTPUT_FOLDER + filename, "r") as rf:
            last_line_items, true_false_list, specific_key_index = rf.readlines()[-1].split(","), [], [0, 2, 3, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
            for key_index in specific_key_index:
                true_false_list.append(data[list(data.keys())[key_index]] == last_line_items[key_index])
            if False in true_false_list:
                with open(OUTPUT_FOLDER + filename, "a", newline = "") as csvfile:
                    csvwriter = csv.writer(csvfile)
                    csvwriter.writerow([data[keys] for keys in data.keys()])
    
    ## This block will create an csv file if you are runnig this script first time.
    else:
        with open(OUTPUT_FOLDER + filename, "a", newline = "") as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(list(data.keys()))
            csvwriter.writerow([data[keys] for keys in data.keys()])

## this function will help us to create randomness in scraper, so we can save our little a** from facebook's anti scraping tools.
def random_sleep_time(secends):
    return random.randint(secends - (secends * 0.3), secends + (secends * 0.4))

## Exit options will called if you pressed "CTRL+C"
def exit_options():
    print("\n\nWelcome to exit options, you have choices below\n1). Exit and close this script\n\n2). Do nothing, I intrupted accidently")
    your_choice = int(input("\nYour command >>> "))
    if your_choice == 1:
        exit()
    else: pass

## This function will take instagram credentials as input, and will login your id as output in browser.
## Warning please make sure that you are using temporary ids to signin and scraping profiles.
def ig_login(email, password):
    print(f"\nTrying to logging in using {email}...")
    slack.post(text = f"Trying to logging in using {email}")
    browser.get("https://instagram.com")
    browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    time.sleep(2.6)
    browser.execute_script("window.scrollTo(document.body.scrollHeight, 0)")
    time.sleep(0.6)
    a = browser.find_element_by_xpath('//*[@id="loginForm"]/div/div[1]/div/label/input')
    a.click()
    time.sleep(3.7)
    for words in email:
        a.send_keys(words)
    time.sleep(0.3)
    b = browser.find_element_by_xpath('//*[@id="loginForm"]/div/div[2]/div/label/input')
    b.click()
    time.sleep(1.6)
    for words in password:
        b.send_keys(words)
    time.sleep(0.25)
    browser.find_element_by_xpath('//*[@id="loginForm"]/div/div[3]/button/div').click()
    print(f"\nSuccessfully logged in {email}...")
    slack.post(text = f"Successfully logged in {email}")
    time.sleep(20)
    try:
        browser.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div/div/div/button').click()
        time.sleep(15)
        browser.find_element_by_xpath('/html/body/div[4]/div/div/div/div[3]/button[2]').click()
        time.sleep(15)
    except:
        pass ## Needs to be solved

## request to our browser to take and save an screenshot "smartly".
t1 = None
def save_ss(event = None):
    global t1
    t2 = time.time()
    if not t1 or ((t2-t1)>120):# 2Minutes
        now = datetime.now(timezone(TimeZone)) ## Change timezone according to your country or state.
        browser.get_screenshot_as_file(f'./ss_log/browser/{now.strftime("%d_%m_%Y")}__{now.strftime("%H_%M")}.png')
        print(f'\nBrowser Screenshot saved at ./ss_log/browser/{now.strftime("%d_%m_%Y")}__{now.strftime("%H_%M")}.png')
        t1 = time.time() ## t1 will be replaced with current time if we succeed to take a screenshot.
    else: print(f"\nScreenshot events cancelled because last ss was taken {t2-t1} secends ago")


## To send alerts to your slack installed devices
t3 = None
def slack_hook(username, exception):
    global t3
    t4 = time.time()
    if not t3 or ((t4-t3)>120):# 2Minutes
        slack.post(text = f"Exception Occurred while scraping for {username}\n "+ str(exception))
        t3 = time.time() ## t3 will be replaced with current time.
    else: print(f"\nSlack hook event cancelled because last text was just posted {t4-t3} secends ago")

## To get public IP of Tor
def get_tor_ip():
    try:
        return get("http://httpbin.org/ip", proxies = proxies).text.split('"')[3] ## return ip as string
    except Exception as e:
        exception = format_exc()
        print(f"\nException Occurred while checking current ip\n", str(exception))

## To change Tor identity(IP)
def renew_tor_ip():
    ## change ControlPort as your configuration.
    with Controller.from_port(port = ControlPort) as controller:
        controller.authenticate()
        controller.signal(Signal.NEWNYM) ## input authentication password as string.


## This Function will log out your id from browser, after logout succeed all cookies will be deleted so we can login new id.
def ig_logout(email):
    browser.get("https://instagram.com")
    print(f"\nTrying to logging out {email}...")
    slack.post(text = f"Trying to logging out {email}")
    browser.find_element_by_xpath('//*[@id="react-root"]/section/nav/div[2]/div/div/div[3]/div/div[5]/span').click()
    time.sleep(1)
    browser.find_element_by_xpath('//div[text() = "Log Out"]').click()
    browser.delete_all_cookies()
    print(f"\nSuccessfully logged out {email}")
    slack.post(text = f"Successfully logged out {email}")

temp_id1 = random.choice([keys for keys in ids.keys()]) ## To load credentials from ids dictionary (randomly).
ig_login(email = temp_id1, password = ids[temp_id1]) ## To login your temprary id in browser
t5 = time.time()

while True: ## To keep running this scraper.
    for username in usernames: ## load a instagram username from usernames list, which we have loaded previously
        filename = f"{username}.csv" ## name of csv file
        try:
            data = scrape_data(username)
            check_csv_file(data, filename)
            print("\n", username, " ", data)
            sleep_time = random_sleep_time(120)# 2 Minutes
            print(f"\nsleeping for {sleep_time} secends.....")
            time.sleep(sleep_time)
            
            ## To logout automaticly if script is running from past 8 hours, else instagram will block our temprory id.
            if (time.time()-t5) > (8*3600):# 8 Hours
                ig_logout(email = temp_id1)
                t5, temp_id2 = time.time(), random.choice([keys for keys in ids.keys()])
                ig_login(email = temp_id2, password = ids[temp_id2]) ## login new id
                temp_id1 = temp_id2 ## variable will replaed if autologin succeed.
        except KeyboardInterrupt:
            print("\n^C Detected. Taking you to exit options....")
            exit_options()
        except Exception as e:
            exception = format_exc() ## to format exceptions
            print(f"\nException Occurred while scraping for {username}", str(exception))
            save_ss()
            slack_hook(username, exception)