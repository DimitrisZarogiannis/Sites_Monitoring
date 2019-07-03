# Import packages
from pymongo import MongoClient
import matplotlib.pyplot as plt
plt.rcdefaults()
import numpy as np
import datetime
import re
from matplotlib.ticker import MaxNLocator
import pendulum

# Simple statistical analysis class for the following metrics:
# 1) Number of characters per article title
# 2) Number of words per article title
# 3) Number of characters per article
# 4) Number of words per article


class StatisticalAnalysis:
    client = MongoClient('mongodb://localhost:27017')
    db = client['Articles_DB']
    genres_term_frequency = db.genres
    blogs_activity = db.blogs_activity
    articles_conn = list()
    articles_count = 0
    term_freq = {}
    terms_dates = []
    metrics_data = list()
    outliers = []

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
            # self.create_collection_histograms(collection, collection_metrics_data)

            self.metrics_data = self.metrics_data + collection_metrics_data

        outlier_collections = {}
        for item in self.outliers:
            if item[0] in outlier_collections:
                outlier_collections[item[0]] += 1
            else:
                outlier_collections[item[0]] = 1

        # print(outlier_collections)

        # for outlier_post in self.outliers:
        #     if outlier_post[0] == 'articles5':
        #         print(outlier_post)

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
    def find_timeline_data_week(self, dates, month, year, activity):
        timeline_dates = []
        timeline_activity_data = []
        for post_date in dates:
            post_year = int(post_date[0:4])
            post_month = int(post_date[5:7])
            if post_year == year and post_month == month:
                timeline_dates.append(post_date)
        for date in timeline_dates:
            dt = pendulum.parse(date)
            week_number = dt.week_of_month
            week_index = None
            if len(timeline_activity_data) > 0:
                for item in timeline_activity_data:
                    if week_index is None:
                        if week_number == int(item[0]):
                            week_index = timeline_activity_data.index(item)
                if week_index is not None:
                    week_data = timeline_activity_data[week_index]
                    week_data[1] += activity[date]
                    timeline_activity_data[week_index] = week_data
                else:
                    timeline_activity_data.append([week_number, activity[date]])
            else:
                timeline_activity_data.append([week_number, activity[date]])
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
                genres_list[index] = re.sub(r'[\n\r]+$', '', gen)

        self.terms_dates = [{} for _ in range(len(genres_list))]

        # Load all collection's articles and calculate term appearance frequency
        for collection in self.articles_conn:
            collection_tf_data = [0] * len(genres_list)
            articles = list(self.db.get_collection(collection).find())

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
                words_list = article_body.split(' ')
                # Calculate genre's terms frequency for every collection
                for word in words_list:
                    if word in genres_list:
                        index = genres_list.index(word)
                        collection_tf_data[index] += 1

                # Calculate terms total appearance frequencies
                if article_date:
                    self.populate_term_freq_dict(words_list, genres_list, article_date)
                else:
                    self.populate_term_freq_dict2(words_list, genres_list)

            # Create Bar Charts for every collection's term frequency data
            # genres = []
            # f_values = []
            # for tf in collection_tf_data:
            #     if tf > 0:
            #         index = collection_tf_data.index(tf)
            #         genres.append(genres_list[index])
            #         f_values.append(tf)
            #
            # y_pos = np.arange(len(genres))
            # plt.bar(y_pos, f_values, align='center', alpha=0.5)
            # plt.xticks(y_pos, genres, rotation=90)
            # plt.ylabel('Frequency')
            # plt.xlabel('Genres')
            # plt.title('Collection : {}'.format(collection))
            # plt.tight_layout()
            # plt.savefig(str(str(collection) + '_bc' + '.png'))
            # plt.show()

        # Insert total genre term frequencies data for all the collections
        # self.genres_term_frequency.insert_one(self.term_freq)

        # Insert total genres tf time-series data for all collections // Create tf time-series diagrams
        timeseries_data = list(map(lambda x, y: [x, y], genres_list, self.terms_dates))
        # self.genres_term_frequency.insert_one({'item': timeseries_data})
        self.create_tf_timelines()

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
            latest_months = self.find_3_latest_months(dates_list, latest_year)
            for month in latest_months:
                genre_plot_data.append(sorted(self.find_timeline_data_week(dates_list, month,
                                                                           latest_year, genre_tf[1]), key=lambda x:x[0]))

            plot_data.append(genre_plot_data)
            genres.append(genre)
            genres_info.append([latest_year, latest_months])


        for d in plot_data:
            genre = genres[plot_data.index(d)]
            info = genres_info[plot_data.index(d)]
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.set_xlim(1, 5)
            ax.yaxis.set_major_locator(MaxNLocator(nbins=4, min_n_ticks=1, integer=True))
            ax.xaxis.set_major_locator(MaxNLocator(nbins=4, min_n_ticks=1, integer=True))
            plt.xlabel('Weeks')
            plt.ylabel('Number of Posts')
            plt.grid()
            for month in d:
                x = [dt[0] for dt in month]
                y = [dt[1] for dt in month]
                ax.plot(x, y, '-8', label=str(info[1][d.index(month)]) + ' \\ '+str(info[0]))
            plt.legend()
            plt.title('Genre Term : {}'.format(genre))
            plt.savefig(str(str(genre)+'.png'), dpi=300)
        #plt.show()

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

                try:
                    self.term_freq[word] += 1
                except:
                    self.term_freq.update({word: 1})

    # Fill the term freq dictionary function
    def populate_term_freq_dict2(self, wordslist, termslist):
        for word in wordslist:
            if word in termslist:
                try:
                    self.term_freq[word] += 1
                except:
                    self.term_freq.update({word: 1})

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

    def count_articles(self):
        total_articles = int()
        for collection in self.articles_conn:
            articles = list(self.db.get_collection(collection).find())
            total_articles += len(articles)
        return total_articles


if __name__ == "__main__":
    stat = StatisticalAnalysis()
    stat.find_all_article_collections()
    # stat.calculate_article_metrics()
    # stat.create_histograms()
    #print(stat.count_articles())
    stat.create_tf_timelines()
    # stat.analyse_site_activity()
    # stat.calculate_genres_frequency()
