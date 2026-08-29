import link_finder
import requests
from bs4 import BeautifulSoup

urls = link_finder.find_links("kiwihacks.org")
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
content = []

def get_content(link):
        global content
        response = requests.get(link, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        redirect = soup.find("meta", attrs={"http-equiv": "refresh"})

        if redirect:
            redirect_content = redirect.get("content", "")
            
            if "URL=" in redirect_content:
                redirect_url = redirect_content.split("URL=", 1)[1].strip()

                response = requests.get(redirect_url, headers=headers, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
        return soup

def get_paragraphs(soup):
        global content
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = (p.get_text())
            content.append(text)
    
def scrape_links():
    for link in urls:
        get_paragraphs(get_content(link))
    return content