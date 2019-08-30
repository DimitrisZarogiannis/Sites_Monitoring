# Import packages
from __future__ import unicode_literals, print_function
from pymongo import MongoClient
import matplotlib.pyplot as plt
plt.rcdefaults()
import numpy as np
import datetime
import re
from matplotlib.ticker import MaxNLocator
import pendulum
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


plt.style.use('seaborn')

# Imports to train Spacy's NER Model
import plac
import random
from pathlib import Path
import spacy
from spacy.util import minibatch, compounding
import os
from spacy.gold import GoldParse
from spacy.scorer import Scorer


# Simple statistical analysis class for the following metrics:
# 1) Number of characters per article title
# 2) Number of words per article title
# 3) Number of characters per article
# 4) Number of words per article
# 5) Genres terms frequency
# 6) Sites activity monitoring
# 7) NER for "Artist" classes


class StatisticalAnalysis:
    client = MongoClient('mongodb://localhost:27017')
    db = client['Articles_DB']
    genres_term_frequency = db.genres
    blogs_activity = db.blogs_activity
    ent_db = db.entities
    articles_conn = list()
    articles_count = 0
    term_freq = {}
    terms_dates = []
    genre_posts_no = 0
    metrics_data = list()
    outliers = []
    entities = {}

    # Find all article collections in the MongoDB
    def find_all_article_collections(self):
        collections = self.db.list_collection_names()
        if 'urls' in collections:
            collections.remove('urls')
        if 'genres' in collections:
            collections.remove('genres')
        if 'blogs_activity' in collections:
            collections.remove('blogs_activity')
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

            # Metrics per article collection
            collection_metrics_data = list()

            for article in articles:

                article_title = article['title']
                article_body = article['article']
                link = article['post-link']

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

                # Find outlier articles
                if article_chars_number > 6000:
                    self.outliers.append([collection, link])

                article_stats = [title_chars_number, title_words_number,
                                 article_chars_number, article_words_number]

                collection_metrics_data.append(article_stats)

            # Create Histogram for every collection's metrics/per article
            self.create_collection_histograms(collection, collection_metrics_data)

            self.metrics_data = self.metrics_data + collection_metrics_data

        outlier_collections = {}
        for item in self.outliers:
            if item[0] in outlier_collections:
                outlier_collections[item[0]] += 1
            else:
                outlier_collections[item[0]] = 1

        print('Collections with outliers are : {}'.format(outlier_collections))

    # Calculate number of articles per day
    def analyse_site_activity(self):
        for collection in self.articles_conn:
            articles = list(self.db.get_collection(collection).find())
            dates_dict = {}

            for article in articles:
                article_date = article['date']
                article_date = re.sub(r"[^a-zA-Z0-9- ]", "", article_date)
                article_date = article_date.strip(' ')
                if stat.checktype1(article_date):
                    article_date = stat.checktype1(article_date)
                elif stat.checktype2(article_date):
                    article_date = stat.checktype2(article_date)
                elif stat.checktype3(article_date):
                    article_date = stat.checktype3(article_date)
                elif stat.checktype4(article_date):
                    article_date = stat.checktype4(article_date)
                elif stat.checktype5(article_date):
                    article_date = stat.checktype5(article_date)
                if article_date:
                    try:
                        posts_on_date = int(dates_dict.get(article_date))
                        posts_on_date += 1
                        dates_dict.update({article_date: posts_on_date})
                    except:
                        dates_dict[article_date] = 1
            # if len(dates_dict) > 0:
            #     self.blogs_activity.insert_one({'site_activity': [dates_dict, collection]})
        self.create_timelines()

    # Create latest month's blog activity timelines
    def create_timelines(self):
        activity_items = self.blogs_activity.find()
        data = []
        collections = []
        collections_info = []
        for ai in activity_items:
            timeline_data = []
            collections.append(ai['site_activity'][1])
            activity_dict = ai['site_activity'][0]
            dates_list = list(activity_dict.keys())
            latest_year = self.find_latest_year(dates_list)
            latest_months = self.find_3_latest_months(dates_list, latest_year)
            for month in latest_months:
                timeline_data.append(sorted(self.find_timeline_data(dates_list, month,
                                                                    latest_year, activity_dict), key=lambda x:x[0]))
            data.append(timeline_data)
            collections_info.append([latest_year, latest_months])

        for d in data:
            collection = collections[data.index(d)]
            info = collections_info[data.index(d)]
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.set_xlim(1, 31)
            plt.xlabel('Dates')
            plt.ylabel('Number of Posts')
            plt.grid()
            for month in d:
                x = [dt[0] for dt in month]
                y = [dt[1] for dt in month]
                ax.plot(x, y, '-8', label=str(info[1][d.index(month)]) + ' \\ '+str(info[0]))
            plt.legend()
            plt.title('Collection : {}'.format(collection))
            plt.savefig(str(str(collection)+'.png'), dpi=300)
        plt.show()

    # Find collection's latest post year
    def find_latest_year(self, dates_list):
        latest_year = int()
        try:
            for post_date in dates_list:
                post_year = int(post_date[0:4])
                if post_year > latest_year:
                    latest_year = post_year
            return latest_year
        except:
            return None

    # Find collection's latest post month
    def find_3_latest_months(self, dates, lyear):
        latest_months = list()
        try:
            for post_date in dates:
                post_year = int(post_date[0:4])
                post_month = int(post_date[5:7])
                if post_year == lyear and (post_month not in latest_months):
                    latest_months.append(int(post_month))
            latest_months.sort(reverse=True)
            return latest_months[0:3]
        except:
            return None

    # Find collection's latest month timeline data
    def find_timeline_data(self, dates, month, year, activity):
        timeline_dates = []
        timeline_activity_data = []
        for post_date in dates:
            post_year = int(post_date[0:4])
            post_month = int(post_date[5:7])
            if post_year == year and post_month == month:
                timeline_dates.append(post_date)
        for date in timeline_dates:
            timeline_activity_data.append((int(date[8:]), activity[date]))
        return timeline_activity_data

    # Find collection's latest month timeline data by week number
    def find_timeline_data_2(self, dates, month, year, activity):
        timeline_dates = []
        timeline_activity_data = []
        for post_date in dates:
            post_year = int(post_date[0:4])
            post_month = int(post_date[5:7])
            if post_year == year and post_month == month:
                timeline_dates.append(post_date)
        for date in timeline_dates:
            timeline_activity_data.append([date, activity[date]])
        return timeline_activity_data

    # Check if date is of type MM DD YY
    def checktype1(self, datestring):
        regex = r'\w+\s\d+\s\d+'
        match = re.match(regex, datestring)
        if match:
            try:
                date = datetime.datetime.strptime(match.group(0), '%B %d %Y').date()
                return str(date)
            except:
                date = datetime.datetime.strptime(match.group(0), '%b %d %Y').date()
                return str(date)
        else:
            return None

    # Check if date is of type DD MM YY
    def checktype2(self, datestring):
        regex = r'\d+\s\w+\s\d+'
        match = re.match(regex, datestring)
        if match:
            try:
                date = datetime.datetime.strptime(match.group(0), '%d %B %Y').date()
                return str(date)
            except:
                return None
        else:
            return None

    # Check if date is of type DDMMYY
    def checktype3(self, datestring):
        split_string = datestring[0:2] + ' ' + datestring[2:5] + ' ' + datestring[5:]
        regex = r'\d+\s\w+\s\d+'
        match = re.match(regex, split_string)
        if match:
            try:
                date = datetime.datetime.strptime(match.group(0), '%d %b %Y').date()
                return str(date)
            except:
                return None
        else:
            return None

    # Check if date containts th,rd,nd,st
    def checktype4(self, datestring):
        date_endings = ['th', 'rd', 'nd', 'st']
        regex = r'\w+\s\d+\w+\s\d+'
        match = re.match(regex, datestring)
        split_string = str(datestring).split(' ')
        if match:
            try:
                for ending in date_endings:
                    split_string[1] = str(split_string[1]).replace(ending, '')
                datestring = ' '.join(split_string)
                date = datetime.datetime.strptime(datestring, '%B %d %Y').date()
                return str(date)
            except:
                return None
        else:
            return None

    # Check if date has no spaces and is of type ex. 05282019
    def checktype5(self, datestring):
        split_string = datestring[0:2] + ' ' + datestring[2:4] + ' ' + datestring[4:]
        regex = r'\d+\s\d+\s\d+'
        match = re.match(regex, split_string)
        if match:
            try:
                date = datetime.datetime.strptime(match.group(0), '%m %d %Y').date()
                return str(date)
            except:
                return None
        else:
            return None

    # Calculate the frequency of appearance for the different music genres
    def calculate_genres_frequency(self):
        with open('genre_list.txt') as gf:
            genres_list = gf.readlines()
        for gen in genres_list:
            index = genres_list.index(gen)
            if gen.endswith('\n'):
                genres_list[index] = re.sub(r'[\n\r]+$', '', gen).lower()

        self.terms_dates = [{} for _ in range(len(genres_list))]

        # Load all collection's articles and calculate term appearance frequency
        for collection in self.articles_conn:
            collection_tf_data = [0] * len(genres_list)
            articles = list(self.db.get_collection(collection).find())
            count = len(articles)
            terms_dict = dict()

            for article in articles:
                article_date = article['date']
                article_date = re.sub(r"[^a-zA-Z0-9- ]", "", article_date)
                article_date = article_date.strip(' ')
                if stat.checktype1(article_date):
                    article_date = stat.checktype1(article_date)
                elif stat.checktype2(article_date):
                    article_date = stat.checktype2(article_date)
                elif stat.checktype3(article_date):
                    article_date = stat.checktype3(article_date)
                elif stat.checktype4(article_date):
                    article_date = stat.checktype4(article_date)
                elif stat.checktype5(article_date):
                    article_date = stat.checktype5(article_date)
                else:
                    article_date = None
                article_body = article['article']
                article_body = re.sub(r'[^\w\d\s]+', ' ', article_body)
                words_list = article_body.split(' ')
                words_list = [str(w).lower() for w in words_list]
                # Calculate genre's terms frequency for every collection
                for word in words_list:
                    if word in genres_list:
                        index = genres_list.index(word)
                        collection_tf_data[index] += 1

                # Calculates the number of posts with at least 1 genre-term
                self.find_posts_mentioning_genres(words_list, genres_list)

                # Calculate terms total appearance frequencies
                if article_date:
                    self.populate_term_freq_dict(words_list, genres_list, article_date)

                self.populate_term_freq_dict2(words_list, genres_list, terms_dict)

            # Normalization of all the genre terms counts
            terms_dict = {k: v / count for k, v in terms_dict.items()}

            for k, v in terms_dict.items():
                try:
                    self.term_freq[k] += round(v, 2)
                except:
                    self.term_freq.update({k: round(v, 2)})

            # Create Bar Charts for every collection's term frequency data
            genres = []
            f_values = []
            for tf in collection_tf_data:
                if tf > 0:
                    index = collection_tf_data.index(tf)
                    genres.append(genres_list[index])
                    f_values.append(tf)

            y_pos = np.arange(len(genres))
            plt.bar(y_pos, f_values, align='center', alpha=0.5)
            plt.xticks(y_pos, genres, rotation=90)
            plt.ylabel('Frequency')
            plt.xlabel('Genres')
            plt.title('Collection : {}'.format(collection))
            plt.tight_layout()
            plt.savefig(str(str(collection) + '_bc' + '.png'))
            plt.show()

        # Insert total genre term frequencies data for all the collections
        self.genres_term_frequency.insert_one({'item1': self.term_freq})

        self.create_normalized_bc()

        # Insert total genres tf time-series data for all collections // Create tf time-series diagrams
        timeseries_data = list(map(lambda x, y: [x, y], genres_list, self.terms_dates))
        self.genres_term_frequency.insert_one({'item': timeseries_data})
        self.create_tf_timelines()

        print('Number of posts containing at least 1 genre term: {}'.format(self.genre_posts_no))

    # Create TF Bar-Chart from the total dataset terms data
    def create_normalized_bc(self):
        collect = len(self.articles_conn)
        genres_data = self.genres_term_frequency.find()
        bc_data = dict()
        for item in genres_data:
            try:
                bc_data = item['item1']
            except:
                continue

        genres = list(dict(bc_data).keys())
        norm_values = list()

        for genre in genres:
            norm_values.append(round(bc_data[genre]/collect, 2))

        y_pos = np.arange(len(genres))
        plt.bar(y_pos, norm_values, align='center', alpha=0.5)
        plt.xticks(y_pos, genres, rotation=90)
        plt.ylabel('Frequency')
        plt.xlabel('Genres')
        plt.title('Articles Dataset')
        plt.tight_layout()
        plt.savefig('dataset_terms_bc' + '.png')
        plt.show()

    # Create Music-Genres TF time-series for the latest 3 months of data
    def create_tf_timelines(self):
        genres_data = self.genres_term_frequency.find()
        timeseries_data = genres_data[1]['item']
        plot_data = []
        genres_info = []
        genres = []
        for genre_tf in timeseries_data:
            genre_plot_data = []
            genre = genre_tf[0]
            dates_list = list(genre_tf[1].keys())
            latest_year = self.find_latest_year(dates_list)
            latest_months = sorted(self.find_3_latest_months(dates_list, latest_year), reverse=False)
            for month in latest_months:
                genre_plot_data.append(sorted(self.find_timeline_data_2(dates_list, month,
                                                                        latest_year, genre_tf[1]), key=lambda x:x[0]))
            genre_plot_data = self.td_concat(genre_plot_data)
            if len(genre_plot_data) > 0:
                plot_data.append(genre_plot_data)
                genres.append(genre)
                genres_info.append([latest_year, latest_months])

        for d in plot_data:
            genre = genres[plot_data.index(d)]
            info = genres_info[plot_data.index(d)]
            year = info[0]
            months_numbers = info[1]
            months = list()
            months_weeks = list()
            plot_range = list()
            if len(months_numbers) > 0:
                for m in months_numbers:
                    month_obj = datetime.datetime(2019, int(m), 5)
                    month_name = month_obj.strftime('%b')
                    months.append(month_name)

            for month in months_numbers:
                weeks = self.year_weeks(year, month)
                for week in weeks:
                    plot_range.append(week)
                months_weeks.append(weeks)

            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.set_xlim(plot_range[0], plot_range[-1])
            ax.yaxis.set_major_locator(MaxNLocator(nbins=10, min_n_ticks=1, integer=True))
            ax.xaxis.set_major_locator(MaxNLocator(nbins=15, min_n_ticks=1, integer=True))
            plt.xlabel('Weeks of year')
            plt.ylabel('Number of Posts')
            plt.setp(ax.get_xticklabels(), rotation=45)
            x = [int(dt[0]) for dt in d]
            y = [dt[1] for dt in d]
            ax.plot(x, y, '-8')
            x_ticks = list()
            for mw in months_weeks:
                tick = sum(mw)/len(mw)
                x_ticks.append(int(tick))
            ax.set_xticks(x_ticks, minor=True)
            ax.tick_params(which='minor', length=0, labelsize=12, pad=25)
            ax.tick_params(which='major', length=0)
            ax.set_xticklabels(months, minor=True)
            plt.title('Genre Term : {}\n Months : {} / {}'.format(genre, ', '.join(months), year))
            plt.savefig(str(str(genre)+'.png'), bbox_inches='tight')
        plt.show()

    # Concatenate the time-series data for every month /  Returns total terms appearance data per week of the year
    def td_concat(self, plotdata):
        total_data = list()
        week_data = list()
        for md in plotdata:
            for dlist in md:
                dt = pendulum.parse(dlist[0])
                new_list = [dt, dlist[1]]
                total_data.append(new_list)
        for dt in total_data:
            week = self.same_week(dt, total_data)
            week_data.append(week)
        for item in week_data:
            while week_data.count(item) > 1:
                week_data.remove(item)
        return week_data

    # Finds and saves all the terms-appearances for a given week
    def same_week(self, date1, datelist):
        week_days = []
        counter = int()
        woy = date1[0].week_of_year
        for date2 in datelist:
            dt2 = date2[0].week_of_year
            dt1 = date1[0].week_of_year
            if dt2 is dt1:
                week_days.append(date2)
        for dd in week_days:
            counter += dd[1]
        week_data = (woy, counter)
        return week_data

    # Find the numbers for all the weeks for a given year
    def year_weeks(self, year, month):
        _, start, _ = datetime.datetime(year, month, 1).isocalendar()
        for d in (31, 30, 29, 28):
            try:
                _, end, _ = datetime.datetime(year, month, d).isocalendar()
                break
            except ValueError:  # skip attempts with bad dates
                continue
        if start > 50:  # spillover from previous year
            return [start] + list(range(1, end + 1))
        else:
            return list(range(start, end + 1))

    # Calculates the number of posts with at least 1 genre-term
    def find_posts_mentioning_genres(self, wordslist, termslist):
        wordslist = list(dict.fromkeys(wordslist))
        for word in wordslist:
            if word in termslist:
                self.genre_posts_no += 1
                break
            else:
                pass

    # Fill the term freq dictionary function
    def populate_term_freq_dict(self, wordslist, termslist, date):
        wordslist = list(dict.fromkeys(wordslist))
        for word in wordslist:
            if word in termslist:
                term_index = termslist.index(word)
                term_dates_dict = self.terms_dates[term_index]

                try:
                    posts_on_date = int(term_dates_dict.get(date))
                    posts_on_date += 1
                    term_dates_dict.update({date: posts_on_date})
                except:
                    term_dates_dict.update({date: 1})

                self.terms_dates[term_index] = term_dates_dict

    # Fill the term freq dictionary function
    def populate_term_freq_dict2(self, wordslist, termslist, termdict):
        for word in wordslist:
            if word in termslist:
                try:
                    termdict[word] += 1
                except:
                    termdict.update({word: 1})

    # Create article/blogs metrics histograms
    def create_histograms(self):
        fig = plt.figure()
        ax1 = fig.add_subplot(2, 1, 1)
        ax2 = fig.add_subplot(2, 1, 2)
        fig2 = plt.figure()
        ax3 = fig2.add_subplot(2, 1, 1)
        ax4 = fig2.add_subplot(2, 1, 2)

        total_title_chars = list()
        for listitem in self.metrics_data:
            total_title_chars.append(listitem[0])
        total_title_chars = np.asarray(total_title_chars)
        n, bins, patches = ax1.hist(total_title_chars, histtype='bar', label=['Characters'])
        ax1.set_ylabel('Frequency')
        ax1.set_xlabel('Article title chars distribution')
        ax1.legend(loc="upper right")


        total_title_words = list()
        for listitem in self.metrics_data:
            total_title_words.append(listitem[1])
        total_title_words = np.asarray(total_title_words)
        n, bins, patches = ax2.hist(total_title_words, histtype='bar', label=['Words'], color='orange')
        ax2.set_ylabel('Frequency')
        ax2.set_xlabel('Article title words distribution')
        ax2.legend(loc="upper right")

        total_article_chars = list()
        for listitem in self.metrics_data:
            total_article_chars.append(listitem[2])
        total_article_chars = np.asarray(total_article_chars)
        n, bins, patches = ax3.hist(total_article_chars, histtype='bar', label=['Characters'])
        ax3.set_ylabel('Frequency')
        ax3.set_xlabel('Article chars distribution')
        ax3.legend(loc="upper right")

        total_article_words = list()
        for listitem in self.metrics_data:
            total_article_words.append(listitem[3])
        total_article_words = np.asarray(total_article_words)
        n, bins, patches = ax4.hist(total_article_words, histtype='bar', label=['Words'], color='orange')
        ax4.set_ylabel('Frequency')
        ax4.set_xlabel('Article words distribution')
        ax4.legend(loc="upper right")

        plt.show()

    # Create article collection metrics histograms
    def create_collection_histograms(self, collection, metricsdata):
        fig = plt.figure()
        ax1 = fig.add_subplot(2, 1, 1)
        ax2 = fig.add_subplot(2, 1, 2)
        fig2 = plt.figure()
        ax3 = fig2.add_subplot(2, 1, 1)
        ax4 = fig2.add_subplot(2, 1, 2)

        Title_chars = list()
        for listitem in metricsdata:
            Title_chars.append(listitem[0])
        Title_chars = np.asarray(Title_chars)
        n, bins, patches = ax1.hist(Title_chars, histtype='bar', label=['Characters'])
        ax1.set_ylabel('Frequency')
        ax1.set_xlabel('Article title chars distribution/articles\nCollection : {}'.format(collection))
        ax1.legend(loc="upper right")
        plt.savefig(str(str(collection) + '-a' + '.png'), dpi=300)

        Title_words = list()
        for listitem in metricsdata:
            Title_words.append(listitem[1])
        Average_title_words = np.asarray(Title_words)
        n, bins, patches = ax2.hist(Title_words, histtype='bar', label=['Words'], color='orange')
        ax2.set_ylabel('Frequency')
        ax2.set_xlabel('Article title words distribution/articles\nCollection : {}'.format(collection))
        ax2.legend(loc="upper right")
        plt.savefig(str(str(collection) + '-b' + '.png'), dpi=300)

        Article_chars = list()
        for listitem in metricsdata:
            Article_chars.append(listitem[2])
        Article_chars = np.asarray(Article_chars)
        n, bins, patches = ax3.hist(Article_chars, histtype='bar', label=['Characters'])
        ax3.set_ylabel('Frequency')
        ax3.set_xlabel('Article chars distribution/articles\nCollection : {}'.format(collection))
        ax3.legend(loc="upper right")
        plt.savefig(str(str(collection) + '-c' + '.png'), dpi=300)

        Article_words = list()
        for listitem in metricsdata:
            Article_words.append(listitem[3])
        Article_words = np.asarray(Article_words)
        n, bins, patches = ax4.hist(Article_words, histtype='bar', label=['Words'], color='orange')
        ax4.set_ylabel('Frequency')
        ax4.set_xlabel('Article words distribution/articles\nCollection : {}'.format(collection))
        ax4.legend(loc="upper right")
        plt.savefig(str(str(collection) + '-d' + '.png'), dpi=300)

        plt.show()

    # Count total dataset articles
    def count_articles(self):
        total_articles = int()
        for collection in self.articles_conn:
            articles = list(self.db.get_collection(collection).find())
            total_articles += len(articles)
        return total_articles

    # Format the EDML entity linking data to the required format by Spacy
    def format_traindata(self):
        tdata = []
        file_id = 1
        while file_id <= 699:
            with open(os.path.dirname(os.path.realpath(__file__)) + f"\\elmd2\\json ({file_id}).json") \
                      as json_file:
                data = json.load(json_file)
                for item in data:
                    text = item['text']
                    ent_list = []
                    if len(item['entities']) > 0:
                        for ent in item['entities']:
                            if ent['category'] == 'Artist':
                                tup = (ent['startChar'], ent['endChar'], ent['category'])
                                ent_list.append(tup)
                        td = (text, {'entities': ent_list})
                        tdata.append(td)
            file_id += 1
        random.seed(75)
        random.shuffle(tdata)
        return tdata[:1000]

    # Load the trained NER model
    def load_NER(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))+'\\ner'
        nlp = spacy.load(dir_path)

        client_id = '59a82995075f42d391d043a01435062d'
        client_secret = 'c1152351e58646cbb4d2ebd41f04c6f1'
        client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

        # Test and use NER model on the collected music articles dataset
        for collection in self.articles_conn:
            articles = list(self.db.get_collection(collection).find())

            for article in articles:
                article = article['article']
                doc = nlp(article)
                if len(doc.ents) > 0:
                    for ent in doc.ents:
                        if ent.label_ == 'Artist':
                            spotify_verify = sp.search(ent.text,type = 'artist', limit = 30)
                            # Verify extracted entity could be refering to an artist
                            if len(spotify_verify['artists']['items']) > 0:
                                try:
                                    entity_count = int(self.entities.get(ent.text))
                                    entity_count += 1
                                    self.entities.update({ent.text: entity_count})
                                except:
                                    self.entities[ent.text] = 1
                            else:
                                continue
        print(self.entities)
        print(len(self.entities))

    # Calculate Precision - Recall - F1 scores on the test set
    def evaluate(self, test_set):
        dir_path = os.path.dirname(os.path.realpath(__file__)) + '\\ner'
        ner_model = spacy.load(dir_path)
        scorer = Scorer()
        test_size = len(test_set)
        test_scores = [0, 0, 0]
        client_id = '59a82995075f42d391d043a01435062d'
        client_secret = 'c1152351e58646cbb4d2ebd41f04c6f1'
        client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        for input_, annot in test_set:
            for tup in annot['entities']:
                ent = input_[tup[0]:tup[1]]
                spotify_verify = sp.search(ent, type='artist', limit=30)
                if len(spotify_verify['artists']['items']) > 0:
                    continue
                else:
                    annot['entities'].remove(tup)
            doc_gold_text = ner_model.make_doc(input_)
            gold = GoldParse(doc_gold_text, entities=annot['entities'])
            pred_value = ner_model(input_)
            scorer.score(pred_value, gold)
            result = scorer.scores
            res_list = [result['ents_p'], result['ents_r'], result['ents_f']]
            test_scores = [test_scores[i] + res_list[i] for i in range(len(test_scores))]
        test_scores = [round(test_scores[i] / test_size, 2) for i in range(len(test_scores))]
        return test_scores

