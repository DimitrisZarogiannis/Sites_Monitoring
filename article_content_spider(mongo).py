import scrapy
import requests
import re
from pymongo import MongoClient
from scrapy.crawler import CrawlerProcess


# Spider class for https://noisey.vice.com/ domain monitoring

class ArticleSpider1(scrapy.Spider):
    name = "article"
    allowed_domains = ['noisey.vice.com']
    start_urls = ['https://noisey.vice.com/en_us/topic/noisey-news?page=1']
    post_urls = []
    page_id = 2
    core_link = 'https://noisey.vice.com/en_us/topic/noisey-news?page='
    client = MongoClient('mongodb://localhost:27017')
    db = client['Articles_DB']
    articles = db.articles
    url_repository = db.urls
    repo_existence_check = 0
    new_content_flag = 1
    max_pages = 400

    def parse(self, response):
        urls_repo_cursor = self.url_repository.find()
        for item in urls_repo_cursor:
            if '_id' and 'post_urls_repo1' in item:
                self.repo_existence_check += 1
                local_item = item

        if self.repo_existence_check == 0:
            for article_url in response.css('.grid__wrapper a::attr("href")').extract():
                self.post_urls.append(article_url)
                yield response.follow(article_url, callback=self.parse_article)

            next_page = requests.get(self.core_link + str(self.page_id))
            if next_page.status_code == 200 and self.page_id <= self.max_pages:
                next_page_link = (self.core_link + str(self.page_id))
                self.page_id += 1
                yield response.follow(next_page_link, callback=self.parse)
            else:
                included_posts = {'post_urls_repo1': self.post_urls}
                self.url_repository.insert_one(included_posts)

        else:
            self.post_urls = local_item['post_urls_repo1']
            if self.new_content_flag == 1:
                for article_url in response.css('.grid__wrapper a::attr("href")').extract():
                    if not (article_url in self.post_urls):
                        self.post_urls.append(article_url)
                        yield response.follow(article_url, callback=self.parse_article)
                    else:
                        self.new_content_flag = 0

                url_repo_id = local_item['_id']
                self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo1': self.post_urls}})
                next_page = requests.get(self.core_link + str(self.page_id))

                if next_page.status_code == 200 and self.page_id <= self.max_pages:
                    next_page_link = (self.core_link + str(self.page_id))
                    self.page_id += 1
                    yield response.follow(next_page_link, callback=self.parse)

                else:
                    url_repo_id = local_item['_id']
                    self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo1': self.post_urls}})

    def parse_article(self, response):
        title = response.css('h1::text').extract()
        date = response.css('.article__contributions__publishdate::text').extract()
        date_after_format = str(date[0])
        date_after_format = re.match(r'(.+?)(?=,\s)', date_after_format)
        date_after_format = date_after_format.group(0)
        article = response.css('p::text, p a::text, p b::text , i::text , strong::text').extract()
        post_link = str(response)
        post_link = post_link.strip('<200 ')
        post_link = post_link.strip('>')
        post = {'title': ''.join(title),
                'date': ''.join(date_after_format),
                'article': ''.join(article),
                'post-link': post_link}
        self.articles.insert_one(post)


# Spider class for http://thump.vice.com/ domain monitoring


class ArticleSpider2(scrapy.Spider):
    name = "article"
    allowed_domains = ['www.vice.com']
    start_urls = ['https://www.vice.com/en_us/topic/thump?page=1']
    post_urls = []
    page_id = 2
    core_link = 'https://www.vice.com/en_us/topic/thump?page='
    client = MongoClient('mongodb://localhost:27017')
    db = client['Articles_DB']
    articles = db.articles2
    url_repository = db.urls
    repo_existence_check = 0
    new_content_flag = 1
    max_pages = 400

    def parse(self, response):
        urls_repo_cursor = self.url_repository.find()
        for item in urls_repo_cursor:
            if '_id' and 'post_urls_repo2' in item:
                self.repo_existence_check += 1
                local_item = item

        if self.repo_existence_check > 0:
            self.post_urls = local_item['post_urls_repo2']
            if self.new_content_flag == 1:
                for article_url in response.css('.grid__wrapper a::attr("href")').extract():
                    if not (article_url in self.post_urls):
                        self.post_urls.append(article_url)
                        yield response.follow(article_url, callback=self.parse_article)
                    else:
                        self.new_content_flag = 0

                url_repo_id = local_item['_id']
                self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo2': self.post_urls}})

                next_page = requests.get(self.core_link + str(self.page_id))
                if next_page.status_code == 200 and self.page_id <= self.max_pages:
                    next_page_link = (self.core_link + str(self.page_id))
                    self.page_id += 1
                    yield response.follow(next_page_link, callback=self.parse)
                else:
                    url_repo_id = local_item['_id']
                    self.url_repository.update_one({'_id': url_repo_id},{'$set': {'post_urls_repo2': self.post_urls}})
        else:
            for article_url in response.css('.grid__wrapper a::attr("href")').extract():
                self.post_urls.append(article_url)
                yield response.follow(article_url, callback=self.parse_article)

            next_page = requests.get(self.core_link + str(self.page_id))
            if next_page.status_code == 200 and self.page_id <= self.max_pages:
                next_page_link = (self.core_link + str(self.page_id))
                self.page_id += 1
                yield response.follow(next_page_link, callback=self.parse)
            else:
                included_posts = {'post_urls_repo2': self.post_urls}
                self.url_repository.insert_one(included_posts)

    def parse_article(self, response):
        title = response.css('h1::text').extract()
        date = response.css('.article__contributions__publishdate::text').extract()
        date_after_format = str(date[0])
        date_after_format = re.match(r'(.+?)(?=,\s)', date_after_format)
        date_after_format = date_after_format.group(0)
        article = response.css('p::text , p a::text, p b::text , i::text , strong::text').extract()
        post_link = str(response)
        post_link = post_link.strip('<200 ')
        post_link = post_link.strip('>')
        post = {'title': ''.join(title),
                'date': ''.join(date_after_format),
                'article': ''.join(article),
                'post-link': post_link}
        self.articles.insert_one(post)

# Spider Class for https://pitchfork.com domain monitoring


class ArticleSpider4(scrapy.Spider):
    name = "article"
    allowed_domains = ['pitchfork.com']
    start_urls = ['https://pitchfork.com/latest/?page=1']
    post_urls = []
    page_id = 2
    new_content_flag = 1
    core_link = 'https://pitchfork.com/latest/?page='
    client = MongoClient('mongodb://localhost:27017')
    db = client['Articles_DB']
    articles = db.articles4
    url_repository = db.urls
    repo_existence_check = 0
    problematic_urls = ['https://pitchfork.com/news/', 'https://pitchfork.com/thepitch/', '/news/', '/thepitch/'
                        , '/reviews/tracks/']
    max_pages = 400

    def parse(self, response):
        urls_repo_cursor = self.url_repository.find()
        for item in urls_repo_cursor:
            if '_id' and 'post_urls_repo4' in item:
                self.repo_existence_check += 1
                local_item = item

        if self.repo_existence_check == 0:
            for article_url in response.css('.article-details a::attr("href")').extract():
                if not(article_url in self.problematic_urls):
                    self.post_urls.append(article_url)
                    yield response.follow(article_url, callback=self.parse_article)

            next_page = requests.get(self.core_link + str(self.page_id))
            if next_page.status_code == 200 and self.page_id <= self.max_pages:
                next_page_link = (self.core_link + str(self.page_id))
                self.page_id += 1
                yield response.follow(next_page_link, callback=self.parse)
            else:
                included_posts = {'post_urls_repo4': self.post_urls}
                self.url_repository.insert_one(included_posts)

        else:
            self.post_urls = local_item['post_urls_repo4']

            if self.new_content_flag == 1:
                for article_url in response.css('.article-details a::attr("href")').extract():
                    if not (article_url in self.post_urls):
                        if not (article_url in self.problematic_urls):
                            self.post_urls.append(article_url)
                            yield response.follow(article_url, callback=self.parse_article)
                        else:
                            self.new_content_flag = 0

                url_repo_id = local_item['_id']
                self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo4': self.post_urls}})

                next_page = requests.get(self.core_link + str(self.page_id))
                if next_page.status_code == 200 and self.page_id <= self.max_pages:
                    next_page_link = (self.core_link + str(self.page_id))
                    self.page_id += 1
                    yield response.follow(next_page_link, callback=self.parse)
                else:
                    url_repo_id = local_item['_id']
                    self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo4': self.post_urls}})

    def parse_article(self, response):
        title = response.css('h1::text ,h1 em::text').extract()
        date = response.css('time::text,time::attr("title")').extract()
        date_after_format = str(date[0])
        date_test = re.search(r'(?<=[,])(.+?)(?=\s[0-9]+[:])', date_after_format)
        if date_test:
            date_test = date_test.group(0)
            date_after_format = date_test[1:].split()
            date_after_format = str(date_after_format[1]+' '+date_after_format[0]+','+' '+date_after_format[2])
        article = response.css('p::text, p a::text, p b::text , i::text , strong::text').extract()
        post_link = str(response)
        post_link = post_link.strip('<200 ')
        post_link = post_link.strip('>')
        if post_link not in self.problematic_urls:
            post = {'title': ''.join(title),
                    'date': ''.join(date_after_format),
                    'article': ''.join(article),
                    'post-link': post_link}
            self.articles.insert_one(post)

# Spider Class for https://djmag.com domain monitoring


class ArticleSpider5(scrapy.Spider):
    name = "article"
    allowed_domains = ['djmag.com']
    start_urls = ['https://djmag.com/news']
    post_urls = []
    page_id = 1
    new_content_flag = 1
    core_link = 'https://djmag.com/news?page='
    client = MongoClient('mongodb://localhost:27017')
    db = client['Articles_DB']
    articles = db.articles5
    url_repository = db.urls
    repo_existence_check = 0
    max_pages = 400

    def parse(self, response):
        urls_repo_cursor = self.url_repository.find()
        for item in urls_repo_cursor:
            if '_id' and 'post_urls_repo5' in item:
                self.repo_existence_check += 1
                local_item = item

        if self.repo_existence_check == 0:
            for article_url in response.css('.typography--HEADING-TERTIARY a::attr("href")').extract():
                if not (article_url in self.post_urls):
                    self.post_urls.append(article_url)
                    yield response.follow(article_url, callback=self.parse_article)

            next_page = requests.get(self.core_link + str(self.page_id))
            if next_page.status_code == 200 and self.page_id <= self.max_pages:
                next_page_link = (self.core_link + str(self.page_id))
                self.page_id += 1
                yield response.follow(next_page_link, callback=self.parse)
            else:
                included_posts = {'post_urls_repo5': self.post_urls}
                self.url_repository.insert_one(included_posts)

        else:
            self.post_urls = local_item['post_urls_repo5']

            if self.new_content_flag == 1:
                for article_url in response.css('.typography--HEADING-TERTIARY a::attr("href")').extract():
                    if not (article_url in self.post_urls):
                        self.post_urls.append(article_url)
                        yield response.follow(article_url, callback=self.parse_article)
                    else:
                        self.new_content_flag = 0

                url_repo_id = local_item['_id']
                self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo5': self.post_urls}})

                next_page = requests.get(self.core_link + str(self.page_id))
                if next_page.status_code == 200 and self.page_id <= self.max_pages:
                    next_page_link = (self.core_link + str(self.page_id))
                    self.page_id += 1
                    yield response.follow(next_page_link, callback=self.parse)
                else:
                    url_repo_id = local_item['_id']
                    self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo5': self.post_urls}})

    def parse_article(self, response):
        title = response.css('.typography--HEADING-PRIMARY::text').extract()
        date = response.xpath('//*[@id="top"]/main/div/div[3]/div/div/article/div[1]/header/div[5]/text()').extract()
        regex1 = r'^[\n]\s+[A-z]+,\s'
        regex2 = r'\s-\s\d+:\d+'
        date_after_format = date[0]
        date_after_format = re.sub(regex1, '', date_after_format)
        date_after_format = re.sub(regex2, '', date_after_format)
        article = response.css('p::text, p a::text, p b::text ,p i::text ,p strong::text').extract()
        post_link = str(response)
        post_link = post_link.strip('<200 ')
        post_link = post_link.strip('>')
        post = {'title': ''.join(title),
                'date': ''.join(date_after_format),
                'article': ''.join(article),
                'post-link': post_link}
        self.articles.insert_one(post)

# Spider Class for https://www.youredm.com domain monitoring


