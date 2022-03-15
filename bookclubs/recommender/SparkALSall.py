# #-*- coding: utf-8 -*-
from pyspark.sql import SparkSession
from pyspark.ml.feature import StringIndexer, IndexToString
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.recommendation import ALS
from pyspark.sql.functions import explode
# from bookclubs.views import get_club_books_average_rating


from django.conf import settings

# from bookclubs.models import ClubBookAverageRating
from bookclubs import models
from bookclubs.models import User, Club, Role, Book, Rating, ClubBookAverageRating
from bookclubs.recommender.BookLens import BookLens

import pandas as pd
import csv



def get_club_books_average_rating():
    """ Saves the average rating of books read by users of each club (banned member are not included) """
    clubs=Club.objects.all()
    for club in clubs:
        members=club.get_moderators()|club.get_members()|club.get_management()
        for user in members:
            for rating in user.get_rated_books():
                clubBookRating=ClubBookAverageRating.objects.all().filter(club=club,book=rating.book)
                if clubBookRating:
                    clubBookRating.get().add_rating(clubBookRating.get().rate)
                    clubBookRating.get().increment_number_of_ratings()
                else:
                    ClubBookAverageRating.objects.create(
                        club=club,
                        book=rating.book,
                        rate=rating.rate,
                        number_of_ratings=1
                    )

# if __name__ == "__main__":
def modelTrain(club_id): #club_subject
    spark = SparkSession\
        .builder\
        .appName("bookclubs")\
        .master('local[4]')\
        .getOrCreate()

    spark.sparkContext.setCheckpointDir("/tmp/checkpoints")

    df = pd.read_csv('bookclubs/dataset/BX-Book-Ratings.csv', sep = ';',names = ['User-ID', 'ISBN', 'Book-Rating'], quotechar = '"', encoding = 'latin-1',header = 0 )
    df = df[df.loc[:]!=0].dropna()
    df.ISBN = df.ISBN.apply(lambda x: x[:-1] + "10" if x[-1] == "X" else x)
    df = df[df.ISBN.str.len() <= 11]
    df = spark.createDataFrame(df)

    # get_club_books_average_rating()
    # clubDf = pd.DataFrame(list(ClubBookAverageRating.objects.all().values()))
    # clubDf = spark.createDataFrame(clubDf)
    # indexer1 = StringIndexer(inputCol="book_id", outputCol="bookID").fit(clubDf)
    # indexed2 = indexer1.transform(clubDf)
    # ratings2 = indexed2.drop("book_id")

    indexer = StringIndexer(inputCol="ISBN", outputCol="bookID").fit(df)
    indexed = indexer.transform(df)
    ratings = indexed.drop("ISBN")
    """ lines = indexed.rdd
    ratingsRDD = lines.map(lambda p: Row(userId=int(p[0]), bookID=int(p[3]),
                                         rating=float(p[2])))
    ratings = spark.createDataFrame(ratingsRDD) """

    (training, test) = ratings.randomSplit([0.8, 0.2])

    als = ALS(maxIter=30, regParam=0.3,rank=40,userCol="User-ID", itemCol="bookID", ratingCol="Book-Rating",
              coldStartStrategy="drop")
    model = als.fit(training)
    return model
    # predictions_test = model.transform(test)
    # predictions_train = model.transform(training)
    # predictions_club = model.transform(ratings2)
    # labelConverter = IndexToString(inputCol="bookID", outputCol="book_id",
                            #    labels=indexer.labels)
    # evaluator = RegressionEvaluator(metricName="rmse", labelCol="Book-Rating",
                                    # predictionCol="prediction")
    # rmse_club = evaluator.evaluate(predictions_club)
    # rmse_test = evaluator.evaluate(predictions_test)
    # rmse_train = evaluator.evaluate(predictions_train)
    # print("Root-mean-square error for test = " + str(rmse_test))
    #print("Root-mean-square error for train = " + str(rmse_train))
    # print("Root-mean-square error for train = " + str(rmse_club))

    # userRecs = model.recommendForAllUsers(10)

    # flatUserRecs = userRecs.withColumn("bookAndRating", explode(userRecs.recommendations)) \
    # .select ( "club_id", "bookAndRating.*")

    # flatUserRecs = labelConverter.transform(flatUserRecs).filter(userRecs['club_id'] == club_id)
    # user85Recs = flatUserRecs.collect()
    # # user85Recs.show()


    # spark.stop()

    # ml = BookLens()
    # ml.loadBookLensLatestSmall()
  
    # print(len(user85Recs))

    # for row in user85Recs:
    #     print(ml.getBookName(row.book_id))

    # return(user85Recs)

