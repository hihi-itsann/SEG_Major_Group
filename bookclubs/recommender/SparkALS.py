# -*- coding: utf-8 -*-
"""
Created on Mon May 28 11:09:55 2018

@author: Frank
"""

from pyspark.sql import SparkSession
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.recommendation import ALS
from pyspark.sql import Row

from pyspark.ml.feature import StringIndexer, IndexToString, FeatureHasher

from BookLens import BookLens
import pandas as pd
from pyspark.sql.functions import explode

if __name__ == "__main__":
    spark = SparkSession\
        .builder\
        .appName("ALSExample")\
        .config("spark.executor.cores", '4')\
        .getOrCreate()

    spark.sparkContext.setCheckpointDir("/tmp/checkpoints")

    df = pd.read_csv('bookclubs/dataset/BX-Book-Ratings.csv', sep = ';',names = ['User-ID', 'ISBN', 'Book-Rating'], quotechar = '"', encoding = 'latin-1',header = 0 ).head(10000)
    df = df[df.loc[:]!=0].dropna()
    df = spark.createDataFrame(df)


    indexer = StringIndexer(inputCol="ISBN", outputCol="bookID").fit(df)
    indexed = indexer.transform(df)
    ratings = indexed.drop("ISBN")

    (training, test) = ratings.randomSplit([0.8, 0.2])

    als = ALS(maxIter=5, regParam=0.01, userCol="User-ID", itemCol="bookID", ratingCol="Book-Rating",
              coldStartStrategy="drop")
    model = als.fit(training)
    predictions = model.transform(test)
    labelConverter = IndexToString(inputCol="bookID", outputCol="ISBN",
                               labels=indexer.labels)
    evaluator = RegressionEvaluator(metricName="rmse", labelCol="Book-Rating",
                                    predictionCol="prediction")
    rmse = evaluator.evaluate(predictions)
    print("Root-mean-square error = " + str(rmse))


    userRecs = model.recommendForAllUsers(10)

    flatUserRecs = userRecs.withColumn("bookAndRating", explode(userRecs.recommendations)) \
    .select ( "User-ID", "bookAndRating.*")

    flatUserRecs = labelConverter.transform(flatUserRecs).filter(userRecs['User-ID'] == 276726)
    user85Recs = flatUserRecs.collect()
    # user85Recs.show()


    spark.stop()

    ml = BookLens()
    ml.loadBookLensLatestSmall()
    print(len(user85Recs))

    for row in user85Recs:
        print(ml.getBookName(row.ISBN))
