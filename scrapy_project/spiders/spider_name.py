import scrapy
import json
from scrapy.crawler import CrawlerProcess


class SpiderNameSpider(scrapy.Spider):
    name = 'spider_name'
    allowed_domains = ['www.work.ua']
    start_urls = ['www.work.ua/resumes-kharkiv/']
    headers = {'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0"}
    pages_count = int(
        input("\033[31m\033[43mPlease, enter the number of pages you want to parse (integer, >0) --> \033[0m"))
    resume_counter = 0

    # redefine the start function also known as crawler's entry point
    def start_requests(self):

        for page in range(1, self.pages_count + 1):
            url = f'https://www.work.ua/resumes-kharkiv/?page={page}'
            yield scrapy.Request(url, headers=self.headers, callback=self.parse_pages)
            break

    def parse_pages(self, response):
        """here we must collect:
        - name,
        - age,
        - position
        and transfer url for another part to process"""

        for card in response.css("#pjax-resume-list div.card.resume-link"):

            # name
            name = card.css('div > b::text').get().strip()

            # age
            try:
                if card.css('div span:nth-child(4)::text').get()[:2].strip().isdigit():
                    age = int(card.css('div span:nth-child(4)::text').get()[:2])
                else:
                    if card.css('div span:nth-child(3)::text').get()[:2].strip().isdigit():
                        age = int(card.css('div span:nth-child(3)::text').get()[:2])
                    else:
                        # in case when we do not have information (like "business card")
                        age = "not defined"
            except:
                age = "not defined"

            # position
            position = card.css('h2 > a::text').get()

            # url
            url_for_inner_information = f'{SpiderNameSpider.allowed_domains[0]}{card.css("h2 > a::attr(href)").get()}'

            # we aim to control the numbers of the resumes we have parsed
            SpiderNameSpider.resume_counter += 1
            numbers_of_the_resume = SpiderNameSpider.resume_counter

            output = {
                'sequence number': numbers_of_the_resume,
                'name': name,
                'age': age,
                'position': position,
                'link': url_for_inner_information,
            }

            # just for checking our data
            print(json.dumps(output, indent=4, sort_keys=False, ensure_ascii=False))
            # yield output

            yield scrapy.Request(url_for_inner_information,
                                 self.parse_card_details,
                                meta={
                                    'sequence number': numbers_of_the_resume,
                                    'name': name,
                                    'age': age,
                                    'position': position,
                                    'link': url_for_inner_information,})


    def parse_card_details(self, response):
        '''
        This method parse detailed information
        :param response:
        :return:
        output : dictionary
        '''
        final = response.meta['name']

        print('final')


# main driver
if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(SpiderNameSpider)
    process.start()