class ArticleSpider6(scrapy.Spider):
    name = "article"
    allowed_domains = ['www.youredm.com']
    start_urls = ['https://www.youredm.com/news/']
    post_urls = []
    page_id = 2
    new_content_flag = 1
    core_link = 'https://www.youredm.com/news/page/'
    client = MongoClient('mongodb://localhost:27017')
    db = client['Articles_DB']
    articles = db.articles6
    url_repository = db.urls
    repo_existence_check = 0
    max_pages = 400

    def parse(self, response):
        urls_repo_cursor = self.url_repository.find()
        for item in urls_repo_cursor:
            if '_id' and 'post_urls_repo6' in item:
                self.repo_existence_check += 1
                local_item = item

        if self.repo_existence_check == 0:
            for article_url in response.css('.cb-post-title a::attr("href")').extract():
                if not (article_url in self.post_urls):
                    self.post_urls.append(article_url)
                    yield response.follow(article_url, callback=self.parse_article)

            next_page = requests.get(self.core_link + str(self.page_id))
            if next_page.status_code == 200 and self.page_id <= self.max_pages:
                next_page_link = (self.core_link + str(self.page_id))
                self.page_id += 1
                yield response.follow(next_page_link, callback=self.parse)
            else:
                included_posts = {'post_urls_repo6': self.post_urls}
                self.url_repository.insert_one(included_posts)

        else:
            self.post_urls = local_item['post_urls_repo6']

            if self.new_content_flag == 1:
                for article_url in response.css('.cb-post-title a::attr("href")').extract():
                    if not (article_url in self.post_urls):
                        self.post_urls.append(article_url)
                        yield response.follow(article_url, callback=self.parse_article)
                    else:
                        self.new_content_flag = 0

                url_repo_id = local_item['_id']
                self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo6': self.post_urls}})

                next_page = requests.get(self.core_link + str(self.page_id))
                if next_page.status_code == 200 and self.page_id <= self.max_pages:
                    next_page_link = (self.core_link + str(self.page_id))
                    self.page_id += 1
                    yield response.follow(next_page_link, callback=self.parse)
                else:
                    url_repo_id = local_item['_id']
                    self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo6': self.post_urls}})

    def parse_article(self, response):
        title = response.css('h1::text').extract()
        date = response.css('.updated::text').extract()
        date_after_format = date[0]
        article = response.css('p::text, p a::text, p b::text ,p i::text ,p strong::text').extract()
        post_link = str(response)
        post_link = post_link.strip('<200 ')
        post_link = post_link.strip('>')
        post = {'title': ''.join(title),
                'date': ''.join(date_after_format),
                'article': ''.join(article),
                'post-link': post_link}
        self.articles.insert_one(post)

# Spider class for https://www.tinymixtapes.com domain monitoring


class ArticleSpider8(scrapy.Spider):
    name = "article"
    allowed_domains = ['www.tinymixtapes.com']
    start_urls = ['https://www.tinymixtapes.com/news']
    post_urls = []
    page_id = 1
    new_content_flag = 1
    core_link = 'https://www.tinymixtapes.com/news?page='
    client = MongoClient('mongodb://localhost:27017')
    db = client['Articles_DB']
    articles = db.articles8
    url_repository = db.urls
    repo_existence_check = 0
    links_xpath = '/html/body/div[2]/div[2]/section[1]/section[2]/div[1]/div/article/div/a[@class="tile__link"]/@href'
    max_pages = 400

    def parse(self, response):
        urls_repo_cursor = self.url_repository.find()
        for item in urls_repo_cursor:
            if '_id' and 'post_urls_repo8' in item:
                self.repo_existence_check += 1
                local_item = item

        if self.repo_existence_check == 0:
            for article_url in response.xpath(self.links_xpath).extract():
                if not (article_url in self.post_urls):
                    self.post_urls.append(article_url)
                    yield response.follow(article_url, callback=self.parse_article)

            next_page = requests.get(self.core_link + str(self.page_id))
            if next_page.status_code == 200 and self.page_id <= self.max_pages:
                next_page_link = (self.core_link + str(self.page_id))
                self.page_id += 1
                yield response.follow(next_page_link, callback=self.parse)
            else:
                included_posts = {'post_urls_repo8': self.post_urls}
                self.url_repository.insert(included_posts)

        else:
            self.post_urls = local_item['post_urls_repo8']

            if self.new_content_flag == 1:
                for article_url in response.xpath(self.links_xpath).extract():
                    if not (article_url in self.post_urls):
                        self.post_urls.append(article_url)
                        yield response.follow(article_url, callback=self.parse_article)
                    else:
                        self.new_content_flag = 0

                url_repo_id = local_item['_id']
                self.url_repository.update({'_id': url_repo_id}, {'$set': {'post_urls_repo8': self.post_urls}})

                next_page = requests.get(self.core_link + str(self.page_id))
                if next_page.status_code == 200 and self.page_id <= self.max_pages:
                    next_page_link = (self.core_link + str(self.page_id))
                    self.page_id += 1
                    self.links_xpath = '/ html / body / div[2] / div[2] / section[1] / section / div[1] / div[2] / article / div / a[@class="tile__link"]/@href'
                    yield response.follow(next_page_link, callback=self.parse)
                else:
                    url_repo_id = local_item['_id']
                    self.url_repository.update({'_id': url_repo_id}, {'$set': {'post_urls_repo8': self.post_urls}})

    def parse_article(self, response):
        title = response.xpath('//*/header/h1/span[2]/text()').extract()
        date = response.xpath('//*/header/p[2]/time/text()').extract()
        article = response.xpath('//*/div/div/p/text()').extract()
        post_link = str(response)
        post_link = post_link.strip('<200 ')
        post_link = post_link.strip('>')
        post = {'title': ''.join(title),
                'date': ''.join(date),
                'article': ''.join(article),
                'post-link': post_link}
        self.articles.insert_one(post)

# Spider class for https://www.edmsauce.com/ domain monitoring


class ArticleSpider9(scrapy.Spider):
    name = "article"
    allowed_domains = ['www.edmsauce.com']
    start_urls = ['https://www.edmsauce.com/news/']
    post_urls = []
    page_id = 2
    new_content_flag = 1
    core_link = 'https://www.edmsauce.com/news/page/'
    client = MongoClient('mongodb://localhost:27017')
    db = client['Articles_DB']
    articles = db.articles9
    url_repository = db.urls
    repo_existence_check = 0
    link_xpath = '//*[@id="td-outer-wrap"]/div/div/div/div[1]/div/div/div/h3/a/@href'
    max_pages = 400

    def parse(self, response):
        urls_repo_cursor = self.url_repository.find()
        for item in urls_repo_cursor:
            if '_id' and 'post_urls_repo9' in item:
                self.repo_existence_check += 1
                local_item = item

        if self.repo_existence_check == 0:
            for article_url in response.xpath(self.link_xpath).extract():
                if not (article_url in self.post_urls):
                    self.post_urls.append(article_url)
                    yield response.follow(article_url, callback=self.parse_article)

            next_page = requests.get(self.core_link + str(self.page_id))
            if next_page.status_code == 200 and self.page_id <= self.max_pages:
                next_page_link = (self.core_link + str(self.page_id))
                self.page_id += 1
                yield response.follow(next_page_link, callback=self.parse)
            else:
                included_posts = {'post_urls_repo9': self.post_urls}
                self.url_repository.insert_one(included_posts)

        else:
            self.post_urls = local_item['post_urls_repo9']

            if self.new_content_flag == 1:
                for article_url in response.xpath(self.link_xpath).extract():
                    if not (article_url in self.post_urls):
                        self.post_urls.append(article_url)
                        yield response.follow(article_url, callback=self.parse_article)
                    else:
                        self.new_content_flag = 0

                url_repo_id = local_item['_id']
                self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo9': self.post_urls}})

                next_page = requests.get(self.core_link + str(self.page_id))
                if next_page.status_code == 200 and self.page_id <= self.max_pages:
                    next_page_link = (self.core_link + str(self.page_id))
                    self.page_id += 1
                    yield response.follow(next_page_link, callback=self.parse)
                else:
                    url_repo_id = local_item['_id']
                    self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo9': self.post_urls}})

    def parse_article(self, response):
        title = response.xpath('//*/div[1]/div[2]/header/h1/text()').extract()
        date = response.xpath('//*/div[1]/div[2]/header/div/span/time/text()').extract()
        article = response.css('.td-post-content p::text,.td-post-content p a::attr("title"),.td-post-content p b::text,'
                               '.td-post-content p i::text,.td-post-content p strong::text').extract()
        post_link = str(response)
        post_link = post_link.strip('<200 ')
        post_link = post_link.strip('>')
        post = {'title': ''.join(title),
                'date': ''.join(date),
                'article': ''.join(article),
                'post-link': post_link}
        self.articles.insert_one(post)

# Spider class for http://www.thissongslaps.com domain monitoring


class ArticleSpider10(scrapy.Spider):
    name = "article"
    allowed_domains = ['www.thissongslaps.com']
    start_urls = ['http://www.thissongslaps.com/category/news/']
    post_urls = []
    page_id = 2
    new_content_flag = 1
    core_link = 'http://www.thissongslaps.com/category/news/page/'
    client = MongoClient('mongodb://localhost:27017')
    db = client['Articles_DB']
    articles = db.articles10
    url_repository = db.urls
    repo_existence_check = 0
    link_xpath = '// *[ @ id = "home-widget-wrap"] / div / ul / li/ div[2] / a/@href'
    max_pages = 120

    def parse(self, response):
        urls_repo_cursor = self.url_repository.find()
        for item in urls_repo_cursor:
            if '_id' and 'post_urls_repo10' in item:
                self.repo_existence_check += 1
                local_item = item

        if self.repo_existence_check == 0:
            for article_url in response.xpath(self.link_xpath).extract():
                if not (article_url in self.post_urls):
                    self.post_urls.append(article_url)
                    yield response.follow(article_url, callback=self.parse_article)

            next_page_link = self.core_link + str(self.page_id)

            if self.page_id <= self.max_pages:
                self.page_id += 1
                yield response.follow(next_page_link, callback=self.parse)

            else:
                included_posts = {'post_urls_repo10': self.post_urls}
                self.url_repository.insert_one(included_posts)

        else:
            self.post_urls = local_item['post_urls_repo10']

            if self.new_content_flag == 1:
                for article_url in response.xpath(self.link_xpath).extract():
                    if not (article_url in self.post_urls):
                        self.post_urls.append(article_url)
                        yield response.follow(article_url, callback=self.parse_article)
                    else:
                        self.new_content_flag = 0

                url_repo_id = local_item['_id']
                self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo10': self.post_urls}})

                next_page_link = self.core_link + str(self.page_id)

                if self.page_id <= self.max_pages:
                    self.page_id += 1
                    yield response.follow(next_page_link, callback=self.parse)

    def parse_article(self, response):
        title = response.xpath('//*[@id="post-area"]/h1//text()').extract()
        date = response.xpath('//*[ @ id = "left-content"]/div[2]/span/time/text()').extract()
        article = response.xpath('//*[ @ id = "content-area"]/p//text()').extract()
        post_link = str(response)
        post_link = post_link.strip('<200 ')
        post_link = post_link.strip('>')
        post = {'title': ''.join(title),
                'date': ''.join(date),
                'article': ''.join(article),
                'post-link': post_link}
        self.articles.insert_one(post)

# Spider class for https://www.edmtunes.com domain monitoring


class ArticleSpider11(scrapy.Spider):
    name = "article"
    allowed_domains = ['www.edmtunes.com']
    start_urls = ['https://www.edmtunes.com/news/']
    post_urls = []
    page_id = 2
    new_content_flag = 1
    core_link = 'https://www.edmtunes.com/news/page/'
    client = MongoClient('mongodb://localhost:27017')
    db = client['Articles_DB']
    articles = db.articles11
    url_repository = db.urls
    repo_existence_check = 0
    link_xpath = '//*[@id="td-outer-wrap"]/div[4]/div/div/div[1]/div/div/div/div/h3/a/@href'
    max_pages = 400

    def parse(self, response):
        urls_repo_cursor = self.url_repository.find()
        for item in urls_repo_cursor:
            if '_id' and 'post_urls_repo11' in item:
                self.repo_existence_check += 1
                local_item = item

        if self.repo_existence_check == 0:
            for article_url in response.xpath(self.link_xpath).extract():
                if not (article_url in self.post_urls):
                    self.post_urls.append(article_url)
                    yield response.follow(article_url, callback=self.parse_article)

            next_page = requests.get(self.core_link + str(self.page_id))
            if next_page.status_code == 200 and self.page_id <= self.max_pages:
                next_page_link = (self.core_link + str(self.page_id))
                self.page_id += 1
                yield response.follow(next_page_link, callback=self.parse)
            else:
                included_posts = {'post_urls_repo11': self.post_urls}
                self.url_repository.insert_one(included_posts)

        else:
            self.post_urls = local_item['post_urls_repo11']

            if self.new_content_flag == 1:
                for article_url in response.xpath(self.link_xpath).extract():
                    if not (article_url in self.post_urls):
                        self.post_urls.append(article_url)
                        yield response.follow(article_url, callback=self.parse_article)
                    else:
                        self.new_content_flag = 0

                url_repo_id = local_item['_id']
                self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo11': self.post_urls}})

                next_page = requests.get(self.core_link + str(self.page_id))
                if next_page.status_code == 200 and self.page_id <= self.max_pages:
                    next_page_link = (self.core_link + str(self.page_id))
                    self.page_id += 1
                    yield response.follow(next_page_link, callback=self.parse)
                else:
                    url_repo_id = local_item['_id']
                    self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo11': self.post_urls}})

    def parse_article(self, response):
        title = response.css('.entry-title::text').extract()
        date = response.css('time::text').extract_first()
        article = response.css(".td-post-content p::text,p a::text, p b::text,p i::text,p strong::text").extract()
        post_link = str(response)
        post_link = post_link.strip('<200 ')
        post_link = post_link.strip('>')
        post = {'title': ''.join(title),
                'date': ''.join(date),
                'article': ''.join(article),
                'post-link': post_link}
        self.articles.insert_one(post)

