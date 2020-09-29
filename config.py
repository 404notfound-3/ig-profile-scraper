import time
from stem import Signal
from stem.control import Controller
from pytz import timezone
from datetime import datetime
from slack_webhook import Slack
from termcolor import cprint
from requests import get
from bs4 import BeautifulSoup as bs
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

TIMEZONE = timezone("Asia/Kolkata")
URL = "https://instagram.com/{}/"
SOCKSPort = 9050 ## Tor SOCKS listner port
ControlPort = 9051 ## Tor control listner port
OUTPUT_FOLDER = "./output/" ## Output Folder path
slack = Slack(url = "<<ADD_YOUR_SLACK_WEBHOOK_URL_HERE")
## Proxies for request over Tor
proxies = {
    "http" : f"socks5h://localhost:{SOCKSPort}",
    "https": f"socks5h://localhost:{ControlPort}"
}
## dict of temporary instagram ids
ids = {
    "temp/fake_id1" : "password1",
    "temp/fake_id2" : "password2"
}
## list of instagram usernames to scrape/monitor.
usernames = ["<<ADD_INSTAGRAM_USERNAMES_IN_THIS_LIST>>"]

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


def date():
    return datetime.now(TIMEZONE).strftime("%d/%m/%Y")
def timee():
    return datetime.now(TIMEZONE).strftime("%H:%M:%S")
def weekday():
    return datetime.now(TIMEZONE).strftime("%A")

def lps(prefix, string, color):
    cprint(f"{prefix}[{timee()}][{date()}] {string}", color)
    slack.post(text = string)
def lprint(prefix, string, color):
    cprint(f"{prefix}[{timee()}][{date()}] {string}", color)

def get_tor_ip():
    return get("http://httpbin.org/ip", proxies = proxies).text.split('"')[3]
def renew_tor_ip():
    ip_before_renewel = get_tor_ip()
    with Controller.from_port(port = 9056) as controller:
        controller.authenticate()
        controller.signal(Signal.NEWNYM)
        lprint("[*]", "Sleeping for 5 secends...", "green")
        time.sleep(5)
    ip_after_renewel = get_tor_ip()
    if (ip_before_renewel != ip_after_renewel):
        lprint(f"[+]", f"Tor IP renewel confirmed, new ip appears to be {ip_after_renewel}", "green")
    else:
        lprint("[!]", "Tor IP renewel faild!, trying again...", "red"), renew_tor_ip()
## to verify Tor connectivity
def check_tor_conn():
    title = str(bs(get("https://check.torproject.org", proxies = proxies).text, "html.parser").title).split("\n")[2]
    if "Congratulations." in title:
        lps("[+]", "Tor Connectivity Verified", "blue")
    elif "not using Tor" in title:
        lps("[-]", "Tor is not configured correctly, Try 'sudo service tor restart'. Aborting...", "red")
        exit()