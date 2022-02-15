import os
import csv
import sys
import re
import urllib.request
import json

from surprise import Dataset
from surprise import Reader

from collections import defaultdict
import numpy as np
import pandas as pd

class BookLens:

    BookISBN_to_title = {}
    title_to_bookISBN = {}
    ratingsPath = '../ml-latest-small/BX-Book-Ratings.csv'
    booksPath = '../ml-latest-small/BX_Books.csv'
    def loadRatingData(self):
        df = pd.read_csv(self.ratingsPath, sep = ';',names = ['User-ID', 'ISBN', 'Book-Rating'], quotechar = '"', encoding = 'latin-1',header = 0 )
        min_book_ratings = 50
        filter_books = df['ISBN'].value_counts() > min_book_ratings
        filter_books = filter_books[filter_books].index.tolist()
        
        min_user_ratings = 50
        filter_users = df['User-ID'].value_counts() > min_user_ratings
        filter_users = filter_users[filter_users].index.tolist()
        
        df_new = df[(df['ISBN'].isin(filter_books)) & (df['User-ID'].isin(filter_users))]
        print('The original data frame shape:\t{}'.format(df.shape))
        print('The new data frame shape:\t{}'.format(df_new.shape))
        return df_new

    def loadBookLensLatestSmall(self):

        # Look for files relative to the directory we are running from
        #os.chdir(os.path.dirname(sys.argv[0]))

        ratingsDataset = 0
        self.BookISBN_to_title = {}
        self.title_to_bookISBN = {}

        reader = Reader(line_format='user item rating', sep=';', skip_lines=1)
        ratingsDataset = Dataset.load_from_df(self.loadRatingData()[['User-ID', 'ISBN', 'Book-Rating']], reader=reader)
        #ratingsDataset = Dataset.load_from_file(self.ratingsPath, reader=reader)
        #ratingsDataset = Dataset.load_from_df(self.loadRatingData(), reader = reader)
        with open(self.booksPath, newline='', encoding='ISO-8859-1') as csvfile:
                bookReader = csv.reader(csvfile, delimiter = ';')
                next(bookReader)  #Skip header line
                for row in bookReader:
                    bookISBN = row[0]
                    bookTitle = row[1]
                    self.BookISBN_to_title[bookISBN] = bookTitle
                    self.title_to_bookISBN[bookTitle] = bookISBN

        return ratingsDataset

    def getUserRatings(self, user):
        userRatings = []
        hitUser = False
        with open(self.ratingsPath, newline='') as csvfile:
            ratingReader = csv.reader(csvfile,delimiter = ';')
            next(ratingReader)
            for row in ratingReader:
                userISBN = row[0]
                if (int(user) == userISBN):
                    bookISBN = row[1]
                    rating = float(row[2])
                    userRatings.append((bookISBN, rating))
                    hitUser = True
                if (hitUser and (user != userISBN)):
                    break

        return userRatings

    def getPopularityRanks(self):
        ratings = defaultdict(int)
        rankings = defaultdict(int)
        with open(self.ratingsPath, newline = '', encoding='ISO-8859-1') as csvfile:
            ratingReader = csv.reader(csvfile, delimiter = ';')
            next(ratingReader)
            for row in ratingReader:
                bookISBN = row[1]
                ratings[bookISBN] += 1
        rank = 1
        for bookISBN, ratingCount in sorted(ratings.items(), key = lambda x: x[1], reverse = True):
            rankings[bookISBN] = rank
            rank += 1
        return rankings
    #the situation when categories is more than 1 has not been considered
    def getGenres(self):
        genres = defaultdict(list)
        genreISBNs = {}
        maxGenreISBN = 0
        with open(self.booksPath, newline='', encoding='ISO-8859-1') as csvfile:
            bookReader = csv.reader(csvfile, delimiter = ';')
            next(bookReader)  #Skip header line
            for row in bookReader:
                bookISBN = row[0]
                genreList = self.getGenra(bookISBN)
                genreISBNList = []
                for genre in genreList:
                    if genre in genreISBNs:
                        genreISBN = genreISBNs[genre]
                    else:
                        genreISBN = maxGenreISBN
                        genreISBNs[genre] = genreISBN
                        maxGenreISBN += 1
                    genreISBNList.append(genreISBN)
                genres[bookISBN] = genreISBNList
        # Convert integer-encoded genre lists to bitfields that we can treat as vectors
        for (bookISBN, genreISBNList) in genres.items():
            bitfield = [0] * maxGenreISBN
            for genreISBN in genreISBNList:
                bitfield[genreISBN] = 1
            genres[bookISBN] = bitfield            
        
        return genres
    
    def getGenra(self, isbn):
        print(isbn)
        base_api_link = "https://www.googleapis.com/books/v1/volumes?q=isbn:"

        with urllib.request.urlopen(base_api_link + isbn) as f:
            text = f.read()

        decoded_text = text.decode("utf-8")
        obj = json.loads(decoded_text) # deserializes decoded_text to a Python object
        volume_info = obj["items"][0] 
        return  volume_info["volumeInfo"]["categories"][0]
               
    def getYears(self):
        p = re.compile(r"(?:\((\d{4})\))?\s*$")
        years = defaultdict(int)
        with open(self.booksPath, newline='', encoding='ISO-8859-1') as csvfile:
            bookReader = csv.reader(csvfile,delimiter = ';')
            next(bookReader)
            for row in bookReader:
                bookISBN = row[0]
                title = row[1]
                m = p.search(title)
                year = m.group(1)
                if year:
                    years[bookISBN] = int(year)
        return years
    
    def getMiseEnScene(self):
        mes = defaultdict(list)
        with open("LLVisualFeatures13K_Log.csv", newline='') as csvfile:
            mesReader = csv.reader(csvfile)
            next(mesReader)
            for row in mesReader:
                bookISBN = int(row[0])
                avgShotLength = float(row[1])
                meanColorVariance = float(row[2])
                stddevColorVariance = float(row[3])
                meanMotion = float(row[4])
                stddevMotion = float(row[5])
                meanLightingKey = float(row[6])
                numShots = float(row[7])
                mes[bookISBN] = [avgShotLength, meanColorVariance, stddevColorVariance,
                   meanMotion, stddevMotion, meanLightingKey, numShots]
        return mes
    
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