# Spider class for https://earmilk.com/ domain monitoring


class ArticleSpider12(scrapy.Spider):
    name = "article"
    allowed_domains = ['earmilk.com']
    start_urls = ['https://earmilk.com/news/']
    post_urls = []
    page_id = 2
    new_content_flag = 1
    core_link = 'https://earmilk.com/news/page/'
    client = MongoClient('mongodb://localhost:27017')
    db = client['Articles_DB']
    articles = db.articles12
    url_repository = db.urls
    repo_existence_check = 0
    link_xpath = '//*/div[2]/h2/a/@href'
    max_pages = 120

    def parse(self, response):
        urls_repo_cursor = self.url_repository.find()
        for item in urls_repo_cursor:
            if '_id' and 'post_urls_repo12' in item:
                self.repo_existence_check += 1
                local_item = item

        if self.repo_existence_check == 0:
            for article_url in response.xpath(self.link_xpath).extract():
                if not (article_url in self.post_urls):
                    self.post_urls.append(article_url)
                    yield response.follow(article_url, callback=self.parse_article)

            next_page = requests.get(self.core_link + str(self.page_id))
            if next_page.status_code == 200 and self.page_id <= self.max_pages:
                next_page_link = (self.core_link + str(self.page_id))
                self.page_id += 1
                yield response.follow(next_page_link, callback=self.parse)
            else:
                included_posts = {'post_urls_repo12': self.post_urls}
                self.url_repository.insert_one(included_posts)

        else:
            self.post_urls = local_item['post_urls_repo12']

            if self.new_content_flag == 1:
                for article_url in response.xpath(self.link_xpath).extract():
                    if not (article_url in self.post_urls):
                        self.post_urls.append(article_url)
                        yield response.follow(article_url, callback=self.parse_article)
                    else:
                        self.new_content_flag = 0

                url_repo_id = local_item['_id']
                self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo12': self.post_urls}})

                next_page = requests.get(self.core_link + str(self.page_id))
                if next_page.status_code == 200 and self.page_id <= self.max_pages:
                    next_page_link = (self.core_link + str(self.page_id))
                    self.page_id += 1
                    yield response.follow(next_page_link, callback=self.parse)
                else:
                    url_repo_id = local_item['_id']
                    self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo12': self.post_urls}})

    def parse_article(self, response):
        title = response.xpath('//*[ @ id = "ajax-content"]/div[2]/div[1]/div[1]/h1/text()').extract()
        date = response.xpath('//*[@id="ajax-content"]/div[2]/div[1]/div[1]/div/span[1]/text()').extract()
        article = response.xpath('//*/div[2]/ div[1]/p//text()').extract()
        post_link = str(response)
        post_link = post_link.strip('<200 ')
        post_link = post_link.strip('>')
        post = {'title': ''.join(title),
                'date': ''.join(date),
                'article': ''.join(article),
                'post-link': post_link}
        self.articles.insert_one(post)

# Spider class for https://wundergroundmusic.com domain monitoring


class ArticleSpider13(scrapy.Spider):
    name = "article"
    allowed_domains = ['wundergroundmusic.com']
    start_urls = ['https://wundergroundmusic.com/category/wunderground-2-0/music-news/']
    post_urls = []
    page_id = 2
    new_content_flag = 1
    core_link = 'https://wundergroundmusic.com/category/wunderground-2-0/music-news/page/'
    client = MongoClient('mongodb://localhost:27017')
    db = client['Articles_DB']
    articles = db.articles13
    url_repository = db.urls
    repo_existence_check = 0
    link_xpath = '//*/div[2]/header/h2/a/@href'
    max_pages = 400

    def parse(self, response):
        urls_repo_cursor = self.url_repository.find()
        for item in urls_repo_cursor:
            if '_id' and 'post_urls_repo13' in item:
                self.repo_existence_check += 1
                local_item = item

        if self.repo_existence_check == 0:
            for article_url in response.xpath(self.link_xpath).extract():
                if not (article_url in self.post_urls):
                    self.post_urls.append(article_url)
                    yield response.follow(article_url, callback=self.parse_article)

            next_page = requests.get(self.core_link + str(self.page_id))

            if next_page.status_code == 200 and self.page_id <= self.max_pages:
                next_page_link = (self.core_link + str(self.page_id))
                self.page_id += 1
                yield response.follow(next_page_link, callback=self.parse)
            else:
                included_posts = {'post_urls_repo13': self.post_urls}
                self.url_repository.insert_one(included_posts)

        else:
            self.post_urls = local_item['post_urls_repo13']

            if self.new_content_flag == 1:
                for article_url in response.xpath(self.link_xpath).extract():
                    if not (article_url in self.post_urls):
                        self.post_urls.append(article_url)
                        yield response.follow(article_url, callback=self.parse_article)
                    else:
                        self.new_content_flag = 0

                url_repo_id = local_item['_id']
                self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo13': self.post_urls}})

                next_page = requests.get(self.core_link + str(self.page_id))

                if next_page.status_code == 200 and self.page_id <= self.max_pages:
                    next_page_link = (self.core_link + str(self.page_id))
                    self.page_id += 1
                    yield response.follow(next_page_link, callback=self.parse)
                else:
                    url_repo_id = local_item['_id']
                    self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo13': self.post_urls}})

    def parse_article(self, response):
        title = response.xpath('//*/header/h1/text()').extract()
        date = ''
        article = response.xpath('//*/div[3]/p//text()').extract()
        post_link = str(response)
        post_link = post_link.strip('<200 ')
        post_link = post_link.strip('>')
        post = {'title': ''.join(title),
                'date': ''.join(date),
                'article': ''.join(article),
                'post-link': post_link}
        self.articles.insert_one(post)

# Spider class for http://noiseprn.com/ domain monitoring


class ArticleSpider14(scrapy.Spider):
    name = "article"
    allowed_domains = ['noiseprn.com']
    start_urls = ['http://noiseprn.com/']
    post_urls = []
    page_id = 2
    new_content_flag = 1
    core_link = 'http://noiseprn.com/page/'
    client = MongoClient('mongodb://localhost:27017')
    db = client['Articles_DB']
    articles = db.articles14
    url_repository = db.urls
    repo_existence_check = 0
    link_xpath = '//*/div/div[1]/div/div/div/div/h2/a/@href'
    max_pages = 400

    def parse(self, response):
        urls_repo_cursor = self.url_repository.find()
        for item in urls_repo_cursor:
            if '_id' and 'post_urls_repo14' in item:
                self.repo_existence_check += 1
                local_item = item

        if self.repo_existence_check == 0:
            for article_url in response.xpath(self.link_xpath).extract():
                if not (article_url in self.post_urls):
                    self.post_urls.append(article_url)
                    yield response.follow(article_url, callback=self.parse_article)

            next_page = requests.get(self.core_link + str(self.page_id))

            if next_page.status_code == 200 and self.page_id <= self.max_pages:
                next_page_link = (self.core_link + str(self.page_id))
                self.page_id += 1
                yield response.follow(next_page_link, callback=self.parse)
            else:
                included_posts = {'post_urls_repo14': self.post_urls}
                self.url_repository.insert_one(included_posts)

        else:
            self.post_urls = local_item['post_urls_repo14']

            if self.new_content_flag == 1:
                for article_url in response.xpath(self.link_xpath).extract():
                    if not (article_url in self.post_urls):
                        self.post_urls.append(article_url)
                        yield response.follow(article_url, callback=self.parse_article)
                    else:
                        self.new_content_flag = 0

                url_repo_id = local_item['_id']
                self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo14': self.post_urls}})
                next_page = requests.get(self.core_link + str(self.page_id))

                if next_page.status_code == 200 and self.page_id <= self.max_pages:
                    next_page_link = (self.core_link + str(self.page_id))
                    self.page_id += 1
                    yield response.follow(next_page_link, callback=self.parse)
                else:
                    url_repo_id = local_item['_id']
                    self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo14': self.post_urls}})

    def parse_article(self, response):
        title = response.xpath('// *[ @ id = "sitecontainer"] / div[1] / div[1] / div / '
                               'div[3] / div / div / div / h1//text()').extract()
        date = response.xpath('// *[ @ id = "sitecontainer"] / div[1] / div[1] / div / div[4] // span//text()').extract()
        article = response.xpath('//*[@id="sitecontainer"]/div[1]/div[2]/div[1]/div//p//text()').extract()
        post_link = str(response)
        post_link = post_link.strip('<200 ')
        post_link = post_link.strip('>')
        post = {'title': ''.join(title),
                'date': ''.join(date),
                'article': ''.join(article),
                'post-link': post_link}
        self.articles.insert_one(post)

# Spider class for https://www.theuntz.com domain monitoring


class ArticleSpider15(scrapy.Spider):
    name = "article"
    allowed_domains = ['www.theuntz.com']
    start_urls = ['https://www.theuntz.com/news/']
    post_urls = []
    page_id = 2
    new_content_flag = 1
    core_link = 'https://www.theuntz.com/news/?page='
    client = MongoClient('mongodb://localhost:27017')
    db = client['Articles_DB']
    articles = db.articles15
    url_repository = db.urls
    repo_existence_check = 0
    link_xpath = '/html/body/div[1]/div[4]/div[1]/div/div[2]/div[2]/div/div[2]/h4/a[2]/@href'
    max_pages = 150

    def parse(self, response):
        urls_repo_cursor = self.url_repository.find()
        for item in urls_repo_cursor:
            if '_id' and 'post_urls_repo15' in item:
                self.repo_existence_check += 1
                local_item = item

        if self.repo_existence_check == 0:
            for article_url in response.xpath(self.link_xpath).extract():
                if not (article_url in self.post_urls):
                    self.post_urls.append(article_url)
                    yield response.follow(article_url, callback=self.parse_article)

            next_page = requests.get(self.core_link + str(self.page_id))

            if next_page.status_code == 200 and self.page_id <= self.max_pages:
                next_page_link = (self.core_link + str(self.page_id))
                self.page_id += 1
                yield response.follow(next_page_link, callback=self.parse)
            else:
                included_posts = {'post_urls_repo15': self.post_urls}
                self.url_repository.insert_one(included_posts)

        else:
            self.post_urls = local_item['post_urls_repo15']

            if self.new_content_flag == 1:
                for article_url in response.xpath(self.link_xpath).extract():
                    if not (article_url in self.post_urls):
                        self.post_urls.append(article_url)
                        yield response.follow(article_url, callback=self.parse_article)
                    else:
                        self.new_content_flag = 0

                url_repo_id = local_item['_id']
                self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo15': self.post_urls}})

                next_page = requests.get(self.core_link + str(self.page_id))

                if next_page.status_code == 200 and self.page_id <= self.max_pages:
                    next_page_link = (self.core_link + str(self.page_id))
                    self.page_id += 1
                    yield response.follow(next_page_link, callback=self.parse)
                else:
                    url_repo_id = local_item['_id']
                    self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo15': self.post_urls}})

    def parse_article(self, response):
        title = response.xpath('/html/body/div[1]/div[4]/div[1]/div/div[1]/div[1]/h2/text()').extract()
        date = response.xpath('/html/body/div[1]/div[4]/div[1]/div/div[1]/div[3]/text()').extract()
        date_after_format = date[0].replace('Published: ', '')
        article = response.xpath('//*[@id = "news_body"]/p//text()').extract()
        post_link = str(response)
        post_link = post_link.strip('<200 ')
        post_link = post_link.strip('>')
        post = {'title': ''.join(title),
                'date': ''.join(date_after_format),
                'article': ''.join(article),
                'post-link': post_link}
        self.articles.insert_one(post)

# Spider class for https://electronicgroove.com domain monitoring


