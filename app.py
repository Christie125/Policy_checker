import os
import traceback

from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import link_finder, link_proccesor, link_scraper, link_converter
import user_input

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable is not set")
app.config['SECRET_KEY'] = SECRET_KEY

csrf = CSRFProtect(app)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=os.getenv("RATE_LIMIT_STORAGE_URI", "memory://"),
    headers_enabled=True,
)

@app.errorhandler(429)
def ratelimit_handler(e):
    return "Too many requests - please wait a moment and try again.", 429

@app.route('/', methods=['GET', 'POST'])
@limiter.limit("10 per minute", methods=["POST"])
def input():
    print("Rendering input page")
    if request.method == 'POST':
        print("Processing form submission")
        url = request.form.get('url')
        if not url:
            return render_template('input.html')
        url = link_converter.normalize_url(url)
        print(f"Received URL: {url}")
        if user_input.check_url_exsistence(url):
                print(f"Redirecting to content page for URL: {url}")
                return redirect(url_for('content', url=url))
    return render_template('input.html')

@app.route('/content')
@limiter.limit("10 per minute")
def content():
    print("Rendering content page")
    url = request.args.get('url')
    if not url:
        return redirect(url_for('input'))
    url = link_converter.normalize_url(url)
    if not user_input.check_url_exsistence(url):
        return redirect(url_for('input'))
    domain = link_converter.get_domain(url)
    print(f"Extracted domain from URL: {domain}")
    try:
        found_links = link_finder.find_links(domain)
        scraped_links = link_scraper.scrape_links(found_links)
        proccessed_content = link_proccesor.synthesise_scraped_data(scraped_links)
    except Exception:
        traceback.print_exc()
        proccessed_content = "<p>Error processing content. Please try again later.</p>"
    print(f"Processed content to be displayed: {proccessed_content}")
    return render_template('content.html', content=proccessed_content)

@app.errorhandler(500)
def internal_error_handler(e):
    traceback.print_exc()
    return render_template('content.html', content="<p>Error processing content. Please try again later.</p>"), 500

if __name__ == "__main__":
    print("Starting Flask app")
    app.run()