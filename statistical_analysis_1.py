# Import packages
from pymongo import MongoClient
import matplotlib.pyplot as plt
import numpy as np
import re

# Simple statistical analysis class for the following metrics:
# 1) Number of characters per article title
# 2) Number of words per article title
# 3) Number of characters per article
# 4) Number of words per article


class StatisticalAnalysis:
    client = MongoClient('mongodb://localhost:27017')
    db = client['Articles_DB']
    articles_conn = list()
    articles_count = 0
    term_freq = {}
    metrics_data = list()

    # Find all article collections in the MongoDB
    def find_all_article_collections(self):
        collections = self.db.list_collection_names()
        if 'urls' in collections:
            collections.remove('urls')
        self.articles_conn = collections

    # Calculate the desired article metrics
    def calculate_article_metrics(self):
        for collection in self.articles_conn:
            articles = list(self.db.get_collection(collection).find())
            self.articles_count = len(articles)

            total_title_characters = int()
            total_title_words = int()
            total_article_chars = int()
            total_article_words = int()

            for article in articles:

                article_title = article['title']
                article_body = article['article']

                # Calculate number of characters/words per article title
                title_chars_number = len(str(article_title).replace(' ', ''))
                title_words_list = str(article_title).split(' ')
                title_words_number = len(title_words_list)
                total_title_characters += title_chars_number
                total_title_words += title_words_number

                # Calculate article number of characters/words
                article_chars_number = len(str(article_body).replace(' ', ''))
                article_words_list = article_body.split(' ')
                article_words_number = len(article_words_list)
                total_article_chars += article_chars_number
                total_article_words += article_words_number

            # Get average metrics for the whole blog collection
            average_title_characters = int(total_title_characters / self.articles_count)
            average_title_words = int(total_title_words / self.articles_count)
            average_article_chars = int(total_article_chars / self.articles_count)
            average_article_words = int(total_article_words / self.articles_count)

            stats = [average_title_characters, average_title_words,
                     average_article_chars, average_article_words]

            self.metrics_data.append(stats)

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

    # Fill the term freq dictionary function
    def populate_term_freq_dict(self, wordslist, termslist):
        for word in wordslist:
            if word in termslist:
                try:
                    self.term_freq[word] += 1
                except:
                    self.term_freq.update({word: 1})

    # Create metrics histograms
    def create_histograms(self):
        fig = plt.figure()
        ax1 = fig.add_subplot(2, 1, 1)
        ax2 = fig.add_subplot(2, 1, 2)
        fig2 = plt.figure()
        ax3 = fig2.add_subplot(2, 1, 1)
        ax4 = fig2.add_subplot(2, 1, 2)

        Average_title_chars = list()
        for listitem in self.metrics_data:
            Average_title_chars.append(listitem[0])
        Average_title_chars = np.asarray(Average_title_chars)
        n, bins, patches = ax1.hist(Average_title_chars, histtype='bar', label=['Characters'])
        ax1.set_ylabel('Frequency')
        ax1.set_xlabel('Average article title chars distribution')
        ax1.legend(loc="upper right")

        Average_title_words = list()
        for listitem in self.metrics_data:
            Average_title_words.append(listitem[1])
        Average_title_words = np.asarray(Average_title_words)
        n, bins, patches = ax2.hist(Average_title_words, histtype='bar', label=['Words'])
        ax2.set_ylabel('Frequency')
        ax2.set_xlabel('Average article title words distribution')
        ax2.legend(loc="upper right")

        Average_article_chars = list()
        for listitem in self.metrics_data:
            Average_article_chars.append(listitem[2])
        Average_article_chars = np.asarray(Average_article_chars)
        n, bins, patches = ax3.hist(Average_article_chars, histtype='bar', label=['Characters'])
        ax3.set_ylabel('Frequency')
        ax3.set_xlabel('Average article chars distribution')
        ax3.legend(loc="upper right")

        Average_article_words = list()
        for listitem in self.metrics_data:
            Average_article_words.append(listitem[3])
        Average_article_words = np.asarray(Average_article_words)
        n, bins, patches = ax4.hist(Average_article_words, histtype='bar', label=['Words'])
        ax4.set_ylabel('Frequency')
        ax4.set_xlabel('Average article words distribution')
        ax4.legend(loc="upper right")

        plt.show()


if __name__ == "__main__":
    stat = StatisticalAnalysis()
    stat.find_all_article_collections()
    stat.calculate_article_metrics()
    stat.create_histograms()
    # stat.analyse_site_activity()
    # stat.calculate_genres_frequency()
