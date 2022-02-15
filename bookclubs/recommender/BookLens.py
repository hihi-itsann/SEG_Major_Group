import os
import csv
import sys
import re

from surprise import Dataset
from surprise import Reader

from collections import defaultdict
import numpy as np
import pandas as pd


class BookLens:

    isbn_to_name = {}
    name_to_isbn = {}
    ratingsPath = '../dataset/BX-Book-Ratings.csv'
    booksPath = '../dataset/BX-Books.csv'

    def loadRatingData(self):
        df = pd.read_csv(self.ratingsPath, sep = ';',names = ['User-ID', 'ISBN', 'Book-Rating'], quotechar = '"', encoding = 'latin-1',header = 0 )

        return df.head(1000)

    def loadBookLensLatestSmall(self):

        # Look for files relative to the directory we are running from
        # os.chdir(os.path.dirname(sys.argv[0]))

        ratingsDataset = 0
        self.isbn_to_name = {}
        self.name_to_isbn = {}

        reader = Reader(line_format='user item rating timestamp', sep=',', skip_lines=1)

        ratingsDataset = Dataset.load_from_df(self.loadRatingData(), reader=reader)

        with open(self.booksPath, newline='', encoding='ISO-8859-1') as csvfile:
                bookReader = csv.reader(csvfile, delimiter = ';')
                next(bookReader)  #Skip header line
                for row in bookReader:
                    isbn = row[0]
                    bookName = row[1]
                    self.isbn_to_name[isbn] = bookName
                    self.name_to_isbn[bookName] = isbn

        return ratingsDataset

    def getUserRatings(self, user):
        userRatings = []
        hitUser = False
        with open(self.ratingsPath, newline='') as csvfile:
            ratingReader = csv.reader(csvfile, delimiter = ';', quotechar = '"')
            next(ratingReader)
            for row in ratingReader:
                userID = int(row[0])
                if (user == userID):
                    isbn = row[1]
                    rating = float(row[2])
                    userRatings.append((isbn, rating))
                    hitUser = True
                if (hitUser and (user != userID)):
                    break

        return userRatings

    def getPopularityRanks(self):
        ratings = defaultdict(int)
        rankings = defaultdict(int)
        with open(self.ratingsPath, newline='', encoding='ISO-8859-1') as csvfile:
            ratingReader = csv.reader(csvfile, delimiter = ';')
            next(ratingReader)
            for row in ratingReader:
                isbn = row[1]
                ratings[isbn] += 1
        rank = 1
        for isbn, ratingCount in sorted(ratings.items(), key=lambda x: x[1], reverse=True):
            rankings[isbn] = rank
            rank += 1
        return rankings

    # def getGenres(self):
    #     genres = defaultdict(list)
    #     genreIDs = {}
    #     maxGenreID = 0
    #     with open(self.booksPath, newline='', encoding='ISO-8859-1') as csvfile:
    #         bookReader = csv.reader(csvfile, delimiter = ';')
    #         next(bookReader)  #Skip header line
    #         for row in bookReader:
    #             isbn = row[0]
    #             genreList = row[2].split('|')
    #             genreIDList = []
    #             for genre in genreList:
    #                 if genre in genreIDs:
    #                     genreID = genreIDs[genre]
    #                 else:
    #                     genreID = maxGenreID
    #                     genreIDs[genre] = genreID
    #                     maxGenreID += 1
    #                 genreIDList.append(genreID)
    #             genres[isbn] = genreIDList
    #     # Convert integer-encoded genre lists to bitfields that we can treat as vectors
    #     for (isbn, genreIDList) in genres.items():
    #         bitfield = [0] * maxGenreID
    #         for genreID in genreIDList:
    #             bitfield[genreID] = 1
    #         genres[isbn] = bitfield
    #
    #     return genres

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

    def getBookName(self, isbn):
        if isbn in self.isbn_to_name:
            return self.isbn_to_name[isbn]
        else:
            return ""

    def getISBN(self, bookName):
        if bookName in self.name_to_isbn:
            return self.name_to_isbn[bookName]
        else:
            return 0
