Sofia <sofiaxia61@gmail.com>

11:43 (4 minuti fa)

a Kindle



import numpy as np

import pandas as pd

from scipy.sparse import csr_matrix

from sklearn.neighbors import NearestNeighbors

#from pyspark.ml.evaluation import RegressionEvaluator

#from bookclubs.recommender.BookLens import BookLens

#from bookclubs.recommender.evaluator import Evaluator

#

# def LoadBookLensData():

#     ml = BookLens()

#     print("Loading book ratings...")

#     data = ml.loadBookLensLatestSmall()

#     print("\nComputing book popularity ranks so we can measure novelty later...")

#     rankings = ml.getPopularityRanks()

#     return (ml, data, rankings)





# Load up common data set for the recommender algorithms

# (ml, evaluationData, rankings) = LoadBookLensData()

# print("after loadbooklens")

# # Construct an Evaluator to, you know, evaluate them

# evaluator = Evaluator(evaluationData, rankings)

# print("after evaluator")

books = pd.read_csv("bookclubs/ml-latest-small/BX_Books.csv", sep=';', encoding="latin-1", error_bad_lines=False)

users = pd.read_csv("bookclubs/ml-latest-small/BX-Users.csv", sep=';', encoding="latin-1", error_bad_lines=False)

ratings = pd.read_csv("bookclubs/ml-latest-small/BX-Book-Ratings.csv", sep=';', encoding="latin-1", error_bad_lines=False)



books = books[['ISBN', 'Book-Title', 'Book-Author', 'Year-Of-Publication', 'Publisher']]

books.rename(columns = {'Book-Title':'title', 'Book-Author':'author', 'Year-Of-Publication':'year', 'Publisher':'publisher'}, inplace=True)

users.rename(columns = {'User-ID':'user_id', 'Location':'location', 'Age':'age'}, inplace=True)

ratings.rename(columns = {'User-ID':'user_id', 'Book-Rating':'rating'}, inplace=True)



x = ratings['user_id'].value_counts() > 200

y = x[x].index  #user_ids

print(y.shape)

ratings = ratings[ratings['user_id'].isin(y)]



rating_with_books = ratings.merge(books, on='ISBN')

rating_with_books.head()



number_rating = rating_with_books.groupby('title')['rating'].count().reset_index()

number_rating.rename(columns= {'rating':'number_of_ratings'}, inplace=True)

final_rating = rating_with_books.merge(number_rating, on='title')

final_rating.shape

final_rating = final_rating[final_rating['number_of_ratings'] >= 50]

final_rating.drop_duplicates(['user_id','title'], inplace=True)



book_pivot = final_rating.pivot_table(columns='user_id', index='title', values="rating")

book_pivot.fillna(0, inplace=True)



book_sparse = csr_matrix(book_pivot)



model = NearestNeighbors(algorithm='brute')

#evaluator.AddAlgorithm(model, "brute")

#evaluator.Evaluate(False)

#evaluator.SampleTopNRecs(ml)



model_transform=model.fit(book_sparse)

#predictions_train = model_transform.transform(book_sparse)

# evaluator = RegressionEvaluator(metricName="rmse", labelCol="Book-Rating",

#                                     predictionCol="prediction")

# rmse_train = evaluator.evaluate(predictions_train)

# print("Root-mean-square error for train = " + str(rmse_train))

print(book_pivot.iloc[200, :])

distances, suggestions = model.kneighbors(book_pivot.iloc[200, :].values.reshape(1, -1))

for i in range(len(suggestions)):

  print(book_pivot.index[suggestions[i]])



print("the end")









Inviato da Posta per Windows
