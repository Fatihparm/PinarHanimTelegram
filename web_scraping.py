import requests
from bs4 import BeautifulSoup
from data_models import ZodiacSign, TarotCard , Model
import logging

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s", 
    datefmt="%Y-%m-%d %H:%M:%S", 
    level=logging.INFO  
)

logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger("TelegramBot") 

model = Model()

class Scrape():
    def __init__(self):
        self.sign_url = "https://onedio.com/gunluk-burc-yorumlari-haberleri"
        self.tarot_url = "https://onedio.com/yasam/astroloji/tarot-fali"
        self.base_url = "https://onedio.com"

    def get_sign_link_set(self):
        response = requests.get(self.sign_url)
        page = BeautifulSoup(response.content, "html.parser")
        link_list = []
        link_set = set()
        deadline = ""
        link_day = ""
        content = page.find_all("a")
        links = [link["href"] for link in content if "-burcu-gunluk-burc-" in link["href"]] # filter out unnecessary links
        for link in links:
            link_day = link.split('/')[2].split('-')[0]
            if deadline == "": 
                deadline = link_day # deadline is the day of the first link in the list
            if link_day == deadline: 
                link_list.append(self.base_url + link)
        link_set = list(set(link_list)) # set() removes duplicates
        return link_set

    def sign_content_push(self):
        link_list = self.get_sign_link_set()
        for link in link_list:
            try:
                response = requests.get(link)
                page = BeautifulSoup(response.content, "html.parser")
                image_section = page.find("div", class_="image relative")
                image = image_section.find("img")["src"]
                caption = page.find("figcaption")
                content = caption.find_all("p")
                text = f"{content[0].text}\n\n{content[1].text}\n\nYarın görüşmek üzere, sevgiyle kal..."
                name = link.split('-')[2] 
                date = link.split('/')[4].split('-')[0]
                sign = ZodiacSign(name, text, date, image)
                model.insert_zodiac_sign(sign)
            except Exception as e:
                logger.error(f"An error occurred while adding the sign {name} to the database: {e}")
        logging.info("Zodiac signs are added to the database.")


    def get_tarot_link(self):
        response = requests.get(self.tarot_url)
        page = BeautifulSoup(response.content, "html.parser")
        content = page.find("div", class_="flex flex-col my-auto px-8 py-0")
        link = content.find("a")["href"]
        return self.base_url + link

    def tarot_content_push(self):
        link = self.get_tarot_link()
        
        response = requests.get(link)
        page = BeautifulSoup(response.content, "html.parser")
        
        content = page.find("article", class_="article px-4 sm:px-0 sm:pt-7.5 relative quiz")
        if content:
            sections = content.find_all("section", class_="entry entry--image image content-visibility-entry")
        else:
            logger.error("No content found for tarot link.")
            return
        
        for section in sections:
            name = ""
            try:
                name = section.find("h2").text
                description = section.find("p").text
                img = section.find("div", class_="image relative")
                image = img.find("img")["src"]
                tarot= TarotCard(name, description, image)
                model.insert_tarot_card(tarot)
            except Exception as e:
                logger.error(f"An error occurred while adding the tarot card {name} to the database: {e}")
        logging.info("Tarot cards are added to the database.")
