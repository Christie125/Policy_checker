import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

import url_safety

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

#Link method 1: scraping footers of website
def find_links_footers(url):

    try:
        response = url_safety.safe_get(url)
        response.raise_for_status()
    except (requests.RequestException, url_safety.UnsafeURLError) as e:
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all("a", href=True)

    anchors = []
    print(f"Found {len(links)} links in the footer of {url}")

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
        print("Checked anchors:", checked_anchors)
    return checked_anchors
            
#Returns a list of unique items from the input list
def check_duplicates(list_input):
    unique_list = []
    for item in list_input:
        if item not in unique_list:
            unique_list.append(item)
        print("Unique list:", unique_list)
    return unique_list

#Combines the above methods to scrape footers and return a list of unique links that contain keywords from the KEYWORDS list
def scrape_footers(url, found_links):
    anchors = find_links_footers(url)
    if not anchors:
        return found_links
    checked_anchors = check_links(anchors)
    unique_list = check_duplicates(checked_anchors)
    print("Final unique links:", unique_list)
    found_links.extend(unique_list)
    return found_links

#Link methods #2 -- scraping robots.txt
def get_robots_txt(domain):
    url = f"https://{domain}/robots.txt"

    try:
        response = url_safety.safe_get(url)
        response.raise_for_status()
        return response.text
    except (requests.RequestException, url_safety.UnsafeURLError):
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
        print(f"Extracted links from robots.txt: {links}")
    return links

#Combines the above methods to scrape robots.txt and return a list of unique links that contain keywords from the KEYWORDS list
def scrape_robots_txt(domain, found_links):
    robots_txt = get_robots_txt(domain)
    if robots_txt:
        links = extract_links_robots_txt(robots_txt)
        absolute_links = [urljoin(f"https://{domain}", link) for link in links]
        checked_links = check_links(absolute_links)
        unique_list = check_duplicates(checked_links)
        found_links.extend(unique_list)
    return found_links

#Link method #3 -- scraping sitemap.xml
def get_sitemap(domain):
    url = f"https://{domain}/sitemap.xml"

    try:
        response = url_safety.safe_get(url, timeout=15)
        response.raise_for_status()
        return response.text
    except (requests.RequestException, url_safety.UnsafeURLError):
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

#Puts all the sitemap methods together to scrape the sitemap.xml file and return a list of unique links that contain keywords from the KEYWORDS list
def scrape_sitemap(domain, found_links):
    sitemap_xml = get_sitemap(domain)
    if sitemap_xml:
        links = extract_links_sitemap(sitemap_xml)
        checked_links = check_links(links)
        unique_list = check_duplicates(checked_links)
        print(f"Unique links from sitemap: {unique_list}")
        found_links.extend(unique_list)
    return found_links

#Combines all methods to find the complete list of unique links that contain keywords from the KEYWORDS list
def find_links(domain):
    found_links = [] 
    scrape_robots_txt(domain, found_links)
    scrape_footers(f'https://{domain}', found_links)
    scrape_sitemap(domain, found_links)
    print(f"Found links for domain {domain}: {found_links}")
    return found_links
