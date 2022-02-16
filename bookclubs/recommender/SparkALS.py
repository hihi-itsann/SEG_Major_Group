# -*- coding: utf-8 -*-
"""
Created on Mon May 28 11:09:55 2018

@author: Frank
"""

from pyspark.sql import SparkSession

from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.recommendation import ALS
from pyspark.sql import Row

from pyspark.ml.feature import StringIndexer, IndexToString

from BookLens import BookLens
import pandas as pd
from pyspark.sql.functions import explode

if __name__ == "__main__":
    spark = SparkSession\
        .builder\
        .appName("ALSExample")\
        .config("spark.executor.cores", '4')\
        .getOrCreate()

    print("yes")

    df = pd.read_csv('../dataset/BX-Book-Ratings.csv', sep = ';',names = ['User-ID', 'ISBN', 'Book-Rating'], quotechar = '"', encoding = 'latin-1',header = 0 )

    # df = pd.read_csv('../dataset/BX-Book-Ratings.csv', sep = ';',names = ['User-ID', 'ISBN', 'Book-Rating'], quotechar = '"', encoding = 'latin-1',header = 0 )
    # books = pd.read_csv('../dataset/BX-Books.csv', sep = ';',names = ['ISBN'], quotechar = '"', encoding = 'latin-1',header = 0 )
    # df["bookID"] = books.ISBN[books.ISBN == df.ISBN].index.tolist()[0]
    # print(df.head)

    # df.ISBN = df.ISBN.apply(lambda x: x[:-1] + "10" if x[-1] == "X" else x)
    # df = df[df.ISBN.str.isdecimal()]
    # df.ISBN = df.ISBN.apply(lambda x: int(x))
    print("yes")

    df = spark.createDataFrame(df)
    print("yes")

    indexer = StringIndexer(inputCol="ISBN", outputCol="bookID").fit(df)
    print("yes")

    indexed = indexer.transform(df)
    print("yes")

    indexed = indexed.repartition(100)
    print("yes")

    lines = indexed.rdd

    print("yes")

    ratingsRDD = lines.map(lambda p: Row(userId=int(p[0]), bookID=int(p[3]),
                                         rating=float(p[2])))


    print("yes")

    ratings = spark.createDataFrame(ratingsRDD)

    ratings = ratings.repartition(100)

    (training, test) = ratings.randomSplit([0.8, 0.2])
    print("yes")

    als = ALS(maxIter=5, regParam=0.01, userCol="userId", itemCol="bookID", ratingCol="rating",
              coldStartStrategy="drop")
    print("yes")

    model = als.fit(training)
    print("yes")

    predictions = model.transform(test)
    print("yes")


    labelConverter = IndexToString(inputCol="bookID", outputCol="ISBN",
                               labels=indexer.labels)

    # predictions = labelConverter.transform(predictions)
    #
    # predictions.show(10)


    evaluator = RegressionEvaluator(metricName="rmse", labelCol="rating",
                                    predictionCol="prediction")
    rmse = evaluator.evaluate(predictions)
    print("Root-mean-square error = " + str(rmse))


    userRecs = model.recommendForAllUsers(10)

    print("yes")

    flatUserRecs = userRecs.withColumn("songAndRating", explode(userRecs. recommendations)) \
    .select ( "userId", "songAndRating.*")

    flatUserRecs = labelConverter.transform(flatUserRecs)
    print("yes")


    user85Recs = flatUserRecs.filter(userRecs['userId'] == 276725).collect()
    # user85Recs.show()


    spark.stop()

    ml = BookLens()
    ml.loadBookLensLatestSmall()

    for row in user85Recs:
        print(ml.getBookName(row.ISBN))
