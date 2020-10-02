import csv
import time
import json
import random
import subprocess
from os import path, name
from selenium import webdriver
from traceback import format_exc
from bs4 import BeautifulSoup as bs
from pyvirtualdisplay import Display
from config import URL, slack, proxies, date, timee, weekday, lps, lprint, get_tor_ip, renew_tor_ip, profile, OUTPUT_FOLDER, usernames, ids, check_tor_conn


## This block will check for your OS.
if name == "nt":## To wake up Tor executables(only windows).
    subprocess.Popen(r".\Tor\tor.exe -f .\Tor\torrc", shell = False)
elif name == "posix":## To create virtual display(only linux).
    display = Display(visiable = False, size = (13666, 768))
    display.start()
    lprint("[+]", "Successfully started virtual display", "green")
check_tor_conn()

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
    data["date"], data["time"], data["weekday"] = date(), timee(), weekday()
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
    ## Check for the existing csv file
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
    return random.randint(secends-(secends * 0.3), secends+(secends * 0.4))

## Exit options will called if you pressed "CTRL+C"
def exit_options():
    print("\n\nWelcome to the exit options, you have choices below\n1). Exit and close this script\n\n2). Do nothing, I intrupted accidently")
    your_choice = int(input("\nYour command >>> "))
    if your_choice == 1:
        exit()
    else: pass

## This function will take instagram credentials as input, and will login your id as output in browser.
## Warning please make sure that you are using temporary ids to signin and scraping profiles.
def ig_login(email, password):
    lps("[*]", f"Trying to logging in using {email}", "yellow")
    browser.get("https://instagram.com")
    username_input_box = browser.find_element_by_xpath('//*[@id="loginForm"]/div/div[1]/div/label/input')
    username_input_box.click()
    time.sleep(3.7)
    for words in email:
        username_input_box.send_keys(words)
        time.sleep(0.3)
    password_input_box = browser.find_element_by_xpath('//*[@id="loginForm"]/div/div[2]/div/label/input')
    password_input_box.click()
    time.sleep(1.6)
    for words in password:
        password_input_box.send_keys(words)
        time.sleep(0.25)
    browser.find_element_by_xpath('//*[@id="loginForm"]/div/div[3]/button/div').click()
    lps("[+]", f"Successfully logged in {email}", "green")
    time.sleep(15)
    browser.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div/div/div/button').click()
    time.sleep(15)
    browser.find_element_by_xpath('/html/body/div[4]/div/div/div/div[3]/button[2]').click()
    time.sleep(15)

## request to browser to take and save an screenshot "smartly".
t1 = None
def save_ss(event = None):
    global t1
    t2 = time.time()
    if not t1 or ((t2-t1)>120):# 2 Minutes
        browser.get_screenshot_as_file(f'./ss_log/browser/{date()}__{timee()}.png')
        lps("[+]", "Browser Screenshot Successfully saved at ./ss_log/browser/", "green")
        t1 = time.time() ## t1 will be replaced with current time if we succeed to take a screenshot.
    else: lprint("[-]", f"Screenshot event cancelled, last ss was taken just {t2-t1} secends ago", "yellow")

## To send alerts to your slack installed devices
t3 = None
def slack_hook(username, exception):
    global t3
    t4 = time.time()
    if not t3 or ((t4-t3)>120):# 2 Minutes
        lps("[!]", f"Exception Occurred while scraping for {username}\n{str(exception)}", "red")
        t3 = time.time() ## t3 will be replaced with current time.
    else: lprint("[-]", f"Slack text cancelled, last text was just posted {t4-t3} secends ago", "yellow")

## This Function will log out your id from browser, after logout succeed all cookies will be deleted so we can login new id.
def ig_logout(email):
    browser.get("https://instagram.com/")
    lps("[*]", f"Trying to logging out {email} ", "yellow")
    browser.find_element_by_xpath('//*[@id="react-root"]/section/nav/div[2]/div/div/div[3]/div/div[5]/span').click()
    time.sleep(1)
    browser.find_element_by_xpath('//div[text() = "Log Out"]').click()
    browser.delete_all_cookies()
    lps("[+]", f"Successfully logged out {email}", "green")

temp_id1 = random.choice([keys for keys in ids.keys()]) ## To load credentials from ids dictionary (randomly).
ig_login(email = temp_id1, password = ids[temp_id1]) ## To login your temprary id in browser
t5 = time.time()

while True: ## To keep running this scraper.
    for username in usernames: ## load a instagram username from usernames list, which we have loaded previously
        filename = f"{username}.csv" ## name of csv file
        try:
            data = scrape_data(username)
            check_csv_file(data, filename)
            lprint("[+]", f"\n{username} {data}", random.choice(["magenta", "cyan", "blue"]))
            sleep_time = random_sleep_time(120)# 2 Minutes
            lprint("[*]", f"Sleeping for {sleep_time} secends", "green")
            time.sleep(sleep_time)
            ## To logout automaticly if script is running from past 8 hours, else instagram will block our temprory id.
            if (time.time()-t5) > (8*3600):# 8 Hours
                ig_logout(email = temp_id1)
                t5, temp_id2 = time.time(), random.choice([keys for keys in ids.keys()])
                ig_login(email = temp_id2, password = ids[temp_id2]) ## login new id
                temp_id1 = temp_id2 ## variable will replaed if autologin succeed.
        except KeyboardInterrupt:
            lprint("[-]", "CTRL+C detected, Taking you to exit options...", "red")
            exit_options()
        except Exception as e:
            exception = format_exc(e) ## to format exceptions
            lprint("[!]", f"Exception Occurred while scraping for {username}\n{str(exception)}", "red")
            save_ss()
            slack_hook(username, exception)