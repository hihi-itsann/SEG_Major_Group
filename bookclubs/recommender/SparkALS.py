# -*- coding: utf-8 -*-
"""
Created on Mon May 28 11:09:55 2018

@author: Frank
"""

from pyspark.sql import SparkSession

from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.recommendation import ALS
from pyspark.sql import Row

from BookLens import BookLens
import pandas as pd

if __name__ == "__main__":
    spark = SparkSession\
        .builder\
        .appName("ALSExample")\
        .getOrCreate()

    df = pd.read_csv('../dataset/BX-Book-Ratings.csv', sep = ';',names = ['User-ID', 'ISBN', 'Book-Rating'], quotechar = '"', encoding = 'latin-1',header = 0 )

    df.ISBN = df.ISBN.apply(lambda x: x[:-1] + "10" if x[-1] == "X" else x)
    df = df[df.ISBN.str.isdecimal()]
    df.ISBN = df.ISBN.apply(lambda x: int(x))


    lines = spark.createDataFrame(df).rdd

    ratingsRDD = lines.map(lambda p: Row(userId=int(p[0]), isbn=int(p[1]),
                                         rating=float(p[2])))

    ratings = spark.createDataFrame(ratingsRDD)

    (training, test) = ratings.randomSplit([0.8, 0.2])

    als = ALS(maxIter=5, regParam=0.01, userCol="userId", itemCol="isbn", ratingCol="rating",
              coldStartStrategy="drop")
    model = als.fit(training)

    predictions = model.transform(test)
    evaluator = RegressionEvaluator(metricName="rmse", labelCol="rating",
                                    predictionCol="prediction")
    rmse = evaluator.evaluate(predictions)
    print("Root-mean-square error = " + str(rmse))

    userRecs = model.recommendForAllUsers(10)

    user85Recs = userRecs.filter(userRecs['userId'] == 85).collect()

    spark.stop()

    ml = BookLens()
    ml.loadMovieLensLatestSmall()

    for row in user85Recs:
        for rec in row.recommendations:
            print(ml.getBookName(rec.ISBN))
