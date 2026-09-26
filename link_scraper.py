import link_finder
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

import url_safety

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

def get_content(link):
        try:
            response = url_safety.safe_get(link, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')

            redirect = soup.find("meta", attrs={"http-equiv": "refresh"})

            if redirect:
                redirect_content = redirect.get("content", "")

                if "URL=" in redirect_content:
                    redirect_url = redirect_content.split("URL=", 1)[1].strip()
                    redirect_url = urljoin(link, redirect_url)

                    response = url_safety.safe_get(redirect_url, headers=headers)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, 'html.parser')
            return soup
        except (requests.RequestException, url_safety.UnsafeURLError) as e:
            print(f"Failed to fetch {link}: {e}")
            return BeautifulSoup("", 'html.parser')

def get_paragraphs(soup, content):
    paragraphs = soup.find_all('p')
    for p in paragraphs:
        text = p.get_text()
        content.append(text) 
    
def scrape_links(urls):
    content = []
    for link in urls:
        get_paragraphs(get_content(link), content)
    print(f"Scraped content: {content}")
    return content