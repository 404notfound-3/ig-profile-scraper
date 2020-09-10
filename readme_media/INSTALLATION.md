# Installation and Setup
* [For windows](##For-Windows)
* [For Linux](##For-Linux)

## For Windows

* Download Mozillla firefox for windows from [here]().

* Download latest version of [geckodriver](https://github.com/mozilla/geckodriver/releases) according to your OS architecture.

* Extract `geckodriver.exe` and paste it to your python's installation DIR (by doing this we don't have to add an extra PATH to windows environment variables).
    ```
    C:\Users\<your_user_name>\Appdata\Local\Programs\Python\Python3X\
    ```

* To verify the installation of [geckeodriver](https://github.com/mozilla/geckodriver/releases) run `geckodriver -h` in command prompt and output should be look like this.
    ```
    PS C:\Users\sword> geckodriver -h
    geckodriver 0.27.0 (7b8c4f32cdde 2020-07-28 18:16 +0000)
    WebDriver implementation for Firefox
    ```

* Download latest [Tor browser](https://torproject.org/) for windows from official [website](https://torproject.org/).

* Run the installer and carefully select the installation PATH, your user's desktop path will be default.

* Git clone or Download [this project](https://github.com/404notfound-3/ig-profile-scraper) and run below command in project directory.
    ```
    pip install -r requirements.txt
    ```

* Open up `windows.py` in your favourite [text editor](https://github.com/404notfound-3/rpad) and
    * Replace timezone according to your country or state.
        ```
        TimeZone = "Asia/Kolkata"
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
    * Copy full path of tor.exe from Tor installation directory and add it in tor_exe.
        ```
        tor_exe = os.popen(r"C:\Program Files (x86)\Tor Browser\Browser\TorBrowser\Tor\tor.exe")
        ```
    * Add your Slack webhook URL to get notified about errors and exceptions while running this scraper.
        ```
        slack = Slack(url = "<<ADD_YOUR_SLACK_WEBHOOK_URL_HERE>>")
        ```
    Congratulations! you are ready to go, now run `windows.py`

## For linux
* Install firefox, xvfb and Tor for linux
    ```
    sudo apt-get install firefox xvfb tor
    ```
<!-- * Verify installation
    ```
    which firefox
    ``` -->
* Download and install geckodriver for linux.
    ```
    wget https://github.com/mozilla/geckodriver/releases/download/v0.27.0/geckodriver-v0.27.0-linux64.tar.gz
    tar xvzf geckodriver-v0.27.0-linux64.tar.gz
    cp geckodriver /usr/local/bin/
    ```
* Verify installations by running `which firefox` and `which geckodriver` output should be look like this.
    ```
    $ which firefox && which geckodriver
    /usr/bin/firefox
    /usr/local/bin/geckodriver
    ```
* Edit torrc file.
    ```
    sudo echo -e "SOCKSPort 9050\nControlPort 9051\nCookieAuthentication 1\n$(cat /etc/tor/torrc)" > /etc/tor/torrc
    ```
* Restart Tor service.
    ```
    sudo service tor restart
    ```
* Clone this project and install dependenceis
    ```
    git clone https://github.com/404notfound-3/ig-profile-scraper
    cd ig-profile-scraper/
    pip install -r requirements.txt
    ```
* Open `linux.py` in your favourite text editor and

    * Replace timezone according to your country or state.
        ```
        TimeZone = "Asia/Kolkata"
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
    Congratulations! you are ready to go, now run `linux.py`