class ArticleSpider16(scrapy.Spider):
    name = "article"
    allowed_domains = ['electronicgroove.com']
    start_urls = ['https://electronicgroove.com/category/news/']
    post_urls = []
    page_id = 2
    new_content_flag = 1
    core_link = 'https://electronicgroove.com/category/news/page/'
    client = MongoClient('mongodb://localhost:27017')
    db = client['Articles_DB']
    articles = db.articles16
    url_repository = db.urls
    repo_existence_check = 0
    link_xpath = '//*/div/header/h2/a/@href'
    max_pages = 400

    def parse(self, response):
        urls_repo_cursor = self.url_repository.find()
        for item in urls_repo_cursor:
            if '_id' and 'post_urls_repo16' in item:
                self.repo_existence_check += 1
                local_item = item

        if self.repo_existence_check == 0:
            for article_url in response.xpath(self.link_xpath).extract():
                if not (article_url in self.post_urls):
                    self.post_urls.append(article_url)
                    yield response.follow(article_url, callback=self.parse_article)

            next_page = requests.get(self.core_link + str(self.page_id))

            if next_page.status_code == 200 and self.page_id <= self.max_pages:
                next_page_link = (self.core_link + str(self.page_id))
                self.page_id += 1
                yield response.follow(next_page_link, callback=self.parse)
            else:
                included_posts = {'post_urls_repo16': self.post_urls}
                self.url_repository.insert_one(included_posts)

        else:
            self.post_urls = local_item['post_urls_repo16']

            if self.new_content_flag == 1:
                for article_url in response.xpath(self.link_xpath).extract():
                    if not (article_url in self.post_urls):
                        self.post_urls.append(article_url)
                        yield response.follow(article_url, callback=self.parse_article)
                    else:
                        self.new_content_flag = 0

                url_repo_id = local_item['_id']
                self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo16': self.post_urls}})
                next_page = requests.get(self.core_link + str(self.page_id))

                if next_page.status_code == 200 and self.page_id <= self.max_pages:
                    next_page_link = (self.core_link + str(self.page_id))
                    self.page_id += 1
                    yield response.follow(next_page_link, callback=self.parse)
                else:
                    url_repo_id = local_item['_id']
                    self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo16': self.post_urls}})

    def parse_article(self, response):
        title = response.xpath('//*[ @ id = "single-blocks"]/header/h1/text()').extract()
        date = response.xpath('//*[@id="single-blocks"]/ul/li[1]/time//text()').extract()
        article = response.xpath('// *[ @ id = "single-blocks"] / div[2] //text()').extract()
        post_link = str(response)
        post_link = post_link.strip('<200 ')
        post_link = post_link.strip('>')
        post = {'title': ''.join(title),
                'date': ''.join(date),
                'article': ''.join(article),
                'post-link': post_link}
        self.articles.insert_one(post)

# Spider class for https://electronicmidwest.com domain monitoring


class ArticleSpider17(scrapy.Spider):
    name = "article"
    allowed_domains = ['electronicmidwest.com']
    start_urls = ['https://electronicmidwest.com/category/news/']
    post_urls = []
    page_id = 2
    new_content_flag = 1
    core_link = 'https://electronicmidwest.com/category/news/page/'
    client = MongoClient('mongodb://localhost:27017')
    db = client['Articles_DB']
    articles = db.articles17
    url_repository = db.urls
    repo_existence_check = 0
    link_xpath = '//*/div/h2/a/@href'
    max_pages = 400

    def parse(self, response):
        urls_repo_cursor = self.url_repository.find()
        for item in urls_repo_cursor:
            if '_id' and 'post_urls_repo17' in item:
                self.repo_existence_check += 1
                local_item = item

        if self.repo_existence_check == 0:
            for article_url in response.xpath(self.link_xpath).extract():
                if not (article_url in self.post_urls):
                    self.post_urls.append(article_url)
                    yield response.follow(article_url, callback=self.parse_article)

            next_page = requests.get(self.core_link + str(self.page_id))

            if next_page.status_code == 200 and self.page_id <= self.max_pages:
                next_page_link = (self.core_link + str(self.page_id))
                self.page_id += 1
                yield response.follow(next_page_link, callback=self.parse)
            else:
                included_posts = {'post_urls_repo17': self.post_urls}
                self.url_repository.insert_one(included_posts)

        else:
            self.post_urls = local_item['post_urls_repo17']

            if self.new_content_flag == 1:
                for article_url in response.xpath(self.link_xpath).extract():
                    if not (article_url in self.post_urls):
                        self.post_urls.append(article_url)
                        yield response.follow(article_url, callback=self.parse_article)
                    else:
                        self.new_content_flag = 0

                url_repo_id = local_item['_id']
                self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo17': self.post_urls}})
                next_page = requests.get(self.core_link + str(self.page_id))

                if next_page.status_code == 200 and self.page_id <= self.max_pages:
                    next_page_link = (self.core_link + str(self.page_id))
                    self.page_id += 1
                    yield response.follow(next_page_link, callback=self.parse)
                else:
                    url_repo_id = local_item['_id']
                    self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo17': self.post_urls}})

    def parse_article(self, response):
        title = response.xpath('//*[@id="page"]/div/div/div/section/div[2]/div[1]/h1//text()').extract()
        date = response.xpath('//*[@id="page"]/div/div/div/section/div[2]/div[1]/p/text()[2]').extract()
        article = response.xpath('//*[@id="page"]/div/div/div/section/div[2]/div[1]'
                                 '/div[3]/div[1]/article/p//text()').extract()
        regex = r'(.+?)(?=\s\d+[:]\d+\s[a-z]+)'
        date_after_format = re.match(regex, str(date[0]))
        date_after_format = str(date_after_format.group(0))
        post_link = str(response)
        post_link = post_link.strip('<200 ')
        post_link = post_link.strip('>')
        post = {'title': ''.join(title),
                'date': ''.join(date_after_format[3:]),
                'article': ''.join(article),
                'post-link': post_link}
        self.articles.insert_one(post)

# Spider class for http://www.feelmybicep.com/ domain monitoring


class ArticleSpider18(scrapy.Spider):
    name = "article"
    allowed_domains = ['www.feelmybicep.com']
    start_urls = ['http://www.feelmybicep.com/']
    post_urls = []
    page_id = 2
    new_content_flag = 1
    core_link = 'http://www.feelmybicep.com/page/'
    client = MongoClient('mongodb://localhost:27017')
    db = client['Articles_DB']
    articles = db.articles18
    url_repository = db.urls
    repo_existence_check = 0
    link_xpath = '//*/h2/a/@href'
    max_pages = 400

    def parse(self, response):
        urls_repo_cursor = self.url_repository.find()
        for item in urls_repo_cursor:
            if '_id' and 'post_urls_repo18' in item:
                self.repo_existence_check += 1
                local_item = item

        if self.repo_existence_check == 0:
            for article_url in response.xpath(self.link_xpath).extract():
                if not (article_url in self.post_urls):
                    self.post_urls.append(article_url)
                    yield response.follow(article_url, callback=self.parse_article)

            if self.page_id <= self.max_pages:
                next_page_link = (self.core_link + str(self.page_id))
                self.page_id += 1
                yield response.follow(next_page_link, callback=self.parse)
            else:
                included_posts = {'post_urls_repo18': self.post_urls}
                self.url_repository.insert_one(included_posts)

        else:
            self.post_urls = local_item['post_urls_repo18']

            if self.new_content_flag == 1:
                for article_url in response.xpath(self.link_xpath).extract():
                    if not (article_url in self.post_urls):
                        self.post_urls.append(article_url)
                        yield response.follow(article_url, callback=self.parse_article)
                    else:
                        self.new_content_flag = 0

                url_repo_id = local_item['_id']
                self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo18': self.post_urls}})

                if self.page_id <= self.max_pages:
                    next_page_link = (self.core_link + str(self.page_id))
                    self.page_id += 1
                    yield response.follow(next_page_link, callback=self.parse)
                else:
                    url_repo_id = local_item['_id']
                    self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo18': self.post_urls}})

    def parse_article(self, response):
        title = response.xpath('//*/h1//text()').extract()
        date = response.xpath('//*/div[1]/a/span/text()').extract()
        article = response.xpath('//*/div[2]/p//text()').extract()
        date_after_format = str(date[1])
        date_after_format = date_after_format.strip('←')
        post_link = str(response)
        post_link = post_link.strip('<200 ')
        post_link = post_link.strip('>')
        post = {'title': ''.join(title),
                'date': ''.join(date_after_format),
                'article': ''.join(article),
                'post-link': post_link}
        self.articles.insert_one(post)

# Spider class for http://houseplanet.dj/ domain monitoring


class ArticleSpider19(scrapy.Spider):
    name = "article"
    allowed_domains = ['houseplanet.dj']
    start_urls = ['http://houseplanet.dj/category/news/']
    post_urls = []
    page_id = 2
    new_content_flag = 1
    core_link = 'http://houseplanet.dj/category/news/page/'
    client = MongoClient('mongodb://localhost:27017')
    db = client['Articles_DB']
    articles = db.articles19
    url_repository = db.urls
    repo_existence_check = 0
    link_xpath = '//*[@id="main-content"]/article/div[2]/header/h3/a/@href'
    max_pages = 400

    def parse(self, response):
        urls_repo_cursor = self.url_repository.find()
        for item in urls_repo_cursor:
            if '_id' and 'post_urls_repo19' in item:
                self.repo_existence_check += 1
                local_item = item

        if self.repo_existence_check == 0:
            for article_url in response.xpath(self.link_xpath).extract():
                if not (article_url in self.post_urls):
                    self.post_urls.append(article_url)
                    yield response.follow(article_url, callback=self.parse_article)

            next_page = requests.get(self.core_link + str(self.page_id))

            if next_page.status_code == 200 and self.page_id <= self.max_pages:
                next_page_link = (self.core_link + str(self.page_id))
                self.page_id += 1
                yield response.follow(next_page_link, callback=self.parse)
            else:
                included_posts = {'post_urls_repo19': self.post_urls}
                self.url_repository.insert_one(included_posts)

        else:
            self.post_urls = local_item['post_urls_repo19']

            if self.new_content_flag == 1:
                for article_url in response.xpath(self.link_xpath).extract():
                    if not (article_url in self.post_urls):
                        self.post_urls.append(article_url)
                        yield response.follow(article_url, callback=self.parse_article)
                    else:
                        self.new_content_flag = 0

                url_repo_id = local_item['_id']
                self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo19': self.post_urls}})
                next_page = requests.get(self.core_link + str(self.page_id))

                if next_page.status_code == 200 and self.page_id <= self.max_pages:
                    next_page_link = (self.core_link + str(self.page_id))
                    self.page_id += 1
                    yield response.follow(next_page_link, callback=self.parse)
                else:
                    url_repo_id = local_item['_id']
                    self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo19': self.post_urls}})

    def parse_article(self, response):
        title = response.xpath('//*/header/h1/text()').extract()
        date = response.xpath('//*/header/p/span[1]/a//text()').extract()
        article = response.xpath('//*/div[1]/p//text()').extract()
        post_link = str(response)
        post_link = post_link.strip('<200 ')
        post_link = post_link.strip('>')
        post = {'title': ''.join(title),
                'date': ''.join(date),
                'article': ''.join(article),
                'post-link': post_link}
        self.articles.insert_one(post)

# Spider class for http://igloomag.com/ domain monitoring


class ArticleSpider20(scrapy.Spider):
    name = "article"
    allowed_domains = ['igloomag.com']
    start_urls = ['http://igloomag.com/']
    post_urls = []
    page_id = 2
    new_content_flag = 1
    core_link = 'https://igloomag.com/page/'
    client = MongoClient('mongodb://localhost:27017')
    db = client['Articles_DB']
    articles = db.articles20
    url_repository = db.urls
    repo_existence_check = 0
    link_xpath = '//*[@id="content"]/div/h2/a/@href'
    max_pages = 400

    def parse(self, response):
        urls_repo_cursor = self.url_repository.find()
        for item in urls_repo_cursor:
            if '_id' and 'post_urls_repo20' in item:
                self.repo_existence_check += 1
                local_item = item

        if self.repo_existence_check == 0:
            for article_url in response.xpath(self.link_xpath).extract():
                if not (article_url in self.post_urls):
                    self.post_urls.append(article_url)
                    yield response.follow(article_url, callback=self.parse_article)

            next_page = requests.get(self.core_link + str(self.page_id))

            if next_page.status_code == 200 and self.page_id <= self.max_pages:
                next_page_link = (self.core_link + str(self.page_id))
                self.page_id += 1
                yield response.follow(next_page_link, callback=self.parse)
            else:
                included_posts = {'post_urls_repo20': self.post_urls}
                self.url_repository.insert_one(included_posts)

        else:
            self.post_urls = local_item['post_urls_repo20']

            if self.new_content_flag == 1:
                for article_url in response.xpath(self.link_xpath).extract():
                    if not (article_url in self.post_urls):
                        self.post_urls.append(article_url)
                        yield response.follow(article_url, callback=self.parse_article)
                    else:
                        self.new_content_flag = 0

                url_repo_id = local_item['_id']
                self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo20': self.post_urls}})
                next_page = requests.get(self.core_link + str(self.page_id))

                if next_page.status_code == 200 and self.page_id <= self.max_pages:
                    next_page_link = (self.core_link + str(self.page_id))
                    self.page_id += 1
                    yield response.follow(next_page_link, callback=self.parse)
                else:
                    url_repo_id = local_item['_id']
                    self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo20': self.post_urls}})

    def parse_article(self, response):
        title = response.xpath('//*[@id="single"]/h1/a//text()').extract()
        date = response.xpath('//*[@id="single"]/ul/li[1]//text()').extract()
        article = response.xpath('//*[@id="single"]/div[1]/p//text()').extract()
        regex = r'\d+/\d+/\d+'
        date_after_format = re.match(regex,str(date[0]))
        post_link = str(response)
        post_link = post_link.strip('<200 ')
        post_link = post_link.strip('>')
        post = {'title': ''.join(title),
                'date': ''.join(date_after_format.group(0)),
                'article': ''.join(article),
                'post-link': post_link}
        self.articles.insert_one(post)

