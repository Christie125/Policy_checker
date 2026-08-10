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
def check_links(anchors):
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

#Combines the above methods to scrape footers and return a list of unique links that contain keywords from the KEYWORDS list
def scrape_footers(url):
    anchors = find_links_footers(url)
    if not anchors:
        return found_links
    checked_anchors = check_links(anchors)
    unique_list = check_duplicates(checked_anchors)
    found_links.extend(unique_list)
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

#Getting links from robots.txt file, only if User-agent: * is present and Disallow is not present
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

#Combines the above methods to scrape robots.txt and return a list of unique links that contain keywords from the KEYWORDS list
def scrape_robots_txt(domain):
    robots_txt = get_robots_txt(domain)
    if robots_txt:
        links = extract_links_robots_txt(robots_txt)
        checked_links = check_links(links)
        unique_list = check_duplicates(checked_links)
        found_links.extend(unique_list)
    return found_links

#Link method #3 -- scraping sitemap.xml
def get_sitemap(domain):
    url = f"https://{domain}/sitemap.xml"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException:
        return None

#Extracts links from the sitemap.xml file
def extract_links_sitemap(sitemap_xml):
    links = []
    if sitemap_xml is None or not sitemap_xml:
        return links
    soup = BeautifulSoup(sitemap_xml, 'xml')
    for url in soup.find_all('loc'):
        link = url.get_text(strip=True)
        links.append(link)
    return links

def scrape_sitemap(domain):
    sitemap_xml = get_sitemap(domain)
    if sitemap_xml:
        links = extract_links_sitemap(sitemap_xml)
        checked_links = check_links(links)
        unique_list = check_duplicates(checked_links)
        found_links.extend(unique_list)
    return found_links

#Combines all methods to find the complete list of unique links that contain keywords from the KEYWORDS list
def find_links(domain):
    scrape_robots_txt(domain)
    scrape_footers(f'https://{domain}')
    scrape_sitemap(domain)
    return found_links

print(find_links("google.com"))