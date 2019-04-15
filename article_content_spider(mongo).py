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
            if next_page.status_code == 200:
                print('Web site exists')
                next_page_link = (self.core_link + str(self.page_id))
                self.page_id += 1
                yield response.follow(next_page_link, callback=self.parse)
            else:
                included_posts = {'post_urls_repo1': self.post_urls}
                self.url_repository.insert(included_posts)

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
                self.url_repository.update({'_id': url_repo_id}, {'$set': {'post_urls_repo1': self.post_urls}})
                next_page = requests.get(self.core_link + str(self.page_id))

                if next_page.status_code == 200:
                    print('Web site exists')
                    next_page_link = (self.core_link + str(self.page_id))
                    self.page_id += 1
                    yield response.follow(next_page_link, callback=self.parse)

                else:
                    url_repo_id = local_item['_id']
                    self.url_repository.update({'_id': url_repo_id}, {'$set': {'post_urls_repo1': self.post_urls}})

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
        self.articles.insert(post)


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
                self.url_repository.update({'_id': url_repo_id}, {'$set': {'post_urls_repo2': self.post_urls}})

                next_page = requests.get(self.core_link + str(self.page_id))
                if next_page.status_code == 200:
                    print('Web site exists')
                    next_page_link = (self.core_link + str(self.page_id))
                    self.page_id += 1
                    yield response.follow(next_page_link, callback=self.parse)
                else:
                    url_repo_id = local_item['_id']
                    self.url_repository.update({'_id': url_repo_id},{'$set': {'post_urls_repo2': self.post_urls}})
        else:
            for article_url in response.css('.grid__wrapper a::attr("href")').extract():
                self.post_urls.append(article_url)
                yield response.follow(article_url, callback=self.parse_article)

            next_page = requests.get(self.core_link + str(self.page_id))
            if next_page.status_code == 200:
                print('Web site exists')
                next_page_link = (self.core_link + str(self.page_id))
                self.page_id += 1
                yield response.follow(next_page_link, callback=self.parse)
            else:
                included_posts = {'post_urls_repo2': self.post_urls}
                self.url_repository.insert(included_posts)

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
        self.articles.insert(post)


# Spider class for https://consequenceofsound.net/ domain monitoring


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
                self.url_repository.update({'_id': url_repo_id},{'$set': {'post_urls_repo3': self.post_urls}})

        else:
            for article_url in response.css('.modules-grid section::attr("data-href")').extract():
                if not (article_url in self.post_urls):
                    self.post_urls.append(article_url)
                    yield response.follow(article_url, callback=self.parse_article)

            included_posts = {'post_urls_repo3': self.post_urls}
            self.url_repository.insert(included_posts)

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
        self.articles.insert(post)

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
            if next_page.status_code == 200 :
                print('Web site exists')
                next_page_link = (self.core_link + str(self.page_id))
                self.page_id += 1
                yield response.follow(next_page_link, callback=self.parse)
            else:
                included_posts = {'post_urls_repo4': self.post_urls}
                self.url_repository.insert(included_posts)

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
                self.url_repository.update({'_id': url_repo_id}, {'$set': {'post_urls_repo4': self.post_urls}})

                next_page = requests.get(self.core_link + str(self.page_id))
                if next_page.status_code == 200:
                    print('Web site exists')
                    next_page_link = (self.core_link + str(self.page_id))
                    self.page_id += 1
                    yield response.follow(next_page_link, callback=self.parse)
                else:
                    url_repo_id = local_item['_id']
                    self.url_repository.update({'_id': url_repo_id}, {'$set': {'post_urls_repo4': self.post_urls}})

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
            self.articles.insert(post)

if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(ArticleSpider1)
    #process.crawl(ArticleSpider2)
    #process.crawl(ArticleSpider3)
    #process.crawl(ArticleSpider4)
    process.start()