# Spider class for http://www.discobelle.net/ domain monitoring


class ArticleSpider21(scrapy.Spider):
    name = "article"
    allowed_domains = ['www.discobelle.net']
    start_urls = ['http://www.discobelle.net/']
    post_urls = []
    page_id = 2
    new_content_flag = 1
    core_link = 'http://www.discobelle.net/page/'
    client = MongoClient('mongodb://localhost:27017')
    db = client['Articles_DB']
    articles = db.articles21
    url_repository = db.urls
    repo_existence_check = 0
    link_xpath = '//*[@id="c-left"]/article/div[1]/h3/a/@href'
    max_pages = 400

    def parse(self, response):
        urls_repo_cursor = self.url_repository.find()
        for item in urls_repo_cursor:
            if '_id' and 'post_urls_repo21' in item:
                self.repo_existence_check += 1
                local_item = item

        if self.repo_existence_check == 0:
            for article_url in response.xpath(self.link_xpath).extract():
                if not (article_url in self.post_urls):
                    self.post_urls.append(article_url)
                    yield response.follow(article_url, callback=self.parse_article)

            next_page = requests.get(self.core_link + str(self.page_id))

            if next_page.status_code == 200 and self.page_id <= self.max_pages:
                next_page_link = (self.core_link + str(self.page_id))
                self.page_id += 1
                yield response.follow(next_page_link, callback=self.parse)
            else:
                included_posts = {'post_urls_repo21': self.post_urls}
                self.url_repository.insert_one(included_posts)

        else:
            self.post_urls = local_item['post_urls_repo21']

            if self.new_content_flag == 1:
                for article_url in response.xpath(self.link_xpath).extract():
                    if not (article_url in self.post_urls):
                        self.post_urls.append(article_url)
                        yield response.follow(article_url, callback=self.parse_article)
                    else:
                        self.new_content_flag = 0

                url_repo_id = local_item['_id']
                self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo21': self.post_urls}})
                next_page = requests.get(self.core_link + str(self.page_id))

                if next_page.status_code == 200 and self.page_id <= self.max_pages:
                    next_page_link = (self.core_link + str(self.page_id))
                    self.page_id += 1
                    yield response.follow(next_page_link, callback=self.parse)
                else:
                    url_repo_id = local_item['_id']
                    self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo21': self.post_urls}})

    def parse_article(self, response):
        title = response.xpath('//*[@id="c-left"]/article/div[1]/h3//text()').extract()
        date = response.xpath('//*[@id="c-left"]/article/div[1]/div/div[1]//text()').extract()
        article = response.xpath('//*[@id="c-left"]/article/div[3]/p//text()').extract()
        post_link = str(response)
        post_link = post_link.strip('<200 ')
        post_link = post_link.strip('>')
        post = {'title': ''.join(title),
                'date': ''.join(date),
                'article': ''.join(article),
                'post-link': post_link}
        self.articles.insert_one(post)

# Spider class for http://thehouseofdisco.com/ domain monitoring


class ArticleSpider22(scrapy.Spider):
    name = "article"
    allowed_domains = ['thehouseofdisco.com']
    start_urls = ['http://thehouseofdisco.com/', 'http://thehouseofdisco.com/blog/'
                                               , 'http://thehouseofdisco.com/category/mixes/']
    post_urls = []
    new_content_flag = 1
    client = MongoClient('mongodb://localhost:27017')
    db = client['Articles_DB']
    articles = db.articles22
    url_repository = db.urls
    repo_existence_check = 0
    link_xpath_1 = '//*/a/@href'
    link_xpath_2 = '//*[ @ id = "wrapper"]/div/div[1]/div/div/div/div[2]/a/@href'
    link_xpath_3 = '//*/div[2]/div/header/h3/a/@href'
    max_pages = 3
    core_link = 'http://thehouseofdisco.com/category/mixes/page/'
    page_id = 2

    def parse(self, response):
        urls_repo_cursor = self.url_repository.find()
        for item in urls_repo_cursor:
            if '_id' and 'post_urls_repo22' in item:
                self.repo_existence_check += 1
                local_item = item

        if self.repo_existence_check == 0:
            for article_url in response.xpath(self.link_xpath_1 or self.link_xpath_2 or self.link_xpath_3).extract():
                if not (article_url in self.post_urls):
                    self.post_urls.append(article_url)
                    yield response.follow(article_url, callback=self.parse_article)

            next_page = requests.get(self.core_link + str(self.page_id))

            if next_page.status_code == 200 and self.page_id <= self.max_pages:
                next_page_link = (self.core_link + str(self.page_id))
                self.page_id += 1
                yield response.follow(next_page_link, callback=self.parse)
            else:
                print(self.page_id)
                included_posts = {'post_urls_repo22': self.post_urls}
                self.url_repository.insert_one(included_posts)

        else:
            self.post_urls = local_item['post_urls_repo22']

            if self.new_content_flag == 1:
                for article_url in response.xpath(self.link_xpath_1).extract():
                    if not (article_url in self.post_urls):
                        self.post_urls.append(article_url)
                        yield response.follow(article_url, callback=self.parse_article)
                    else:
                        self.new_content_flag = 0

                url_repo_id = local_item['_id']
                self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo22': self.post_urls}})
                next_page = requests.get(self.core_link + str(self.page_id))

                if next_page.status_code == 200 and self.page_id <= self.max_pages:
                    next_page_link = (self.core_link + str(self.page_id))
                    self.page_id += 1
                    yield response.follow(next_page_link, callback=self.parse)
                else:
                    url_repo_id = local_item['_id']
                    self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo22': self.post_urls}})

    def parse_article(self, response):
        title = response.xpath('//*/div/div/header/h1//text()').extract()
        date = response.xpath('//*/div/div/header/aside/text()').extract()
        article = response.xpath('//*/div/div/div/p/text()').extract()
        if date:
            date_after_format = date[0]
            date_after_format = date_after_format.replace(' / ', '')
        else:
            date_after_format = ''
        post_link = str(response)
        post_link = post_link.strip('<200 ')
        post_link = post_link.strip('>')
        if title and date and article and post_link:
            post = {'title': ''.join(title),
                    'date': ''.join(str(date_after_format)),
                    'article': ''.join(article),
                    'post-link': post_link}
            self.articles.insert_one(post)

# Spider class for http://ekm.co/ domain monitoring


class ArticleSpider23(scrapy.Spider):
    name = "article"
    allowed_domains = ['ekm.co']
    start_urls = ['http://ekm.co/']
    post_urls = []
    page_id = 2
    new_content_flag = 1
    core_link = 'http://ekm.co/page/'
    client = MongoClient('mongodb://localhost:27017')
    db = client['Articles_DB']
    articles = db.articles23
    url_repository = db.urls
    repo_existence_check = 0
    link_xpath = '//*[ @ id = "td-outer-wrap"]/div[2]/div/div/div[1]/div/div/div/div/h3/a/@href'
    max_pages = 150

    def parse(self, response):
        urls_repo_cursor = self.url_repository.find()
        for item in urls_repo_cursor:
            if '_id' and 'post_urls_repo23' in item:
                self.repo_existence_check += 1
                local_item = item

        if self.repo_existence_check == 0:
            for article_url in response.xpath(self.link_xpath).extract():
                if not (article_url in self.post_urls):
                    self.post_urls.append(article_url)
                    yield response.follow(article_url, callback=self.parse_article)

            next_page = requests.get(self.core_link + str(self.page_id))

            if next_page.status_code == 200 and self.page_id <= self.max_pages:
                next_page_link = (self.core_link + str(self.page_id))
                self.page_id += 1
                yield response.follow(next_page_link, callback=self.parse)
            else:
                included_posts = {'post_urls_repo23': self.post_urls}
                self.url_repository.insert_one(included_posts)

        else:
            self.post_urls = local_item['post_urls_repo23']

            if self.new_content_flag == 1:
                for article_url in response.xpath(self.link_xpath).extract():
                    if not (article_url in self.post_urls):
                        self.post_urls.append(article_url)
                        yield response.follow(article_url, callback=self.parse_article)
                    else:
                        self.new_content_flag = 0

                url_repo_id = local_item['_id']
                self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo23': self.post_urls}})
                next_page = requests.get(self.core_link + str(self.page_id))

                if next_page.status_code == 200 and self.page_id <= self.max_pages:
                    next_page_link = (self.core_link + str(self.page_id))
                    self.page_id += 1
                    yield response.follow(next_page_link, callback=self.parse)
                else:
                    url_repo_id = local_item['_id']
                    self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo23': self.post_urls}})

    def parse_article(self, response):
        title = response.xpath('//*/div[1]/header/h1//text()').extract()
        date = response.xpath('//*/div[1]/header/div/span/time//text()').extract()
        article = response.xpath('//*/div[2]/p//text()').extract()
        post_link = str(response)
        post_link = post_link.strip('<200 ')
        post_link = post_link.strip('>')
        post = {'title': ''.join(title),
                'date': ''.join(date),
                'article': ''.join(article),
                'post-link': post_link}
        self.articles.insert_one(post)

# Spider class for http://weunderground.net/ domain monitoring


class ArticleSpider24(scrapy.Spider):
    name = "article"
    allowed_domains = ['weunderground.net']
    start_urls = ['http://weunderground.net/']
    post_urls = []
    page_id = 2
    new_content_flag = 1
    core_link = 'http://weunderground.net/page/'
    client = MongoClient('mongodb://localhost:27017')
    db = client['Articles_DB']
    articles = db.articles24
    url_repository = db.urls
    repo_existence_check = 0
    link_xpath = '//*/header/h2/a/@href'
    max_pages = 100

    def parse(self, response):
        urls_repo_cursor = self.url_repository.find()
        for item in urls_repo_cursor:
            if '_id' and 'post_urls_repo24' in item:
                self.repo_existence_check += 1
                local_item = item

        if self.repo_existence_check == 0:
            for article_url in response.xpath(self.link_xpath).extract():
                if not (article_url in self.post_urls):
                    self.post_urls.append(article_url)
                    yield response.follow(article_url, callback=self.parse_article)

            next_page = requests.get(self.core_link + str(self.page_id))

            if next_page.status_code == 200 and self.page_id <= self.max_pages:
                next_page_link = (self.core_link + str(self.page_id))
                self.page_id += 1
                yield response.follow(next_page_link, callback=self.parse)
            else:
                included_posts = {'post_urls_repo24': self.post_urls}
                self.url_repository.insert_one(included_posts)

        else:
            self.post_urls = local_item['post_urls_repo24']

            if self.new_content_flag == 1:
                for article_url in response.xpath(self.link_xpath).extract():
                    if not (article_url in self.post_urls):
                        self.post_urls.append(article_url)
                        yield response.follow(article_url, callback=self.parse_article)
                    else:
                        self.new_content_flag = 0

                url_repo_id = local_item['_id']
                self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo24': self.post_urls}})
                next_page = requests.get(self.core_link + str(self.page_id))

                if next_page.status_code == 200 and self.page_id <= self.max_pages:
                    next_page_link = (self.core_link + str(self.page_id))
                    self.page_id += 1
                    yield response.follow(next_page_link, callback=self.parse)
                else:
                    url_repo_id = local_item['_id']
                    self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo24': self.post_urls}})

    def parse_article(self, response):
        title = response.xpath('//*/header/h1//text()').extract()
        date = response.xpath('//*/div[2]/span[2]/a/time[1]//text()').extract()
        article = response.xpath('//*/div[3]/p//text()').extract()
        post_link = str(response)
        post_link = post_link.strip('<200 ')
        post_link = post_link.strip('>')
        post = {'title': ''.join(title),
                'date': ''.join(date),
                'article': ''.join(article),
                'post-link': post_link}
        self.articles.insert_one(post)

# Spider class for https://www.electrojams.com/ domain monitoring


