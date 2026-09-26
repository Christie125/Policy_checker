import os

from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import CSRFProtect
import link_finder, link_proccesor, link_scraper, link_converter
import user_input

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
csrf = CSRFProtect(app)
    
@app.route('/', methods=['GET', 'POST'])
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
    found_links = link_finder.find_links(domain)
    scraped_links = link_scraper.scrape_links(found_links)
    proccessed_content = link_proccesor.synthesise_scraped_data(scraped_links)
    print(f"Processed content to be displayed: {proccessed_content}")
    return render_template('content.html', content=proccessed_content)

if __name__ == "__main__":
    print("Starting Flask app")
    app.run(debug=True, use_reloader=False)