import requests
import link_converter
import url_safety

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

def check_url_exsistence(url):
    try:
        url = link_converter.normalize_url(url)
        response = url_safety.safe_get(url, headers=headers)
        if not response.ok:
            print(f"Error: Received status code {response.status_code} for URL: {url}")
            return False
        print(f"URL exists: {url} (Status code: {response.status_code})")
        return True
    except (requests.RequestException, url_safety.UnsafeURLError) as exception:
        print(exception)
        return False

def error():
    print("error")