class ArticleSpider25(scrapy.Spider):
    name = "article"
    allowed_domains = ['www.electrojams.com']
    start_urls = ['https://www.electrojams.com/']
    post_urls = []
    page_id = 2
    new_content_flag = 1
    core_link = 'https://www.electrojams.com/page/'
    client = MongoClient('mongodb://localhost:27017')
    db = client['Articles_DB']
    articles = db.articles25
    url_repository = db.urls
    repo_existence_check = 0
    link_xpath = '//*/div/div/div[1]/h4/a/@href'
    max_pages = 400
    dates_of_articles = list()
    list_of_dates = list()

    def parse(self, response):
        urls_repo_cursor = self.url_repository.find()
        for item in urls_repo_cursor:
            if '_id' and 'post_urls_repo25' in item:
                self.repo_existence_check += 1
                local_item = item
        if self.repo_existence_check == 0:
            dates = response.xpath('//*/div/div/div[3]/span[1]/text()').extract()
            titles = response.xpath('//*/ div /div/div[1]/h4/a/text()').extract()
            self.dates_of_articles = list(map(lambda x, y: (x, y), titles, dates))
            for article_info in self.dates_of_articles:
                self.list_of_dates.append(article_info)
            for article_url in response.xpath(self.link_xpath).extract():
                if not (article_url in self.post_urls):
                    self.post_urls.append(article_url)
                    yield response.follow(article_url, callback=self.parse_article)

            next_page = requests.get(self.core_link + str(self.page_id))

            if next_page.status_code == 200 and self.page_id <= self.max_pages:
                next_page_link = (self.core_link + str(self.page_id))
                self.page_id += 1
                yield response.follow(next_page_link, callback=self.parse)
            else:
                included_posts = {'post_urls_repo25': self.post_urls}
                self.url_repository.insert_one(included_posts)

        else:
            self.post_urls = local_item['post_urls_repo25']

            if self.new_content_flag == 1:
                for article_url in response.xpath(self.link_xpath).extract():
                    if not (article_url in self.post_urls):
                        self.post_urls.append(article_url)
                        yield response.follow(article_url, callback=self.parse_article)
                    else:
                        self.new_content_flag = 0

                url_repo_id = local_item['_id']
                self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo25': self.post_urls}})
                next_page = requests.get(self.core_link + str(self.page_id))

                if next_page.status_code == 200 and self.page_id <= self.max_pages:
                    next_page_link = (self.core_link + str(self.page_id))
                    self.page_id += 1
                    yield response.follow(next_page_link, callback=self.parse)
                else:
                    url_repo_id = local_item['_id']
                    self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo25': self.post_urls}})

    def parse_article(self, response):
        title = response.xpath('//*[@id="page"]/section/div/div/div/h1//text()').extract()
        article = response.xpath('//*/div/p//text()').extract()
        post_link = str(response)
        post_link = post_link.strip('<200 ')
        post_link = post_link.strip('>')
        date = ''
        for item in self.dates_of_articles:
            if str(title[0]) == item[0]:
                index = self.dates_of_articles.index(item)
                item_tuple = self.dates_of_articles[index]
                date = item_tuple[1]
        if date == '':
            for item in self.list_of_dates:
                if str(title[0]) == item[0]:
                    index = self.list_of_dates.index(item)
                    item_tuple = self.list_of_dates[index]
                    date = item_tuple[1]
        post = {'title': ''.join(title),
                'date': ''.join(date),
                'article': ''.join(article),
                'post-link': post_link}
        self.articles.insert_one(post)

# Spider class for http://edmnyc.com/ domain monitoring


class ArticleSpider26(scrapy.Spider):
    name = "article"
    allowed_domains = ['edmnyc.com']
    start_urls = ['http://edmnyc.com/category/latestevents/',
                  'http://edmnyc.com/category/global-news/']
    post_urls = []
    page_id_1 = 2
    page_id_2 = 2
    new_content_flag = 1
    core_link_2 = 'http://edmnyc.com/category/global-news/page/'
    core_link_1 = 'http://edmnyc.com/category/latestevents/page/'
    client = MongoClient('mongodb://localhost:27017')
    db = client['Articles_DB']
    articles = db.articles26
    url_repository = db.urls
    repo_existence_check = 0
    link_xpath = '/html/body/div[2]/div[4]/div/div/div[1]/div/article/h2/a/@href'
    max_pages_1 = 200
    max_pages_2 = 100

    def parse(self, response):
        urls_repo_cursor = self.url_repository.find()
        for item in urls_repo_cursor:
            if '_id' and 'post_urls_repo26' in item:
                self.repo_existence_check += 1
                local_item = item

        if self.repo_existence_check == 0:
            for article_url in response.xpath(self.link_xpath).extract():
                if not (article_url in self.post_urls):
                    self.post_urls.append(article_url)
                    yield response.follow(article_url, callback=self.parse_article)

            next_page_1 = requests.get(self.core_link_1 + str(self.page_id_1))
            next_page_2 = requests.get(self.core_link_2 + str(self.page_id_2))

            if next_page_1.status_code == 200 and self.page_id_1 <= self.max_pages_1:
                next_page_link = (self.core_link_1 + str(self.page_id_1))
                self.page_id_1 += 1
                yield response.follow(next_page_link, callback=self.parse)

            elif next_page_2.status_code == 200 and self.page_id_2 <= self.max_pages_2:
                next_page_link = (self.core_link_2 + str(self.page_id_2))
                self.page_id_2 += 1
                yield response.follow(next_page_link, callback=self.parse)

            else:
                included_posts = {'post_urls_repo26': self.post_urls}
                self.url_repository.insert_one(included_posts)
        else:
            self.post_urls = local_item['post_urls_repo26']

            if self.new_content_flag == 1:
                for article_url in response.xpath(self.link_xpath).extract():
                    if not (article_url in self.post_urls):
                        self.post_urls.append(article_url)
                        yield response.follow(article_url, callback=self.parse_article)
                    else:
                        self.new_content_flag = 0

                url_repo_id = local_item['_id']
                self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo26': self.post_urls}})
                next_page_1 = requests.get(self.core_link_1 + str(self.page_id_1))
                next_page_2 = requests.get(self.core_link_2 + str(self.page_id_2))

                if next_page_1.status_code == 200 and self.page_id_1 <= self.max_pages_1:
                    next_page_link = (self.core_link_1 + str(self.page_id_1))
                    self.page_id_1 += 1
                    yield response.follow(next_page_link, callback=self.parse)

                elif next_page_2.status_code == 200 and self.page_id_2 <= self.max_pages_2:
                    next_page_link = (self.core_link_2 + str(self.page_id_2))
                    self.page_id_2 += 1
                    yield response.follow(next_page_link, callback=self.parse)
                else:
                    url_repo_id = local_item['_id']
                    self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo26': self.post_urls}})

    def parse_article(self, response):
        title = response.xpath('//*/header/h1//text()').extract()
        date = response.xpath('//*/div[1]/span[2]/span/time/text()').extract()
        article = response.xpath('//*/div[2]/div/div/p//text()'
                                 or '//*/div[2]/div/div/div//span//text()').extract()
        post_link = str(response)
        post_link = post_link.strip('<200 ')
        post_link = post_link.strip('>')
        post = {'title': ''.join(title),
                'date': ''.join(date),
                'article': ''.join(article),
                'post-link': post_link}
        self.articles.insert_one(post)

# Spider class for https://www.housemusicwithlove.com domain monitoring


class ArticleSpider27(scrapy.Spider):
    name = "article"
    allowed_domains = ['www.housemusicwithlove.com']
    start_urls = ['https://www.housemusicwithlove.com/blog/']
    post_urls = []
    page_id = 2
    new_content_flag = 1
    core_link = 'https://www.housemusicwithlove.com/blog/page/'
    client = MongoClient('mongodb://localhost:27017')
    db = client['Articles_DB']
    articles = db.articles27
    url_repository = db.urls
    repo_existence_check = 0
    link_xpath = '//*/div/div[2]/h2/a/@href'
    max_pages = 110

    def parse(self, response):
        urls_repo_cursor = self.url_repository.find()
        for item in urls_repo_cursor:
            if '_id' and 'post_urls_repo27' in item:
                self.repo_existence_check += 1
                local_item = item

        if self.repo_existence_check == 0:
            for article_url in response.xpath(self.link_xpath).extract():
                if not (article_url in self.post_urls):
                    self.post_urls.append(article_url)
                    yield response.follow(article_url, callback=self.parse_article)

            next_page = requests.get(self.core_link + str(self.page_id))

            if next_page.status_code == 200 and self.page_id <= self.max_pages:
                next_page_link = (self.core_link + str(self.page_id))
                self.page_id += 1
                yield response.follow(next_page_link, callback=self.parse)
            else:
                included_posts = {'post_urls_repo27': self.post_urls}
                self.url_repository.insert_one(included_posts)

        else:
            self.post_urls = local_item['post_urls_repo27']

            if self.new_content_flag == 1:
                for article_url in response.xpath(self.link_xpath).extract():
                    if not (article_url in self.post_urls):
                        self.post_urls.append(article_url)
                        yield response.follow(article_url, callback=self.parse_article)
                    else:
                        self.new_content_flag = 0

                url_repo_id = local_item['_id']
                self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo27': self.post_urls}})
                next_page = requests.get(self.core_link + str(self.page_id))

                if next_page.status_code == 200 and self.page_id <= self.max_pages:
                    next_page_link = (self.core_link + str(self.page_id))
                    self.page_id += 1
                    yield response.follow(next_page_link, callback=self.parse)
                else:
                    url_repo_id = local_item['_id']
                    self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo27': self.post_urls}})

    def parse_article(self, response):
        title = response.xpath('//*/div[1]/div/header/h1/text()').extract()
        date = response.xpath('//*/div[1]/div/header/ul/li/a/time//text()').extract()
        article = response.xpath('//*/div[2]/div/div/p//text()').extract()
        post_link = str(response)
        post_link = post_link.strip('<200 ')
        post_link = post_link.strip('>')
        post = {'title': ''.join(title),
                'date': ''.join(date),
                'article': ''.join(article),
                'post-link': post_link}
        self.articles.insert_one(post)

# Spider class for https://thetechnokittens.com domain monitoring


class ArticleSpider28(scrapy.Spider):
    name = "article"
    allowed_domains = ['thetechnokittens.com']
    start_urls = ['https://thetechnokittens.com/blog/']
    post_urls = []
    page_id = 2
    new_content_flag = 1
    core_link = 'https://thetechnokittens.com/blog/page/'
    client = MongoClient('mongodb://localhost:27017')
    db = client['Articles_DB']
    articles = db.articles28
    url_repository = db.urls
    repo_existence_check = 0
    link_xpath = '//*[ @ id = "main"]/div[2]/div/main/article/div[2]/header/h2/a/@href'
    max_pages = 110

    def parse(self, response):
        urls_repo_cursor = self.url_repository.find()
        for item in urls_repo_cursor:
            if '_id' and 'post_urls_repo28' in item:
                self.repo_existence_check += 1
                local_item = item

        if self.repo_existence_check == 0:
            for article_url in response.xpath(self.link_xpath).extract():
                if not (article_url in self.post_urls):
                    self.post_urls.append(article_url)
                    yield response.follow(article_url, callback=self.parse_article)

            next_page = requests.get(self.core_link + str(self.page_id))

            if next_page.status_code == 200 and self.page_id <= self.max_pages:
                next_page_link = (self.core_link + str(self.page_id))
                self.page_id += 1
                yield response.follow(next_page_link, callback=self.parse)
            else:
                included_posts = {'post_urls_repo28': self.post_urls}
                self.url_repository.insert_one(included_posts)

        else:
            self.post_urls = local_item['post_urls_repo28']

            if self.new_content_flag == 1:
                for article_url in response.xpath(self.link_xpath).extract():
                    if not (article_url in self.post_urls):
                        self.post_urls.append(article_url)
                        yield response.follow(article_url, callback=self.parse_article)
                    else:
                        self.new_content_flag = 0

                url_repo_id = local_item['_id']
                self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo28': self.post_urls}})
                next_page = requests.get(self.core_link + str(self.page_id))

                if next_page.status_code == 200 and self.page_id <= self.max_pages:
                    next_page_link = (self.core_link + str(self.page_id))
                    self.page_id += 1
                    yield response.follow(next_page_link, callback=self.parse)
                else:
                    url_repo_id = local_item['_id']
                    self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo28': self.post_urls}})

    def parse_article(self, response):
        title = response.xpath('//*[@id="main"]/div[2]/div/main/article/div[2]/header/h1/a/@title').extract()
        date = response.xpath('//*[@id="main"]/div[2]/div/main/article/div[2]/header/span/time/text()').extract()
        article = response.xpath('//*[@id="main"]/div[2]/div/main/article/div[2]/div[1]/p//text()').extract()
        post_link = str(response)
        post_link = post_link.strip('<200 ')
        post_link = post_link.strip('>')
        post = {'title': ''.join(title),
                'date': ''.join(date),
                'article': ''.join(article),
                'post-link': post_link}
        self.articles.insert_one(post)

# Spider class for http://www.dubtechnoblog.com/ domain monitoring


