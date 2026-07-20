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

#Returns all links found in the footer of a given URL
def find_links(url):

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  
    except requests.RequestException as e:
        print(f"Error fetching URL: {e}")
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

def scrape_footers(url):
    anchors = find_links(url)
    if not anchors:
        print("No links found in the footer.")
        return
    checked_anchors = check_links(anchors)
    unique_list = check_duplicates(checked_anchors)
    found_links.append(unique_list)
    return found_links

results = scrape_footers("https://www.google.com")
print(results)