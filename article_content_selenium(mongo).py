# Importing packages

from selenium import webdriver
from pymongo import MongoClient
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Selenium Class for https://ukf.com domain monitoring


class ArticleSelenium:
    client = MongoClient('mongodb://localhost:27017')
    db = client['Articles_DB']
    articles = db.articles39
    url_repository = db.urls
    repo_existence_check = 0
    new_content_flag = 1
    start_url = "https://ukf.com/news"
    option = webdriver.ChromeOptions()
    option.add_argument("--incognito")
    post_urls = []
    bool_flag = True

    def parse(self):
        browser = webdriver.Chrome(executable_path='chromedriver.exe', options=self.option)
        browser.get(self.start_url)

        urls_repo_cursor = self.url_repository.find()
        for item in urls_repo_cursor:
            if '_id' and 'post_urls_repo39' in item:
                self.repo_existence_check += 1
                local_item = item

        if self.repo_existence_check == 0:

            # Parse and extract page articles function call
            self.parse_articles(browser)

            # Check if there more posts available and parse them
            while self.bool_flag:
                try:
                    next_page_element = browser.find_element_by_xpath('//*[@id="primary"]/div/a')
                    next_page_link = next_page_element.get_attribute('href')
                    browser.get(next_page_link)
                    self.parse_articles(browser)
                except:
                    self.bool_flag = False
                    browser.quit()
                    included_posts = {'post_urls_repo39': self.post_urls}
                    self.url_repository.insert_one(included_posts)
        else:
            self.post_urls = local_item['post_urls_repo39']

            # Parse and extract page articles function call
            self.parse_articles(browser)

            while self.new_content_flag == 1:

                # Check if there more posts available and parse them
                while self.bool_flag:
                    try:
                        next_page_element = browser.find_element_by_xpath('//*[@id="primary"]/div/a')
                        next_page_link = next_page_element.get_attribute('href')
                        browser.get(next_page_link)
                        self.parse_articles(browser)
                        url_repo_id = local_item['_id']
                        self.url_repository.update_one({'_id': url_repo_id},
                                                       {'$set': {'post_urls_repo39': self.post_urls}})
                    except:
                        self.bool_flag = False
                        self.new_content_flag = 0
                        browser.quit()
                        url_repo_id = local_item['_id']
                        self.url_repository.update_one({'_id': url_repo_id},
                                                       {'$set': {'post_urls_repo39': self.post_urls}})

    # Parse and extract articles per page function
    def parse_articles(self, browser):
        articles_urls_element = browser.find_elements_by_xpath('// *[ @ id = "main"] / div / '
                                                               'div / div / div[3] / a')
        page_urls = []
        new_urls = []

        for url_elem in articles_urls_element:
            page_urls.append(url_elem.get_attribute('href'))

        for link in page_urls:
            if link not in self.post_urls:
                self.post_urls.append(link)
                new_urls.append(link)

        # Get article title,date and content
        if len(new_urls) > 0:
            for url in new_urls:
                browser_next_post = webdriver.Chrome(executable_path='chromedriver.exe', options=self.option)
                browser_next_post.get(url)

                try:
                    # Get article title
                    title_element = browser_next_post.find_element_by_xpath('//*/header/h1')
                    title = title_element.text
                    # Get article date
                    date_element = browser_next_post.find_element_by_xpath('//*/header/div/span[2]/a/time')
                    date = date_element.text
                    # Get article content
                    article_element = browser_next_post.find_elements_by_xpath('//*/div[2]/p')
                    article = str()
                    for paragraph in article_element:
                        article += paragraph.text
                    post = {'title': ''.join(title),
                            'date': ''.join(date),
                            'article': ''.join(article),
                            'post-link': url}
                    self.articles.insert_one(post)
                    print(post)
                    browser_next_post.quit()
                except:
                    browser_next_post.quit()
        else:
            self.new_content_flag = 0

# Selenium Class for https://consequenceofsound.net domain monitoring


