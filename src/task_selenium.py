import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

import helper


logger = logging.getLogger("scrapy")

TIMEOUT = int(os.getenv("TIMEOUT", 5))
SELENIUM_DRIVE = os.getenv("SELENIUM_DRIVE")

class Task:
    def __init__(self, URL, id):
        self.orig_URL = URL
        if not URL.startswith("http"):
            URL = "http://" + URL
        self.id = id
        self.URL = URL
        self.phone_number = []
        self.social_media = []
        self.html = []
        self.driver = webdriver.Chrome(service=Service(SELENIUM_DRIVE))

    def __del__(self):
        self.driver.quit()

    def get_id(self):
        return self.id

    def fetch(self, overrided_url = None):
        url = self.URL
        if overrided_url:
            url = overrided_url
        try:
            self.driver.get(url)
            time.sleep(TIMEOUT)
            self.html.append(self.driver.page_source)
            # if url.startswith("http://"):
            #     file = url[7:]
            # elif url.startswith("https://"):
            #     file = url[8:]
            # file = "sample/" + file.replace("/", "-") + ".html"
            # with open(file, "w") as f:
            #     f.write(self.driver.page_source)
        except Exception as e:
            logger.warning(f"Couldn't process {url}")
        logger.debug(f"Fetch for {url} finished successfully!")

    def run(self):
        if not len(self.html):
            logger.info(f"Nothing to do for {self.URL}, as html is empty")
            return
        
        links = helper.parse_for_contact_page(self.URL, self.html)
        links = list(set(links))
        # with open("sample/" + self.URL[7:] + ".txt", "w") as f:
        #     for link in links:
        #         f.write(link + "\n")
        for link in links:
            self.fetch(link)
        
        phones = helper.find_phone_number(self.html)
        self.phone_number.extend(phones)
        self.phone_number = list(set(self.phone_number))

        social_m = helper.find_social_media(self.html)
        self.social_media.extend(social_m)
        self.social_media = list(set(self.social_media))


    def get_result(self):
        url = self.orig_URL
        phone_number = self.phone_number[0] if len(self.phone_number) else ''
        social_media = self.social_media[0] if len(self.social_media) else ''
        return [
            url,
            phone_number,
            social_media
        ]
