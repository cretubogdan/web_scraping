import os
import requests
import logging

import helper

logger = logging.getLogger("scrapy")

TIMEOUT = int(os.getenv("TIMEOUT", 5))


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

    def get_id(self):
        return self.id

    def fetch(self, overrided_url = None):
        url = self.URL
        if overrided_url:
            url = overrided_url
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=TIMEOUT)
            if 200 == response.status_code:
                self.html.append(response.text)
                # if url.startswith("http://"):
                #     file = url[7:]
                # elif url.startswith("https://"):
                #     file = url[8:]
                # file = "sample/" + file.replace("/", "-") + ".html"
                # with open(file, "w") as f:
                #     f.write(response.text)
            else:
                logger.warning(f"Couldn't process {url} Response: {response.status_code} Mesage: {self.id}.log")
                with open(f"sample/{self.id}.log", "w") as f:
                    f.write(response.text)
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
        return [
            self.orig_URL,
            " | ".join(self.phone_number),
            " | ".join(self.social_media)
        ]
