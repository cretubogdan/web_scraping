import asyncio
import aiohttp
import re
from bs4 import BeautifulSoup
import phonenumbers
from phonenumbers import geocoder, carrier
import requests
import logging
import os


logger = logging.getLogger("main")

CONTACT_KEYWORDS = ["contact", "about", "company", "support", "get-in-touch", "reach-us"]
SOCIAL_MEDIA_PLATFORMS = [
    "facebook", "twitter", "instagram", "linkedin", "youtube", "tiktok", "pinterest", "snapchat"
]

TIMEOUT = int(os.getenv("TIMEOUT", 5))
MAX_SIZE_URL = int(os.getenv("MAX_SIZE_URL", 100))

class Task:
    def __init__(self, URL, id):
        self.orig_URL = URL
        if not URL.startswith("http"):
            URL = "http://" + URL
        self.id = id
        self.URL = URL
        self.phone_number = []
        self.address = []
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

    def _parse_for_contact_page(self):
        if not len(self.html):
            logger.warning(f"Nothing to search for (contact page) in empty html page")
            return None

        soup = BeautifulSoup(self.html[0], "html.parser")
        links = []

        for a in soup.find_all("a", href=True):
            href = a["href"]
            if any(word in href.lower() for word in CONTACT_KEYWORDS):
                logger.debug(f"Might found contact link in {href.lower()} in ")
                if not href.startswith("http"):
                    href = self.URL.rstrip("/") + "/" + href.lstrip("/")
                links.append(href)

        logger.debug(f"A number of {len(links)} have been found!")
        return links
    
    def _find_phone_number(self, country="US"):
        for html in self.html:
            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text(separator=" ")

            phone_numbers = phonenumbers.PhoneNumberMatcher(text, country)

            valid_numbers = []
            for match in phone_numbers:
                if phonenumbers.is_valid_number(match.number):
                    formatted_number = phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.E164)
                    valid_numbers.append(formatted_number)
            self.phone_number.extend(valid_numbers)

    def _find_social_media(self):
        for html in self.html:
            soup = BeautifulSoup(html, "html.parser")
            links = soup.find_all("a", href=True)

            social_links = []

            for link in links:
                url = link.get("href")
                if any(platform in url.lower() for platform in SOCIAL_MEDIA_PLATFORMS):
                    if len(url) < MAX_SIZE_URL:
                        social_links.append(url)
            self.social_media.extend(social_links)

    def _find_address(self):
        address_patterns = [
            r"\d{1,5}\s\w+\s\w+",  # Matches formats like "123 Main St"
            r"\d{5}(-\d{4})?",  # Matches ZIP codes, e.g., 12345 or 12345-6789
            r"[A-Za-z]+,\s[A-Za-z]+",  # Matches city and state like "New York, NY"
            r"[A-Za-z]+,\s[A-Za-z]+\s\d{5}",  # Matches city, state, and ZIP code like "New York, NY 10001"
        ]

        for html in self.html:
            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text()

            addresses = []

            for pattern in address_patterns:
                found_addresses = re.findall(pattern, text)
                addresses.extend(found_addresses)
            self.address.extend(addresses)

    def run(self):
        if not len(self.html):
            logger.info(f"Nothing to do for {self.URL}, as html is empty")
            return
        
        links = self._parse_for_contact_page()
        links = list(set(links))
        # with open("sample/" + self.URL[7:] + ".txt", "w") as f:
        #     for link in links:
        #         f.write(link + "\n")
        for link in links:
            self.fetch(link)
        
        self._find_phone_number()
        self.phone_number = list(set(self.phone_number))
        self._find_social_media()
        self.social_media = list(set(self.social_media))
        # self._find_address()
        # self.address = list(set(self.address))


    def get_result(self):
        return [
            self.orig_URL,
            "|".join(self.phone_number),
            # "|".join(self.address),
            "|".join(self.social_media),
        ]
