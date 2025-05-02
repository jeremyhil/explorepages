from flask import Flask, request, render_template
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        sitemap_url = request.form.get('sitemap_url')
        page_data = process_sitemap(sitemap_url)
        return render_template('result.html', page_data=page_data)
    return render_template('index.html')

def process_sitemap(sitemap_url):
    response = requests.get(sitemap_url)
    if response.status_code != 200:
        return [{"url": sitemap_url, "title": "Error retrieving sitemap", "description": "", "title_length": 0, "desc_length": 0}]

    root = ET.fromstring(response.content)
    namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    urls = [elem.text for elem in root.findall('.//ns:loc', namespace)]

    page_data = []
    for url in urls:
        page_info = fetch_page_meta(url)
        page_data.append(page_info)

    return page_data

def fetch_page_meta(url):
    response = requests.get(url)
    if response.status_code != 200:
        return {"url": url, "title": "Error retrieving page", "description": "", "title_length": 0, "desc_length": 0}

    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.title.string if soup.title else "No Title"
    description_tag = soup.find("meta", attrs={"name": "description"})
    description = description_tag["content"] if description_tag else "No Description"

    return {
        "url": url,
        "title": title,
        "description": description,
        "title_length": len(title),
        "desc_length": len(description)
    }

if __name__ == '__main__':
    app.run(debug=True)