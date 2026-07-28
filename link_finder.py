import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

KEYWORDS = [
    "legal",
    "terms",
    "privacy",
    "cookies",
    "policy",
    "disclaimer",
    "agreement",
    "notice",
    "conditions",
    "acceptable use",
]

found_links = []

#Link method 1: scraping footers of website
def find_links_footers(url):

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  
    except requests.RequestException as e:
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all("a", href=True)

    anchors = []

    for link in links:
            absolute = urljoin(url, link["href"])
            anchors.append(absolute)

    return anchors
    

#Returns list of links that contain keywords from the KEYWORDS list
def check_footer_links(anchors):
    checked_anchors = []

    for anchor in anchors:
        for keyword in KEYWORDS:
            if keyword.strip().lower() in anchor.strip().lower():
                checked_anchors.append(anchor)
                break
    return checked_anchors
            
#Returns a list of unique items from the input list
def check_duplicates(list_input):
    unique_list = []
    for item in list_input:
        if item not in unique_list:
            unique_list.append(item)
    return unique_list

def scrape_footers(url):
    anchors = find_links_footers(url)
    if not anchors:
        return found_links
    checked_anchors = check_footer_links(anchors)
    unique_list = check_duplicates(checked_anchors)
    found_links.append(unique_list)
    return found_links

#Link methods #2 -- scraping robots.txt
def get_robots_txt(domain):
    url = f"https://{domain}/robots.txt"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException:
        return None

def extract_links_robots_txt(robots_txt):
    links = []
    if robots_txt is None or not robots_txt:
        return links
    if robots_txt.startswith("User-agent: *"):
        for line in robots_txt.splitlines():
            if line.startswith("Disallow:"):
                continue
            if line.startswith("Allow:"):
                path = line.split("Allow:")[1].strip()
                if path:
                    links.append(path)
    return links

def check_links_robots_txt(links):
    checked_links = []
    for link in links:
        for keyword in KEYWORDS:
            if keyword.strip().lower() in link.strip().lower():
                checked_links.append(link)
                break
    return checked_links

def scrape_robots_txt(domain):
    robots_txt = get_robots_txt(domain)
    if robots_txt:
        links = extract_links_robots_txt(robots_txt)
        checked_links = check_links_robots_txt(links)
        unique_list = check_duplicates(checked_links)
        found_links.append(unique_list)
    return found_links

def find_links(domain):
    scrape_robots_txt(domain)
    scrape_footers(f'https://{domain}')
    return found_links