class ArticleSpider29(scrapy.Spider):
    name = "article"
    allowed_domains = ['www.dubtechnoblog.com']
    start_urls = ['http://www.dubtechnoblog.com/']
    post_urls = []
    page_id = 2
    new_content_flag = 1
    core_link = 'http://www.dubtechnoblog.com/page/'
    client = MongoClient('mongodb://localhost:27017')
    db = client['Articles_DB']
    articles = db.articles29
    url_repository = db.urls
    repo_existence_check = 0
    link_xpath = '//*/header/h1/a/@href'
    max_pages = 110

    def parse(self, response):
        urls_repo_cursor = self.url_repository.find()
        for item in urls_repo_cursor:
            if '_id' and 'post_urls_repo29' in item:
                self.repo_existence_check += 1
                local_item = item

        if self.repo_existence_check == 0:
            for article_url in response.xpath(self.link_xpath).extract():
                if not (article_url in self.post_urls):
                    self.post_urls.append(article_url)
                    yield response.follow(article_url, callback=self.parse_article)

            next_page = requests.get(self.core_link + str(self.page_id))

            if next_page.status_code == 200 and self.page_id <= self.max_pages:
                next_page_link = (self.core_link + str(self.page_id))
                self.page_id += 1
                yield response.follow(next_page_link, callback=self.parse)
            else:
                included_posts = {'post_urls_repo29': self.post_urls}
                self.url_repository.insert_one(included_posts)

        else:
            self.post_urls = local_item['post_urls_repo29']

            if self.new_content_flag == 1:
                for article_url in response.xpath(self.link_xpath).extract():
                    if not (article_url in self.post_urls):
                        self.post_urls.append(article_url)
                        yield response.follow(article_url, callback=self.parse_article)
                    else:
                        self.new_content_flag = 0

                url_repo_id = local_item['_id']
                self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo29': self.post_urls}})
                next_page = requests.get(self.core_link + str(self.page_id))

                if next_page.status_code == 200 and self.page_id <= self.max_pages:
                    next_page_link = (self.core_link + str(self.page_id))
                    self.page_id += 1
                    yield response.follow(next_page_link, callback=self.parse)
                else:
                    url_repo_id = local_item['_id']
                    self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo29': self.post_urls}})

    def parse_article(self, response):
        title = response.xpath('//*/header/h1/a/text()').extract()
        date = response.xpath('//*/header/div/span[1]/a/time[1]/text()').extract()
        article = response.xpath('//*/div[2]/p//text()').extract()
        post_link = str(response)
        post_link = post_link.strip('<200 ')
        post_link = post_link.strip('>')
        post = {'title': ''.join(title),
                'date': ''.join(date),
                'article': ''.join(article),
                'post-link': post_link}
        self.articles.insert_one(post)

# Spider class for http://www.electronicaoasis.com/ domain monitoring


class ArticleSpider30(scrapy.Spider):
    name = "article"
    allowed_domains = ['www.electronicaoasis.com']
    start_urls = ['http://www.electronicaoasis.com/']
    post_urls = []
    page_id = 2
    new_content_flag = 1
    core_link = 'http://www.electronicaoasis.com/page/'
    client = MongoClient('mongodb://localhost:27017')
    db = client['Articles_DB']
    articles = db.articles30
    url_repository = db.urls
    repo_existence_check = 0
    link_xpath = '//*[ @ id = "content"]/div/section/div[1]/article/header/h2/a/@href'
    max_pages = 400

    def parse(self, response):
        urls_repo_cursor = self.url_repository.find()
        for item in urls_repo_cursor:
            if '_id' and 'post_urls_repo30' in item:
                self.repo_existence_check += 1
                local_item = item

        if self.repo_existence_check == 0:
            for article_url in response.xpath(self.link_xpath).extract():
                if not (article_url in self.post_urls):
                    self.post_urls.append(article_url)
                    yield response.follow(article_url, callback=self.parse_article)

            next_page = requests.get(self.core_link + str(self.page_id))

            if next_page.status_code == 200 and self.page_id <= self.max_pages:
                next_page_link = (self.core_link + str(self.page_id))
                self.page_id += 1
                yield response.follow(next_page_link, callback=self.parse)
            else:
                included_posts = {'post_urls_repo30': self.post_urls}
                self.url_repository.insert_one(included_posts)

        else:
            self.post_urls = local_item['post_urls_repo30']

            if self.new_content_flag == 1:
                for article_url in response.xpath(self.link_xpath).extract():
                    if not (article_url in self.post_urls):
                        self.post_urls.append(article_url)
                        yield response.follow(article_url, callback=self.parse_article)
                    else:
                        self.new_content_flag = 0

                url_repo_id = local_item['_id']
                self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo30': self.post_urls}})
                next_page = requests.get(self.core_link + str(self.page_id))

                if next_page.status_code == 200 and self.page_id <= self.max_pages:
                    next_page_link = (self.core_link + str(self.page_id))
                    self.page_id += 1
                    yield response.follow(next_page_link, callback=self.parse)
                else:
                    url_repo_id = local_item['_id']
                    self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo30': self.post_urls}})

    def parse_article(self, response):
        title = response.xpath('//*/header/h1/span//text()').extract()
        date = response.xpath('//*/header/div/span[2]/text()').extract()
        article = response.xpath('//*/div/div/p//text()').extract()
        post_link = str(response)
        post_link = post_link.strip('<200 ')
        post_link = post_link.strip('>')
        post = {'title': ''.join(title),
                'date': ''.join(date),
                'article': ''.join(article),
                'post-link': post_link}
        self.articles.insert_one(post)

# Spider class for http://www.breaksblog.biz/ domain monitoring


class ArticleSpider31(scrapy.Spider):
    name = "article"
    allowed_domains = ['www.breaksblog.biz']
    start_urls = ['http://www.breaksblog.biz/']
    post_urls = []
    page_id = 2
    new_content_flag = 1
    core_link = 'http://www.breaksblog.biz/page/'
    client = MongoClient('mongodb://localhost:27017')
    db = client['Articles_DB']
    articles = db.articles31
    url_repository = db.urls
    repo_existence_check = 0
    link_xpath = '//*/header/h2/a/@href'
    max_pages = 150

    def parse(self, response):
        urls_repo_cursor = self.url_repository.find()
        for item in urls_repo_cursor:
            if '_id' and 'post_urls_repo31' in item:
                self.repo_existence_check += 1
                local_item = item

        if self.repo_existence_check == 0:
            for article_url in response.xpath(self.link_xpath).extract():
                if not (article_url in self.post_urls):
                    self.post_urls.append(article_url)
                    yield response.follow(article_url, callback=self.parse_article)

            next_page = requests.get(self.core_link + str(self.page_id))

            if next_page.status_code == 200 and self.page_id <= self.max_pages:
                next_page_link = (self.core_link + str(self.page_id))
                self.page_id += 1
                yield response.follow(next_page_link, callback=self.parse)
            else:
                included_posts = {'post_urls_repo31': self.post_urls}
                self.url_repository.insert_one(included_posts)

        else:
            self.post_urls = local_item['post_urls_repo31']

            if self.new_content_flag == 1:
                for article_url in response.xpath(self.link_xpath).extract():
                    if not (article_url in self.post_urls):
                        self.post_urls.append(article_url)
                        yield response.follow(article_url, callback=self.parse_article)
                    else:
                        self.new_content_flag = 0

                url_repo_id = local_item['_id']
                self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo31': self.post_urls}})
                next_page = requests.get(self.core_link + str(self.page_id))

                if next_page.status_code == 200 and self.page_id <= self.max_pages:
                    next_page_link = (self.core_link + str(self.page_id))
                    self.page_id += 1
                    yield response.follow(next_page_link, callback=self.parse)
                else:
                    url_repo_id = local_item['_id']
                    self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo31': self.post_urls}})

    def parse_article(self, response):
        title = response.xpath('//*/header/h1//text()').extract()
        date = response.xpath('//*/header/div/span/time[1]/text()').extract()
        article = response.xpath('//*/div//p//text()').extract()
        post_link = str(response)
        post_link = post_link.strip('<200 ')
        post_link = post_link.strip('>')
        post = {'title': ''.join(title),
                'date': ''.join(date),
                'article': ''.join(article),
                'post-link': post_link}
        self.articles.insert_one(post)

# Spider class for http://dropthebeatz.com/ domain monitoring


class ArticleSpider32(scrapy.Spider):
    name = "article"
    allowed_domains = ['dropthebeatz.com']
    start_urls = ['http://dropthebeatz.com/category/new-music/']
    post_urls = []
    page_id = 2
    new_content_flag = 1
    core_link = 'http://dropthebeatz.com/category/new-music/page/'
    client = MongoClient('mongodb://localhost:27017')
    db = client['Articles_DB']
    articles = db.articles32
    url_repository = db.urls
    repo_existence_check = 0
    link_xpath = '//*/div[2]/h2/a/@href'
    max_pages = 150

    def parse(self, response):
        urls_repo_cursor = self.url_repository.find()
        for item in urls_repo_cursor:
            if '_id' and 'post_urls_repo32' in item:
                self.repo_existence_check += 1
                local_item = item

        if self.repo_existence_check == 0:
            for article_url in response.xpath(self.link_xpath).extract():
                if not (article_url in self.post_urls):
                    self.post_urls.append(article_url)
                    yield response.follow(article_url, callback=self.parse_article)

            next_page = requests.get(self.core_link + str(self.page_id))

            if next_page.status_code == 200 and self.page_id <= self.max_pages:
                next_page_link = (self.core_link + str(self.page_id))
                self.page_id += 1
                yield response.follow(next_page_link, callback=self.parse)
            else:
                included_posts = {'post_urls_repo32': self.post_urls}
                self.url_repository.insert_one(included_posts)

        else:
            self.post_urls = local_item['post_urls_repo32']

            if self.new_content_flag == 1:
                for article_url in response.xpath(self.link_xpath).extract():
                    if not (article_url in self.post_urls):
                        self.post_urls.append(article_url)
                        yield response.follow(article_url, callback=self.parse_article)
                    else:
                        self.new_content_flag = 0

                url_repo_id = local_item['_id']
                self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo32': self.post_urls}})
                next_page = requests.get(self.core_link + str(self.page_id))

                if next_page.status_code == 200 and self.page_id <= self.max_pages:
                    next_page_link = (self.core_link + str(self.page_id))
                    self.page_id += 1
                    yield response.follow(next_page_link, callback=self.parse)
                else:
                    url_repo_id = local_item['_id']
                    self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo32': self.post_urls}})

    def parse_article(self, response):
        title = response.xpath('//*[@id="omc-full-article"]/h1//text()').extract()
        date = response.xpath('//*[@id="omc-inner-placeholder"]/div/p/text()').extract()
        date_after_format = ''.join(date[1:])
        date_after_format = date_after_format.replace(' |', '')
        article = response.xpath('//*[@id="omc-full-article"]/p//text()').extract()
        post_link = str(response)
        post_link = post_link.strip('<200 ')
        post_link = post_link.strip('>')
        post = {'title': ''.join(title),
                'date': ''.join(date_after_format),
                'article': ''.join(article),
                'post-link': post_link}
        self.articles.insert_one(post)

# Spider class for http://trancemusicblog.com/ domain monitoring


class ArticleSpider33(scrapy.Spider):
    name = "article"
    allowed_domains = ['trancemusicblog.com']
    start_urls = ['http://trancemusicblog.com/']
    post_urls = []
    new_content_flag = 1
    client = MongoClient('mongodb://localhost:27017')
    db = client['Articles_DB']
    articles = db.articles33
    url_repository = db.urls
    repo_existence_check = 0
    link_xpath = '//*[ @ id = "recent-posts-4"]/div/ul/li/a/@href'

    def parse(self, response):
        urls_repo_cursor = self.url_repository.find()
        for item in urls_repo_cursor:
            if '_id' and 'post_urls_repo33' in item:
                self.repo_existence_check += 1
                local_item = item

        if self.repo_existence_check == 0:
            for article_url in response.xpath(self.link_xpath).extract():
                if not (article_url in self.post_urls):
                    self.post_urls.append(article_url)
                    yield response.follow(article_url, callback=self.parse_article)

            included_posts = {'post_urls_repo33': self.post_urls}
            self.url_repository.insert_one(included_posts)

        else:
            self.post_urls = local_item['post_urls_repo33']

            if self.new_content_flag == 1:
                for article_url in response.xpath(self.link_xpath).extract():
                    if not (article_url in self.post_urls):
                        self.post_urls.append(article_url)
                        yield response.follow(article_url, callback=self.parse_article)
                    else:
                        self.new_content_flag = 0

                url_repo_id = local_item['_id']
                self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo33': self.post_urls}})

    def parse_article(self, response):
        title = response.xpath('/html/body/div[2]/div/div/main/article/header/h1//text()').extract()
        article = response.xpath('/html/body/div[2]/div/div/main/article/div/p//text()').extract()
        post_link = str(response)
        post_link = post_link.strip('<200 ')
        post_link = post_link.strip('>')
        post = {'title': ''.join(title),
                'date': ''.join(''),
                'article': ''.join(article),
                'post-link': post_link}
        self.articles.insert_one(post)