def get_recommendations(club_id):
    model = modelTrain(club_id)
    spark = SparkSession\
        .builder\
        .appName("ALSExample")\
        .config("spark.executor.cores", '4')\
        .master('local[4]')\
        .getOrCreate()


    ClubBookAverageRating.objects.all().delete()

    get_club_books_average_rating()
    spark.sparkContext.setCheckpointDir("/tmp/checkpoints")
    df = pd.DataFrame(list(ClubBookAverageRating.objects.all().values()))
    new_cols = ['id','User-ID','book_id','rate','number_of_ratings']
    new_names_map = {df.columns[i]:new_cols[i] for i in range(len(new_cols))}
    df.rename(new_names_map, axis=1, inplace=True)
    df.book_id = df.book_id.apply(lambda x: x[:-1] + "10" if x[-1] == "X" else x)
    df = df[df.book_id.str.len() <= 11]
    df = df[df.loc[:]!=0].dropna()
    df = spark.createDataFrame(df)
    indexer1 = StringIndexer(inputCol="book_id", outputCol="bookID").fit(df)
    indexed2 = indexer1.transform(df)
    ratings2 = indexed2.drop("book_id") 

    predictions_club = model.transform(ratings2)

    labelConverter = IndexToString(inputCol="bookID", outputCol="book_id",
                               labels=indexer1.labels)
    evaluator = RegressionEvaluator(metricName="rmse", labelCol="rate",
                                    predictionCol="prediction")
    
    rmse_club = evaluator.evaluate(predictions_club)
    print("Root-mean-square error for train = " + str(rmse_club))

    userRecs = model.recommendForAllUsers(10)

    flatUserRecs = userRecs.withColumn("bookAndRating", explode(userRecs.recommendations)) \
    .select ( "User-ID", "bookAndRating.*")

    flatUserRecs = labelConverter.transform(flatUserRecs).filter(userRecs['User-ID'] == club_id)
    user85Recs = flatUserRecs.collect()
    # user85Recs.show()


    spark.stop()

    ml = BookLens()
    ml.loadBookLensLatestSmall()
  
    print(len(user85Recs))

# #-*- coding: utf-8 -*-

# from curses import BUTTON1_DOUBLE_CLICKED
# from email import header
# from os import sep
# from pyspark.sql import Row
# from pyspark.sql import SparkSession
# from pyspark.ml.feature import StringIndexer, IndexToString
# from pyspark.ml.evaluation import RegressionEvaluator
# from pyspark.ml.recommendation import ALS
# from pyspark.sql.functions import explode

# from bookclubs.models import ClubBookAverageRating, Club
# from bookclubs.recommender.BookLens import BookLens

# import pandas as pd
# import csv


    # spark.sparkContext.setCheckpointDir("/tmp/checkpoints")

# def get_club_books_average_rating():
#     """ Saves the average rating of books read by users of each club (banned member are not included) """

