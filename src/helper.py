import os
import re
import logging
import phonenumbers
from bs4 import BeautifulSoup


logger = logging.getLogger("scrapy")

CONTACT_KEYWORDS = [
    "contact", "about", "company", "support", "get-in-touch", "reach-us", 
    "contact-us", "get-in-touch", "reach-out", "customer-service", "help", 
    "support-center", "helpdesk", "service", "contact-form", "inquiries", 
    "connect", "support-us", "questions", "talk-to-us", "contact-information", 
    "contact-details", "contact-support", "contact-us-now", "email-us", 
    "call-us", "client-support", "get-help", "how-to-reach-us", "contact-page", 
    "customer-care"
]
SOCIAL_MEDIA_PLATFORMS = [
    "facebook"#, "twitter", "instagram", "linkedin", "youtube", "tiktok", "pinterest", "snapchat"
]
MAX_SIZE_URL = int(os.getenv("MAX_SIZE_URL", 100))


def parse_for_contact_page(URL, htmls):
    if not len(htmls):
        logger.warning(f"Nothing to search for (contact page) in empty html page")
        return None

    soup = BeautifulSoup(htmls[0], "html.parser")
    links = []

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if any(word in href.lower() for word in CONTACT_KEYWORDS):
            logger.debug(f"Might found contact link in {href.lower()} in ")
            if not href.startswith("http"):
                href = URL.rstrip("/") + "/" + href.lstrip("/")
            links.append(href)

    logger.debug(f"A number of {len(links)} have been found!")
    return links

def format_phone_number(phone_number):
    return phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)

def find_phone_number(htmls, country="US"):
    to_return = []
    for html in htmls:
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator=" ")

        phone_numbers = phonenumbers.PhoneNumberMatcher(text, country)

        valid_numbers = []
        for match in phone_numbers:
            if phonenumbers.is_valid_number(match.number):
                formatted_number = format_phone_number(match.number)
                valid_numbers.append(formatted_number)
        to_return.extend(valid_numbers)
    return to_return

def clean_social_media(url):
    url = re.sub(r"^(https?://)?(www\.)?", "", url)
    return url

def find_social_media(htmls):
    to_return = []
    for html in htmls:
        soup = BeautifulSoup(html, "html.parser")
        links = soup.find_all("a", href=True)

        social_links = []

        for link in links:
            url = link.get("href")
            if any(platform in url.lower() for platform in SOCIAL_MEDIA_PLATFORMS):
                if len(url) < MAX_SIZE_URL:
                    cleaned_url = clean_social_media(url)
                    social_links.append(cleaned_url)
        to_return.extend(social_links)
    return to_return