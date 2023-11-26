import scrapy
from urllib.parse import urlencode
import pdfkit
import re
import json
from bs4 import BeautifulSoup
from ..helpers import generate_pdfs_file_path

options = {
    "disable-javascript": None,
    "disable-external-links": None,
    "quiet": None,
    "encoding": "UTF-8",
}


class MetaSpider(scrapy.Spider):
    name = "meta_spider"
    start_urls = [
        "https://engineering.fb.com/category/core-infra/",
        "https://engineering.fb.com/category/data-infrastructure/",
        "https://engineering.fb.com/category/developer-tools/",
        "https://engineering.fb.com/category/production-engineering/",
        "https://engineering.fb.com/category/security/",
    ]
    post_fetched = 0

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, self.parse_initial)
    def parse_initial(self, response):
        endpoint, query_args = get_loadmore_endpoints_and_params(response)
        for page in range(3):
            params = {
                "action": "loadmore",
                "queryArgs": query_args,
                "page": page,
                "post_type": "post",
            }
            # print(query_args)
            loadmore_endpoint = get_load_more_posts_url(endpoint, params=params)
            # print(loadmore_endpoint)
            yield scrapy.Request(url=loadmore_endpoint,  callback=self.parse_loadmore)

    def parse_loadmore(self, response):
        # print("parse_loadmore called with response: {}".format(response.text))
        resp = scrapy.Selector(text=response.json())
        # Create a TextResponse object
        for post in resp.css("article.post"):
            header = post.css("header.entry-header")
            title = header.css(".entry-title a::text").get().strip()
            url = header.css(".entry-title a::attr(href)").get()

            # Sanitize the title to create a valid filename
            safe_title = re.sub(r"[^\w\s-]", "", title).replace(" ", "_")
            yield scrapy.Request(
                url, callback=self.parse_post, meta={"title": safe_title}
            )
        
    def parse_post(self, response):
        footer = response.css("footer.entry-footer").get()
        if "podcast" in (footer or "").lower():
            return

        title = response.meta["title"]
        soup = BeautifulSoup(response.css(".post").get(), "html.parser")
        clean_post_html(soup)

        html_content = soup.prettify()

        pdf_path = generate_pdfs_file_path(title)
        print(f"saving pdf to {pdf_path}....")

        try:
            pdfkit.from_string(html_content, pdf_path, options=options)
        except Exception as e:
            self.logger.error(f"Error generating PDF for {title}: {e}")


def clean_post_html(soup):
    for script in soup.find_all("script"):
        script.decompose()
    for script in soup.find_all("noscript"):
        script.decompose()
    for element in soup.find_all(class_="sharedaddy"):
        element.decompose()

    image_container = soup.find(id="post-feat-image-container")
    if image_container:
        image_container.decompose()


def get_loadmore_endpoints_and_params(response):
    script_content = response.xpath(
        '//script[contains(., "loadmore_params")]/text()'
    ).get()

    if script_content:
        params_json = re.search(r"var loadmore_params = (.*?);", script_content)
        if params_json:
            params_string = params_json.group(1)
            params = json.loads(params_string)
            return params["restfulURL"], params["posts"]


def get_load_more_posts_url(url, params):
    query_string = urlencode(params, doseq=True)
    return f"{url}?{query_string}"