class ArticleSelenium2:
    client = MongoClient('mongodb://localhost:27017')
    db = client['Articles_DB']
    articles = db.articles40
    url_repository = db.urls
    repo_existence_check = 0
    new_content_flag = 1
    start_url = "https://consequenceofsound.net/category/check-out/"
    option = webdriver.ChromeOptions()
    option.add_argument("--incognito")
    prefs = {'profile.managed_default_content_settings.images': 2}
    option.add_experimental_option("prefs", prefs)
    post_urls = []
    bool_flag = True
    scraped_articles = 0

    def parse(self):
        browser = webdriver.Chrome(executable_path='chromedriver.exe', options=self.option)
        browser.get(self.start_url)

        urls_repo_cursor = self.url_repository.find()
        for item in urls_repo_cursor:
            if '_id' and 'post_urls_repo40' in item:
                self.repo_existence_check += 1
                local_item = item

        if self.repo_existence_check == 0:

            # Parse and extract page articles function call
            self.parse_articles(browser)

            # Check if there more posts available and parse them
            while self.bool_flag:
                try:
                    button = browser.find_elements(By.XPATH, '//*[@id="infinite-handle"]/span/button')
                    self.option.add_experimental_option("detach", True)
                    button[0].click()
                    # Wait 10 seconds for page to load
                    timeout = 10
                    WebDriverWait(browser, timeout).until(EC.presence_of_element_located((By.XPATH, '//*[@id="infinite-handle"]/span/button')))
                    self.parse_articles(browser)
                except:
                    self.bool_flag = False
                    browser.quit()
                    included_posts = {'post_urls_repo40': self.post_urls}
                    self.url_repository.insert_one(included_posts)
        else:
            self.post_urls = local_item['post_urls_repo40']

            # Parse and extract page articles function call
            self.parse_articles(browser)

            while self.new_content_flag == 1:

                # Check if there more posts available and parse them
                while self.bool_flag:
                    try:
                        button = browser.find_elements(By.XPATH, '//*[@id="infinite-handle"]/span/button')
                        self.option.add_experimental_option("detach", True)
                        button[0].click()
                        # Wait 10 seconds for page to load
                        timeout = 10
                        WebDriverWait(browser, timeout).until(
                            EC.presence_of_element_located((By.XPATH, '//*[@id="infinite-handle"]/span/button')))
                        self.parse_articles(browser)
                        url_repo_id = local_item['_id']
                        self.url_repository.update_one({'_id': url_repo_id},
                                                       {'$set': {'post_urls_repo40': self.post_urls}})
                    except:
                        self.bool_flag = False
                        self.new_content_flag = 0
                        browser.quit()
                        url_repo_id = local_item['_id']
                        self.url_repository.update_one({'_id': url_repo_id},
                                                       {'$set': {'post_urls_repo40': self.post_urls}})

    # Parse and extract articles per page function
    def parse_articles(self, browser):
        articles_urls_element = browser.find_elements_by_xpath('//*[@id="tab-everything"]/section/div/h1/a')
        page_urls = []

        # Gather all articles links in a temp list
        for url_elem in articles_urls_element:
            page_urls.append(url_elem.get_attribute('href'))

        # Insert every link at the mongo db posts urls dict/Filter out duplicates caused from the click event
        for link in page_urls:
            self.post_urls.append(link)

        for url in self.post_urls:
            if self.post_urls.count(url) > 1 and url in page_urls:
                page_urls.remove(url)
                self.post_urls.remove(url)

        # Parse and extract all posts that haven't been extracted
        if len(page_urls) > 0:
            print(page_urls)
            for article_link in page_urls:

                # Get article title,date and content
                browser_next_post = webdriver.Chrome(executable_path='chromedriver.exe', options=self.option)
                browser_next_post.get(article_link)

                try:
                    # Get article title
                    title_element = browser_next_post.find_element_by_xpath('//*[@id="viewport-wrapper"]/div[4]/h1')
                    title = title_element.text

                    # Get article date
                    date_element = browser_next_post.find_element_by_xpath('//*[@id="viewport-wrapper"]/div[4]'
                                                                           '/section/div[1]/div[2]/span')
                    date = date_element.text
                    # Get article content
                    article_element = browser_next_post.find_elements_by_xpath('//*[@id="main-content"]/div/article/p')
                    article = str()
                    for paragraph in article_element:
                        article += paragraph.text
                    post = {'title': ''.join(title),
                            'date': ''.join(date),
                            'article': ''.join(article),
                            'post-link': article_link}
                    self.articles.insert_one(post)
                    print(post)
                    browser_next_post.quit()
                except:
                    browser_next_post.quit()
        else:
            self.new_content_flag = 0
            self.bool_flag = False


if __name__ == '__main__':
    # selenium_domain_1 = ArticleSelenium()
    # selenium_domain_1.parse()
    selenium_domain_2 = ArticleSelenium2()
    selenium_domain_2.parse()
