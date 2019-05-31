# Import packages
from pymongo import MongoClient
import re

# Simple statistical analysis class for the following metrics:
# 1) Number of characters per article title
# 2) Number of words per article title
# 3) Number of characters per article
# 4) Number of words per article


class StatisticalAnalysis:
    client = MongoClient('mongodb://localhost:27017')
    db = client['Articles_DB']
    articles_conn = db.articles11
    articles_count = 0
    term_freq = {}
    total_title_characters = 0
    total_title_words = 0
    total_article_chars = 0
    total_article_words = 0
    average_title_characters = int()
    average_title_words = int()
    average_article_chars = int()
    average_article_words = int()

    # Calculate the desired article metrics
    def calculate_article_metrics(self):
        articles = list(self.articles_conn.find())
        self.articles_count = len(articles)

        for article in articles:

            article_title = article['title']
            article_body = article['article']

            # Calculate number of characters/words per article title
            title_chars_number = len(str(article_title).replace(' ', ''))
            title_words_list = str(article_title).split(' ')
            title_words_number = len(title_words_list)
            self.total_title_characters += title_chars_number
            self.total_title_words += title_words_number

            # Calculate article number of characters/words
            article_chars_number = len(str(article_body).replace(' ', ''))
            article_words_list = article_body.split(' ')
            article_words_number = len(article_words_list)
            self.total_article_chars += article_chars_number
            self.total_article_words += article_words_number

        # Get average metrics for the whole blog collection
        self.average_title_characters = int(self.total_title_characters / self.articles_count)
        self.average_title_words = int(self.total_title_words / self.articles_count)
        self.average_article_chars = int(self.total_article_chars / self.articles_count)
        self.average_article_words = int(self.total_article_words / self.articles_count)
        print(self.average_title_characters)
        print(self.average_title_words)
        print(self.average_article_chars)
        print(self.average_article_words)

    # Calculate number of articles per day
    def analyse_site_activity(self):
        articles = list(self.articles_conn.find())
        self.articles_count = len(articles)
        dates_dict = {}

        for article in articles:
            article_date = article['date']
            try:
                posts_on_date = int(dates_dict.get(article_date))
                posts_on_date += 1
                dates_dict.update({article_date: posts_on_date})
            except:
                dates_dict[article_date] = 1
        print(dates_dict)

    # Calculate the frequency of appearance for the different music genres
    def calculate_genres_frequency(self):
        with open('genre_list.txt') as gf:
            genres_list = gf.readlines()
        for gen in genres_list:
            index = genres_list.index(gen)
            if gen.endswith('\n'):
                genres_list[index] = re.sub(r'[\n\r]+$', '', gen)

        # Load all articles and calculate term appearance frequency
        articles = list(self.articles_conn.find())
        self.articles_count = len(articles)

        for article in articles:
            article_body = article['article']
            words_list = article_body.split(' ')
            self.populate_term_freq_dict(words_list, genres_list)

        print(self.term_freq)

    def populate_term_freq_dict(self, wordslist, termslist):
        for word in wordslist:
            if word in termslist:
                try:
                    self.term_freq[word] += 1
                except:
                    self.term_freq.update({word: 1})


if __name__ == "__main__":
    stat = StatisticalAnalysis()
    stat.calculate_article_metrics()
    stat.analyse_site_activity()
    stat.calculate_genres_frequency()
