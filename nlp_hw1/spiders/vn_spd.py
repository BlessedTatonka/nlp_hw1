import scrapy
import time
from util.table import Table

class VisualNovelSpider(scrapy.Spider):
    name = 'visualnovels'

    # Sorted by popularity
    start_urls = ['https://vndb.org/v?f=&s=33w']

    # To fetch only 
    current_pages_crawled = 0
    max_pages_crawled = 1000

    def parse(self, response):
        vn_page_links = response.css('.tc_title a::attr(href)').getall()
        for i in range(len(vn_page_links)):
            if not '?' in vn_page_links[i]:
                yield from response.follow_all([vn_page_links[i]], self.parse_vn)
                time.sleep(5)
                self.current_pages_crawled += 1
                
            if self.max_pages_crawled <= self.current_pages_crawled:
                break

        if self.max_pages_crawled <= self.current_pages_crawled:
            return

        # I need only to follow link that contains 'next' in text
        pagination_texts = response.css('li a::text').getall()
        pagination_links = response.css('li a::attr(href)').getall()
        for i in range(len(pagination_texts)):
            if 'next' in pagination_texts[i]:
                yield from response.follow_all([pagination_links[i]], self.parse)

        # yield from response.follow_all(pagination_links, self.parse)

    def parse_vn(self, response):
        def extract_with_css(query):
            return response.css(query).get(default='').strip()

        yield {
            'title': extract_with_css('tr.title td span::text'),
            'description': extract_with_css('td.vndesc p')
        }

        page = response.url.split("/")[-1]
        filename = f'{page}.html'
        folder = 'vn_pages/'
        with open(folder + filename, 'wb') as f:
            f.write(response.body)

        # # Using class Table to fetch tables
        # table = Table(response.xpath('(//table)[1]'))
        # yield from table.as_dicts()
