from urllib.parse import urlparse

def normalize_url(raw):
    if not raw.startswith(("http://", "https://")):
        raw = "https://" + raw
    if raw.endswith("/"):
        raw = raw[:-1]
    return raw

def get_domain(url):
    return urlparse(url).netloc