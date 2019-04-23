import scrapy
import requests
import re
from pymongo import MongoClient
from scrapy.crawler import CrawlerProcess
from scrapy import Request



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


# Spider class for https://consequenceofsound.net/ domain monitoring(pagination trouble)


class ArticleSpider3(scrapy.Spider):
    name = "article"
    allowed_domains = ['consequenceofsound.net']
    start_urls = ['https://consequenceofsound.net/category/check-out/']
    post_urls = []
    new_content_flag = 1
    client = MongoClient('mongodb://localhost:27017')
    db = client['Articles_DB']
    articles = db.articles3
    url_repository = db.urls
    repo_existence_check = 0

    def parse(self, response):
        urls_repo_cursor = self.url_repository.find()
        for item in urls_repo_cursor:
            if '_id' and 'post_urls_repo3' in item:
                self.repo_existence_check += 1
                local_item = item

        if self.repo_existence_check > 0:

            self.post_urls = local_item['post_urls_repo3']
            if self.new_content_flag == 1:
                for article_url in response.css('.modules-grid section::attr("data-href")').extract():
                    if not (article_url in self.post_urls):
                        self.post_urls.append(article_url)
                        yield response.follow(article_url, callback=self.parse_article)
                    else:
                        self.new_content_flag = 0

                url_repo_id = local_item['_id']
                self.url_repository.update_one({'_id': url_repo_id},{'$set': {'post_urls_repo3': self.post_urls}})

        else:
            for article_url in response.css('.modules-grid section::attr("data-href")').extract():
                if not (article_url in self.post_urls):
                    self.post_urls.append(article_url)
                    yield response.follow(article_url, callback=self.parse_article)

            included_posts = {'post_urls_repo3': self.post_urls}
            self.url_repository.insert_one(included_posts)

    def parse_article(self, response):
        title = response.css('.post-title::text').extract()
        date = response.css('.localtime::text').extract()
        date_after_format = str(date[0])
        date_after_format = re.match(r'(.+?)(?=,\s\d+[:])', date_after_format)
        date_after_format = date_after_format.group(0)
        article = response.css('.post-content p::text, .post-content a::text, .post-content b::text,.post-content i::text,.post-content strong::text').extract()
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

# Spider Class for https://mixmag.net domain monitoring(Pagination Trouble)


class ArticleSpider7(scrapy.Spider):
    name = "article"
    allowed_domains = ['mixmag.net']
    start_urls = ['https://mixmag.net/music']
    post_urls = []
    new_content_flag = 1
    client = MongoClient('mongodb://localhost:27017')
    db = client['Articles_DB']
    articles = db.articles7
    url_repository = db.urls
    repo_existence_check = 0

    def parse(self, response):
        urls_repo_cursor = self.url_repository.find()
        for item in urls_repo_cursor:
            if '_id' and 'post_urls_repo7' in item:
                self.repo_existence_check += 1
                local_item = item

        if self.repo_existence_check == 0:
            for article_url in response.css('.story-block a::attr("href")').extract():
                if not (article_url in self.post_urls):
                    self.post_urls.append(article_url)
                    yield response.follow(article_url, callback=self.parse_article)

            included_posts = {'post_urls_repo7': self.post_urls}
            self.url_repository.insert(included_posts)

        else:
            self.post_urls = local_item['post_urls_repo7']

            if self.new_content_flag == 1:
                for article_url in response.css('.story-block a::attr("href")').extract():
                    if not (article_url in self.post_urls):
                        self.post_urls.append(article_url)
                        yield response.follow(article_url, callback=self.parse_article)
                    else:
                        self.new_content_flag = 0

                url_repo_id = local_item['_id']
                self.url_repository.update({'_id': url_repo_id}, {'$set': {'post_urls_repo7': self.post_urls}})


    def parse_article(self, response):
        title = response.css('h1::text').extract()
        date = response.css('.article-header__meta li::text').extract()
        article = response.xpath('//*[@id="js-infinity"]/article/div[2]/div[1]/div[1]/div[1]//text()').extract()
        if not article:
            article = response.xpath('//*[@class="copy rich-text__block"]//text()').extract()
        if not article:
            article = response.xpath('//*[@class="copy rich-text__block rich-text__block--centre"]//text()').extract()
        post_link = str(response)
        post_link = post_link.strip('<200 ')
        post_link = post_link.strip('>')
        post = {'title': ''.join(title),
                'date': ''.join(date[1]),
                'article': ''.join(article),
                'post-link': post_link}
        self.articles.insert(post)

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




if __name__ == "__main__":
    process = CrawlerProcess()
    # process.crawl(ArticleSpider1)
    # process.crawl(ArticleSpider2)
    # process.crawl(ArticleSpider3)
    # process.crawl(ArticleSpider4)
    # process.crawl(ArticleSpider5)
    # process.crawl(ArticleSpider6)
    # process.crawl(ArticleSpider7)
    # process.crawl(ArticleSpider8)
    # process.crawl(ArticleSpider9)
    # process.crawl(ArticleSpider10)
    # process.crawl(ArticleSpider11)
    # process.crawl(ArticleSpider12)
    process.start()

