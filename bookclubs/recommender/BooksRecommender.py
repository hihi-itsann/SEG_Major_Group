from getpass import getuser
from operator import index
import os
import csv
from posixpath import sep
import sys
import re
import urllib.request
import json
import pandas as pd
# Part of getGenra code comes from https://gist.github.com/AO8/faa3f52d3d5eac63820cfa7ec2b24aa7
from surprise import Dataset
from surprise import Reader

from collections import defaultdict

    
class BooksRecommender:

    # def loadData(self):
    #     user_book_rating = zipfile.ZipFile('./dataset/book-review-dataset.zip')
    #     user_book_rating.extractall("./dataset") 
    #     user_book_rating.close()
    #     # unzip the file cuz its to large to put in
    #     # load user information, get userID and other info
    #     users = {}
    #     with codecs.open('./dataset/BX-Users.csv', 'r', 'latin-1') as user:
    #         next(user)
    #         for line in user:
    #             features = list(map(lambda x: x.strip('"'), line.split(';')))
    #             users[features[0]] = "--".join(features[1:])

    #     books = {}
    #     with codecs.open('./dataset/BX-Books.csv', 'r', 'latin-1') as book:
    #         next(book)
    #         for line in book:
    #             features = list(map(lambda x: x.strip('"'), line.split(';')))
    #             books[features[0]] = '--'.join(features[1:])

    #     ratings = {}
    #     with codecs.open('./dataset/BX-Book-Ratings.csv', 'r', 'latin-1') as rating:
    #         next(rating)
    #         for line in rating:
    #             features = list(map(lambda x: x.strip('"'), line.split(';')))
    #             if features[0] in ratings:
    #                 current_ratings = ratings[features[0]]
    #             else:
    #                 current_ratings = {}
    #             current_ratings[features[1]] = int(features[2].strip().strip('"'))
    #             ratings[features[0]] = current_ratings

    # #     books = pd.read_csv('./dataset/BX-Books.csv', sep=';')
    # #     user = pd.read_csv('./dataset/BX-Users.csv', sep=';')
    # #     ratings = pd.read_csv('./dataset/BX-Books-Ratings.csv', sep=';')
    #     df = pd.DataFrame({ 'User-ID': users,
    #                         'ISBN'   : books,
    #                         'rating' : ratings})
    #     return df



    os.chdir(os.path.dirname(sys.argv[0]))

    
    isbn_to_bookTitle = {}
    bookTitle_to_isbn = {}
    ratingsPath = './dataset/BX-Book-Ratings.csv'
    booksPath   = './dataset/BX-Books.csv'
    
    def loadRatingData(self):
            df = pd.read_csv(self.ratingsPath, sep = ';',names = ['User-ID', 'ISBN', 'Book-Rating'], quotechar = '"', encoding = 'latin-1',header = 0)
            new_df = df[df.loc[:]!=0].dropna()
            new_df.to_csv('./dataset/BX-Books.csv')
            return new_df.head(10000)

    """     def loadRatingData(self):
        
        df = pd.read_csv(self.ratingsPath, sep = ';',names = ['User-ID', 'ISBN', 'Book-Rating'], quotechar = '"', encoding = 'latin-1',header = 0 )
        #df.to_csv("test.csv", index = False)
        return df.sample(frac=1).reset_index(drop=True).head(10000) """

    def loadBookRecommenderLatestSmall(self):

        # Look for files relative to the directory we are running from
        #os.chdir(os.path.dirname(sys.argv[0]))
        ratingsDataset = 0
        self.isbn_to_bookTitle = {}
        self.bookTitle_to_isbn = {}

        reader = Reader(line_format = 'user item rating', sep = ',',skip_lines = 1, rating_scale=(1,10))

        ratingsDataset = Dataset.load_from_df(self.loadRatingData(), reader = reader)

        with open(self.booksPath, newline='', encoding='ISO-8859-1') as csvfile:
                bookReader = csv.reader(csvfile, delimiter = ';')
                next(bookReader)  #Skip header line
                for row in bookReader:
                    isbn = row[0]
                    bookTitle = row[1]
                    self.isbn_to_bookTitle[isbn] = bookTitle
                    self.bookTitle_to_isbn[bookTitle] = isbn
        return ratingsDataset

    def getUserratings(self, user):
        userRatings = []
        hitUser = False
        with open(self.ratingsPath, newLine = '') as csvfile:
            ratingReader = csv.reader(csvfile, delimiter = ';', quotechar = '"')
            next(ratingReader)
            for row in ratingReader:
                userID = int(row[0])
                if (user == userID):
                    isbn = row[1]
                    rating = float(row[2])
                    if rating != 0:
                        userRatings.append((isbn, rating))
                    hitUser = True
                if (hitUser and (user != userID)):
                    break
    
    def getPopularityRanks(self):
        ratings = defaultdict(int)
        rankings = defaultdict(int)
        with open(self.ratingsPath, newline = '', encoding='ISO-8859-1') as csvfile:
            ratingReader = csv.reader(csvfile, delimiter = ';')
            next(ratingReader)
            for row in ratingReader:
                isbn = row[1]
                ratings[isbn] += 1
        rank = 1
        for isbn, ratingCount in sorted(ratings.items(), key = lambda x: x[1], reverse = True):
            rankings[isbn] = rank
            rank += 1
        return rankings

    def getYears(self):
        p = re.compile(r"(?:\((\d{4})\))?\s*$")
        years = defaultdict(int)
        with open(self.booksPath, newline='', encoding='ISO-8859-1') as csvfile:
            bookReader = csv.reader(csvfile, delimiter = ';')
            next(bookReader)
            for row in bookReader:
                isbn = row[0]
                title = row[1]
                m = p.search(title)
                year = m.group(1)
                if year:
                    years[isbn] = int(year)
        return years

    def getBookTitle(self, isbn):
        if isbn in self.isbn_to_bookTitle:
            return self.isbn_to_bookTitle[isbn]
        else:
            return ""
        
    def getIsbn(self, bookTitle):
        if bookTitle in self.bookTitle_to_isbn:
            return self.bookTitle_to_isbn
        else:
            return 0

# not sure if this useful at current stage
    def getGenra(self, isbn):
        base_api_link = "https://www.googleapis.com/books/v1/volumes?q=isbn:"

        with urllib.request.urlopen(base_api_link + isbn) as f:
            text = f.read()

        decoded_text = text.decode("utf-8")
        obj = json.loads(decoded_text) # deserializes decoded_text to a Python object
        volume_info = obj["items"][0] 
        return  volume_info["volumeInfo"]["categories"]
                