# Training the NER Model for the new "Artist" entity
@plac.annotations(
    model=("Model name. Defaults to blank 'en' model.", "option", "m", str),
    new_model_name=("New model name for model meta.", "option", "nm", str),
    output_dir=("Optional output directory", "option", "o", Path),
    n_iter=("Number of training iterations", "option", "n", int),
)
def main(model=None, new_model_name="Music Data", output_dir=os.path.dirname(os.path.realpath(__file__))+'\\ner', n_iter=10):
    LABEL_1 = 'Artist'
    stat = StatisticalAnalysis()
    data = stat.format_traindata()
    TEST_DATA = data[0:1000]
    TRAIN_DATA = data[1000:]
    """Set up the pipeline and entity recognizer, and train the new entity."""
    random.seed(0)
    if model is not None:
        nlp = spacy.load(model)  # load existing spaCy model
        print("Loaded model '%s'" % model)
    else:
        nlp = spacy.blank("en")  # create blank Language class
        print("Created blank 'en' model")
    # Add entity recognizer to model if it's not in the pipeline
    # nlp.create_pipe works for built-ins that are registered with spaCy
    if "ner" not in nlp.pipe_names:
        ner = nlp.create_pipe("ner")
        nlp.add_pipe(ner)
    # otherwise, get it, so we can add labels to it
    else:
        ner = nlp.get_pipe("ner")

    ner.add_label(LABEL_1)  # add new entity label to entity recognizer

    if model is None:
        optimizer = nlp.begin_training()
    else:
        optimizer = nlp.resume_training()
    move_names = list(ner.move_names)
    # get names of other pipes to disable them during training
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]

    with nlp.disable_pipes(*other_pipes):  # only train NER
        sizes = compounding(1.0, 4.0, 1.001)
        # batch up the examples using spaCy's minibatch
        for itn in range(n_iter):
            random.shuffle(TRAIN_DATA)
            batches = minibatch(TRAIN_DATA, size=sizes)
            losses = {}
            for batch in batches:
                texts, annotations = zip(*batch)
                nlp.update(texts, annotations, sgd=optimizer, drop=0.35, losses=losses)
            print("Losses", losses)

    # save model to output directory
    if output_dir is not None:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.meta["name"] = new_model_name  # rename model
        nlp.to_disk(output_dir)
        print("Saved model to", output_dir)

    # test the trained model
    accuracy_score = int()

    # Calculate accuracy score
    for td in TEST_DATA:
        test_text = td[0]
        real_ents = list(td[1]['entities'])
        test_score = int()
        doc = nlp(test_text)
        for ent in doc.ents:
            tup = (ent.start_char, ent.end_char, ent.label_)
            if tup in real_ents:
                test_score += 1

        if len(doc.ents) > 0:
            accuracy_score += test_score / len(doc.ents)

    accuracy_score = accuracy_score / 1000
    print(f'Accuracy metric score is {accuracy_score}')

    # Calculate Precision-Recall scores
    results = stat.evaluate(TEST_DATA)
    print(f'Precision metric score is {results[0]} ')
    print(f'Recall accuracy metric score is {results[1]} ')
    print(f'F1 accuracy metric score is {results[2]} ')


if __name__ == "__main__":
    stat = StatisticalAnalysis()
    stat.find_all_article_collections()
    # stat.calculate_article_metrics()
    # stat.create_histograms()
    # print(stat.count_articles())
    # stat.create_tf_timelines()
    # stat.create_normalized_bc()
    # stat.analyse_site_activity()
    # stat.calculate_genres_frequency()
    # plac.call(main)
    data = stat.format_traindata()
    # stat.load_NER()
    print(stat.evaluate(data))
