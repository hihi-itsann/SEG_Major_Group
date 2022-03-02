# -*- coding: utf-8 -*-

from curses import BUTTON1_DOUBLE_CLICKED
from email import header
from os import sep
from pyspark.sql import Row
from pyspark.sql import SparkSession
from pyspark.ml.feature import StringIndexer, IndexToString
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.recommendation import ALS
from pyspark.sql.functions import explode
from BookLens import BookLens

import pandas as pd
import csv

from BookLens import BookLens


if __name__ == "__main__":
    spark = SparkSession\
        .builder\
        .appName("ALSExample")\
        .config("spark.executor.cores", '4')\
        .getOrCreate()

    spark.sparkContext.setCheckpointDir("/tmp/checkpoints")

    df = pd.read_csv('bookclubs/dataset/BX-Book-Ratings.csv', sep = ';',names = ['User-ID', 'ISBN', 'Book-Rating'], quotechar = '"', encoding = 'latin-1',header = 0 )
    df = df[df.loc[:]!=0].dropna()
    df.ISBN = df.ISBN.apply(lambda x: x[:-1] + "10" if x[-1] == "X" else x)
    df = df[df.ISBN.str.len() <= 11]
    df = spark.createDataFrame(df)

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
    predictions_test = model.transform(test)
    predictions_train = model.transform(training)
    labelConverter = IndexToString(inputCol="bookID", outputCol="ISBN",
                               labels=indexer.labels)
    evaluator = RegressionEvaluator(metricName="rmse", labelCol="Book-Rating",
                                    predictionCol="prediction")
    rmse_test = evaluator.evaluate(predictions_test)
    rmse_train = evaluator.evaluate(predictions_train)
    print("Root-mean-square error for test = " + str(rmse_test))
    print("Root-mean-square error for train = " + str(rmse_train))


    userRecs = model.recommendForAllUsers(10)

    flatUserRecs = userRecs.withColumn("bookAndRating", explode(userRecs.recommendations)) \
    .select ( "User-ID", "bookAndRating.*")

    flatUserRecs = labelConverter.transform(flatUserRecs).filter(userRecs['User-ID'] == 222906)
    user85Recs = flatUserRecs.collect()
    # user85Recs.show()


    spark.stop()

    ml = BookLens()
    ml.loadBookLensLatestSmall()
    print(len(user85Recs))
    

    for row in user85Recs:
        print(ml.getBookName(row.ISBN))

        