# Spider class for https://datatransmission.co/ domain monitoring


class ArticleSpider34(scrapy.Spider):
    name = "article"
    allowed_domains = ['datatransmission.co']
    start_urls = ['https://datatransmission.co/news/']
    post_urls = []
    page_id = 2
    new_content_flag = 1
    core_link = 'https://datatransmission.co/news/page/'
    client = MongoClient('mongodb://localhost:27017')
    db = client['Articles_DB']
    articles = db.articles34
    url_repository = db.urls
    repo_existence_check = 0
    link_xpath = '// *[ @ id = "content-wrapper"] /div[1]/div[2]/div[1]/div/div/a/@href'
    max_pages = 500

    def parse(self, response):
        urls_repo_cursor = self.url_repository.find()
        for item in urls_repo_cursor:
            if '_id' and 'post_urls_repo34' in item:
                self.repo_existence_check += 1
                local_item = item

        if self.repo_existence_check == 0:
            for article_url in response.xpath(self.link_xpath).extract():
                if not (article_url in self.post_urls):
                    self.post_urls.append(article_url)
                    yield response.follow(article_url, callback=self.parse_article)

            next_page = requests.get(self.core_link + str(self.page_id))

            if next_page.status_code == 200 and self.page_id <= self.max_pages:
                next_page_link = (self.core_link + str(self.page_id))
                self.page_id += 1
                yield response.follow(next_page_link, callback=self.parse)
            else:
                included_posts = {'post_urls_repo34': self.post_urls}
                self.url_repository.insert_one(included_posts)

        else:
            self.post_urls = local_item['post_urls_repo34']

            if self.new_content_flag == 1:
                for article_url in response.xpath(self.link_xpath).extract():
                    if not (article_url in self.post_urls):
                        self.post_urls.append(article_url)
                        yield response.follow(article_url, callback=self.parse_article)
                    else:
                        self.new_content_flag = 0

                url_repo_id = local_item['_id']
                self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo34': self.post_urls}})
                next_page = requests.get(self.core_link + str(self.page_id))

                if next_page.status_code == 200 and self.page_id <= self.max_pages:
                    next_page_link = (self.core_link + str(self.page_id))
                    self.page_id += 1
                    yield response.follow(next_page_link, callback=self.parse)
                else:
                    url_repo_id = local_item['_id']
                    self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo34': self.post_urls}})

    def parse_article(self, response):
        title = response.xpath('//*[@id="content-wrapper"]/div[2]/div[2]/div[1]/article/h1//text()').extract()
        date = response.xpath('//*[@id="content-wrapper"]/div[2]/div[2]/div[1]/article/div[5]/div/span[2]/text()').extract()
        article = response.xpath('//*[@id="content-wrapper"]/div[2]/div[2]/div[1]/article/div[9]/p//text()').extract()
        post_link = str(response)
        post_link = post_link.strip('<200 ')
        post_link = post_link.strip('>')
        post = {'title': ''.join(title),
                'date': ''.join(date),
                'article': ''.join(article),
                'post-link': post_link}
        self.articles.insert_one(post)

# Spider class for http://www.edmlounge.com/ domain monitoring


class ArticleSpider35(scrapy.Spider):
    name = "article"
    allowed_domains = ['www.edmlounge.com']
    start_urls = ['http://www.edmlounge.com/']
    post_urls = []
    page_id = 2
    new_content_flag = 1
    core_link = 'http://www.edmlounge.com/blog/?currentPage='
    client = MongoClient('mongodb://localhost:27017')
    db = client['Articles_DB']
    articles = db.articles35
    url_repository = db.urls
    repo_existence_check = 0
    link_xpath = '//*/div[3]/h2/a/@href'
    max_pages = 150

    def parse(self, response):
        urls_repo_cursor = self.url_repository.find()
        for item in urls_repo_cursor:
            if '_id' and 'post_urls_repo35' in item:
                self.repo_existence_check += 1
                local_item = item

        if self.repo_existence_check == 0:
            for article_url in response.xpath(self.link_xpath).extract():
                if not (article_url in self.post_urls):
                    self.post_urls.append(article_url)
                    yield response.follow(article_url, callback=self.parse_article)

            next_page = requests.get(self.core_link + str(self.page_id))

            if next_page.status_code == 200 and self.page_id <= self.max_pages:
                next_page_link = (self.core_link + str(self.page_id))
                self.page_id += 1
                yield response.follow(next_page_link, callback=self.parse)
            else:
                included_posts = {'post_urls_repo35': self.post_urls}
                self.url_repository.insert_one(included_posts)

        else:
            self.post_urls = local_item['post_urls_repo35']

            if self.new_content_flag == 1:
                for article_url in response.xpath(self.link_xpath).extract():
                    if not (article_url in self.post_urls):
                        self.post_urls.append(article_url)
                        yield response.follow(article_url, callback=self.parse_article)
                    else:
                        self.new_content_flag = 0

                url_repo_id = local_item['_id']
                self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo35': self.post_urls}})
                next_page = requests.get(self.core_link + str(self.page_id))

                if next_page.status_code == 200 and self.page_id <= self.max_pages:
                    next_page_link = (self.core_link + str(self.page_id))
                    self.page_id += 1
                    yield response.follow(next_page_link, callback=self.parse)
                else:
                    url_repo_id = local_item['_id']
                    self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo35': self.post_urls}})

    def parse_article(self, response):
        title = response.xpath('//*/div[3]/h2/a//text()').extract()
        date = response.xpath('//*/div[4]/div[3]/span[1]/text()[2]').extract()
        article = response.xpath('//*/div[3]/div[2]/p//text()').extract()
        regex = r'(.+?)(?= [a-z]{2})'
        date_after_format = date[0]
        date_after_format = re.match(regex, date_after_format).group(0)
        date_after_format = date_after_format.split(',')
        date_after_format = ','.join(date_after_format[1:3]).strip(' ')
        post_link = str(response)
        post_link = post_link.strip('<200 ')
        post_link = post_link.strip('>')
        post = {'title': ''.join(title),
                'date': ''.join(date_after_format),
                'article': ''.join(article),
                'post-link': post_link}
        self.articles.insert_one(post)

# Spider class for https://en.wordpress.com/tag/electronic-music/ domain monitoring


class ArticleSpider36(scrapy.Spider):
    name = "article"
    start_urls = ['https://en.wordpress.com/tag/electronic-music/']
    post_urls = []
    new_content_flag = 1
    client = MongoClient('mongodb://localhost:27017')
    db = client['Articles_DB']
    articles = db.articles36
    url_repository = db.urls
    repo_existence_check = 0
    link_xpath = '//*[@id="tag-posts"]/div/div[2]/h4/a/@href'

    def parse(self, response):
        urls_repo_cursor = self.url_repository.find()
        for item in urls_repo_cursor:
            if '_id' and 'post_urls_repo36' in item:
                self.repo_existence_check += 1
                local_item = item

        if self.repo_existence_check == 0:
            for article_url in response.xpath(self.link_xpath).extract():
                if not (article_url in self.post_urls):
                    self.post_urls.append(article_url)
                    yield response.follow(article_url, callback=self.parse_article)

            included_posts = {'post_urls_repo36': self.post_urls}
            self.url_repository.insert_one(included_posts)

        else:
            self.post_urls = local_item['post_urls_repo36']

            if self.new_content_flag == 1:
                for article_url in response.xpath(self.link_xpath).extract():
                    if not (article_url in self.post_urls):
                        self.post_urls.append(article_url)
                        yield response.follow(article_url, callback=self.parse_article)
                    else:
                        self.new_content_flag = 0

                url_repo_id = local_item['_id']
                self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo36': self.post_urls}})

    def parse_article(self, response):
        title = response.css('h1::text,h2::text').extract_first()
        date = response.css('time::text,.date span::text').extract_first()
        article = response.css('p::text, p a::text, p b::text ,p i::text ,'
                               'p strong::text,span::text').extract()
        post_link = str(response)
        post_link = post_link.strip('<200 ')
        post_link = post_link.strip('>')
        post = {'title': ''.join(title),
                'date': date,
                'article': ''.join(article),
                'post-link': post_link}
        self.articles.insert_one(post)

# Spider class for https://darkfloor.co.uk/ domain monitoring


class ArticleSpider37(scrapy.Spider):
    name = "article"
    allowed_domains = ['darkfloor.co.uk']
    start_urls = ['https://darkfloor.co.uk/words/']
    post_urls = []
    page_id = 2
    new_content_flag = 1
    core_link = 'https://darkfloor.co.uk/words/page/'
    client = MongoClient('mongodb://localhost:27017')
    db = client['Articles_DB']
    articles = db.articles37
    url_repository = db.urls
    repo_existence_check = 0
    link_xpath = '//*[ @ id = "blog"]/div/h3/a/@href'
    max_pages = 50

    def parse(self, response):
        urls_repo_cursor = self.url_repository.find()
        for item in urls_repo_cursor:
            if '_id' and 'post_urls_repo37' in item:
                self.repo_existence_check += 1
                local_item = item

        if self.repo_existence_check == 0:
            for article_url in response.xpath(self.link_xpath).extract():
                if not (article_url in self.post_urls):
                    self.post_urls.append(article_url)
                    yield response.follow(article_url, callback=self.parse_article)

            next_page = requests.get(self.core_link + str(self.page_id))

            if next_page.status_code == 200 and self.page_id <= self.max_pages:
                next_page_link = (self.core_link + str(self.page_id))
                self.page_id += 1
                yield response.follow(next_page_link, callback=self.parse)
            else:
                included_posts = {'post_urls_repo37': self.post_urls}
                self.url_repository.insert_one(included_posts)

        else:
            self.post_urls = local_item['post_urls_repo37']

            if self.new_content_flag == 1:
                for article_url in response.xpath(self.link_xpath).extract():
                    if not (article_url in self.post_urls):
                        self.post_urls.append(article_url)
                        yield response.follow(article_url, callback=self.parse_article)
                    else:
                        self.new_content_flag = 0

                url_repo_id = local_item['_id']
                self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo37': self.post_urls}})
                next_page = requests.get(self.core_link + str(self.page_id))

                if next_page.status_code == 200 and self.page_id <= self.max_pages:
                    next_page_link = (self.core_link + str(self.page_id))
                    self.page_id += 1
                    yield response.follow(next_page_link, callback=self.parse)
                else:
                    url_repo_id = local_item['_id']
                    self.url_repository.update_one({'_id': url_repo_id}, {'$set': {'post_urls_repo37': self.post_urls}})

    def parse_article(self, response):
        title = response.xpath('//*[@id="content"]/div[1]/h1//text()').extract()
        date = response.xpath('//*[@id="content"]/div[2]/div[1]/div[1]/span[2]/text()').extract()
        date_after_format = ''.join(date)
        date_after_format = date_after_format.replace('on ', '')
        article = response.xpath('//*[@id="content"]/div[2]/div[1]/div[2]/p//text()').extract()
        post_link = str(response)
        post_link = post_link.strip('<200 ')
        post_link = post_link.strip('>')
        post = {'title': ''.join(title),
                'date': ''.join(date_after_format),
                'article': ''.join(article),
                'post-link': post_link}
        self.articles.insert_one(post)

if __name__ == "__main__":
    process = CrawlerProcess()
    # process.crawl(ArticleSpider1)
    # process.crawl(ArticleSpider2)
    # process.crawl(ArticleSpider4)
    # process.crawl(ArticleSpider5)
    # process.crawl(ArticleSpider6)
    # process.crawl(ArticleSpider8)
    # process.crawl(ArticleSpider9)
    # process.crawl(ArticleSpider10)
    # process.crawl(ArticleSpider11)
    # process.crawl(ArticleSpider12)
    # process.crawl(ArticleSpider13)
    # process.crawl(ArticleSpider14)
    # process.crawl(ArticleSpider15)
    # process.crawl(ArticleSpider16)
    # process.crawl(ArticleSpider17)
    # process.crawl(ArticleSpider18)
    # process.crawl(ArticleSpider19)
    # process.crawl(ArticleSpider20)
    # process.crawl(ArticleSpider21)
    # process.crawl(ArticleSpider22)
    # process.crawl(ArticleSpider23)
    # process.crawl(ArticleSpider24)
    # process.crawl(ArticleSpider25)
    # process.crawl(ArticleSpider26)
    # process.crawl(ArticleSpider27)
    # process.crawl(ArticleSpider28)
    # process.crawl(ArticleSpider29)
    # process.crawl(ArticleSpider30)
    # process.crawl(ArticleSpider31)
    # process.crawl(ArticleSpider32)
    # process.crawl(ArticleSpider33)
    # process.crawl(ArticleSpider34)
    # process.crawl(ArticleSpider35)
    # process.crawl(ArticleSpider36)
    # process.crawl(ArticleSpider37)
    process.start()

