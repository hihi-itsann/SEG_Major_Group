import os
import csv
import sys
import re

from surprise import Dataset
from surprise import Reader

from collections import defaultdict

class BookRecommender:
    
    isbn_to_bookTitle = {}
    bookTitle_to_isbn = {}
    ratingsPath = '/book-review-dataset/BX_Book_Ratings.csv'
    booksPath   = '/book-review-dataset/BX_Books.csv'

    def loadBookRecommenderLatestSmall(self):

        # Look for files relative to the directory we are running from
        os.chdir(os.path.dirname(sys.argv[0]))

        ratingsDataset = 0
        self.isbn_to_bookTitle = {}
        self.bookTitle_to_isbn = {}

        reader = Reader(line_format = 'User-ID ISBN Book-Rating', sep = ',', skip_lines = 1)

        ratingsDataset = Dataset.load_from_file(self.ratingsPath, reader = reader)

        with open(self.booksPath, newline='', encoding='ISO-8859-1') as csvfile:
                bookReader = csv.reader(csvfile)
                next(bookReader)  #Skip header line
                for row in bookReader:
                    isbn = int(row[0])
                    bookTitle = row[1]
                    self.isbn_to_bookTitle[isbn] = bookTitle
                    self.bookTitle_to_isbn[bookTitle] = isbn
        return ratingsDataset

    def getUserratings(self, user):
        userRatings = []
        hitUser = False
        with open(self.ratingsPath, newLine = '') as csvfile:
            ratingReader = csv.reader(csvfile)
            next(ratingReader)
            for row in ratingReader:
                userID = int(row[0])
                if (user == userID):
                    isbn = int(row[1])
                    rating = float(row[2])
                    userRatings.append((isbn, rating))
                    hitUser = True
                if (hitUser and (user != userID)):
                    break
    
    def getPopularityRanks(self):
        ratings = defaultdict(int)
        rankings = defaultdict(int)
        with open(self.ratingsPath, newline = '') as csvfile:
            ratingReader = csv.reader(csvfile)
            next(ratingReader)
            for row in ratingReader:
                isbn = int(row[1])
                ratings[isbn] += 1
        rank = 1
        for isbn, ratingCount in sorted(ratings.items(), key = lambda x: x[1], reverse = True):
            rankings[isbn] = rank
            rank += 1

    def getYears(self):
        p = re.compile(r"(?:\((\d{4})\))?\s*$")
        years = defaultdict(int)
        with open(self.booksPath, newline='', encoding='ISO-8859-1') as csvfile:
            bookReader = csv.reader(csvfile)
            next(bookReader)
            for row in bookReader:
                isbn = int(row[0])
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
                