#     clubs=Club.objects.all()
#     for club in clubs:
#         members=club.get_moderators()|club.get_members()|club.get_management()
#         for user in members:
#             for rating in user.get_rated_books():
#                 clubBookRating=ClubBookAverageRating.objects.all().filter(club=club,book=rating.book)
#                 if clubBookRating:
#                     clubBookRating.get().add_rating(clubBookRating.get().rate)
#                     clubBookRating.get().increment_number_of_ratings()
#                 else:
#                     ClubBookAverageRating.objects.create(
#                         club=club,
#                         book=rating.book,
#                         rate=rating.rate,
#                         number_of_ratings=1
#                     )

# # if __name__ == "__main__":
# def get_recommendations(club_id): #club_subject
#     spark = SparkSession\
#         .builder\
#         .master("local")\
#         .appName("ALSExample")\
#         .config("spark.executor.cores", '4')\
#         .getOrCreate()

#     spark.sparkContext.setCheckpointDir("/tmp/checkpoints")
    
#     ClubBookAverageRating.objects.all().delete()

#     #df = pd.read_csv('bookclubs/dataset/BX-Book-Ratings.csv', sep = ';',names = ['User-ID', 'ISBN', 'Book-Rating'], quotechar = '"', encoding = 'latin-1',header = 0 )
#     get_club_books_average_rating()
#     df=pd.DataFrame(list(ClubBookAverageRating.objects.all().values()))
#     print(df)
#     df['Book-Rating']=df['rate']/df['number_of_ratings']
#     print(df)

#     df = df[df.loc[:]!=0].dropna()
#     df.book_id = df.book_id.apply(lambda x: x[:-1] + "10" if x[-1] == "X" else x)
#     df = df[df.book_id.str.len() <= 11]
#     df = spark.createDataFrame(df)

#     indexer = StringIndexer(inputCol="book_id", outputCol="bookID").fit(df)
#     indexed = indexer.transform(df)
#     ratings = indexed.drop("book_id")
#     """ lines = indexed.rdd
#     ratingsRDD = lines.map(lambda p: Row(userId=int(p[0]), bookID=int(p[3]),
#                                          rating=float(p[2])))
#     ratings = spark.createDataFrame(ratingsRDD) """

#     (training, test) = ratings.randomSplit([0.8, 0.2])

#     als = ALS(maxIter=30, regParam=0.3,rank=40,userCol="club_id", itemCol="bookID", ratingCol="Book-Rating",
#               coldStartStrategy="drop")
#     model = als.fit(training)
#     predictions_test = model.transform(test)
#     predictions_train = model.transform(training)
#     labelConverter = IndexToString(inputCol="bookID", outputCol="book_id",
#                                labels=indexer.labels)
#     evaluator = RegressionEvaluator(metricName="rmse", labelCol="Book-Rating",
#                                     predictionCol="prediction")
#     rmse_test = evaluator.evaluate(predictions_test)
#     rmse_train = evaluator.evaluate(predictions_train)
#     print("Root-mean-square error for test = " + str(rmse_test))
#     print("Root-mean-square error for train = " + str(rmse_train))


#     userRecs = model.recommendForAllUsers(10)

#     flatUserRecs = userRecs.withColumn("bookAndRating", explode(userRecs.recommendations)) \
#     .select ( "club_id", "bookAndRating.*")

#     flatUserRecs = labelConverter.transform(flatUserRecs).filter(userRecs['club_id'] == club_id)
#     user85Recs = flatUserRecs.collect()
#     # user85Recs.show()


#     spark.stop()

#     ml = BookLens()
#     ml.loadBookLensLatestSmall()
  
#     # print(len(user85Recs))

#     isbn_list = []

#     for row in user85Recs:
#         isbn_list.append(row['book_id'])

#     # for row in user85Recs:
#     #     print(ml.getBookName(row.book_id))

#     return(isbn_list)

# def test():
#     ClubBookAverageRating.objects.all().delete()

#     get_club_books_average_rating()
#     df = pd.DataFrame(list(ClubBookAverageRating.objects.all().values()))
#     df.to_csv("tessst.csv")
