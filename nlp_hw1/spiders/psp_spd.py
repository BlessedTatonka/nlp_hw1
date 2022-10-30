import scrapy
import time
import re

class PSPGameSpider(scrapy.Spider):
    name = 'pspgames'

    # Sorted by popularity
    start_urls = ['http://pspiso.tv/psp-games/']

    # To fetch only 
    current_pages_crawled = 0
    max_pages_crawled = 100000

    def parse(self, response):
        game_page_links = response.css('div.n_title_v a::attr(href)').getall()
        for i in range(len(game_page_links)):
            yield from response.follow_all([game_page_links[i]], self.parse_vn)
            # time.sleep(1)
            self.current_pages_crawled += 1

        if self.max_pages_crawled <= self.current_pages_crawled:
            return

        pagination_links = response.css('span.pnext a::attr(href)').getall()
        print('pagination', pagination_links)
        yield from response.follow_all(pagination_links, self.parse)

    def parse_vn(self, response):
        def extract_with_css(query):
            raw = response.css(query).getall()
            processed = ''
            for i in range(len(raw)):
                if 'Описание' in re.sub(r'[^а-яА-Я]', '', raw[i]):
                    processed = re.sub(r'[^а-яА-Я \n]', '', raw[i])
                    break
            try:
                processed = processed.split('Описание')[1]
            except:
                pass

            return processed

        yield {
            'title': response.css('div.n_title_v h1::text').get().strip(),
            'description': extract_with_css('div.news_mid p')
        }

        page = response.url.split("/")[-1]
        filename = f'{page}.html'
        folder = 'psp_pages/'
        with open(folder + filename, 'wb') as f:
            f.write(response.body)
