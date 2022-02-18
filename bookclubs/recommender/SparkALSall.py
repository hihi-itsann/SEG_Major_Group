# -*- coding: utf-8 -*-

from pyspark import Row
from pyspark.sql import SparkSession
from pyspark.ml.feature import StringIndexer, IndexToString
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.recommendation import ALS
from pyspark.context import SparkContext
from pyspark.sql.functions import explode

import pandas as pd
import csv

from BookLens import BookLens


if __name__ == "__main__":
    spark = SparkSession\
        .builder\
        .appName("ALSExample")\
        .config("spark.executor.cores", '4')\
        .config("spark.executor.memory", '10G')\
        .config("spark.executor.memoryOverhead", '1G')\
        .getOrCreate()

    df = pd.read_csv('bookclubs/dataset/BX-Book-Ratings.csv', sep = ';',names = ['User-ID', 'ISBN', 'Book-Rating'], quotechar = '"', encoding = 'latin-1',header = 0)
    df = df[df.loc[:]!=0].dropna()
    # df = pd.read_csv('../dataset/BX-Book-Ratings.csv', sep = ';',names = ['User-ID', 'ISBN', 'Book-Rating'], quotechar = '"', encoding = 'latin-1',header = 0 )
    # books = pd.read_csv('../dataset/BX-Books.csv', sep = ';',names = ['ISBN'], quotechar = '"', encoding = 'latin-1',header = 0 )
    # df["bookID"] = books.ISBN[books.ISBN == df.ISBN].index.tolist()[0]
    # print(df.head)

    # df.ISBN = df.ISBN.apply(lambda x: x[:-1] + "10" if x[-1] == "X" else x)
    # df = df[df.ISBN.str.isdecimal()]
    # df.ISBN = df.ISBN.apply(lambda x: int(x))
    df = spark.createDataFrame(df).repartition(1000)

    indexer = StringIndexer(inputCol="ISBN", outputCol="bookID").fit(df)
    indexed = indexer.transform(df)
    indexed.show()


    lines = indexed.rdd

    # print("yes")

    ratingsRDD = lines.map(lambda p: Row(userId=int(p[0]), bookID=int(p[3]),
                                         rating=float(p[2])))

    ratings = spark.createDataFrame(ratingsRDD)

    (training, test) = ratings.randomSplit([0.75, 0.25])

    training.cache()
    test.cache()

    als = ALS(maxIter=5, regParam=0.01, userCol="userId", itemCol="bookID", ratingCol="rating",
              coldStartStrategy="drop")

    model = als.fit(training)

    predictions = model.transform(test)

    labelConverter = IndexToString(inputCol="bookID", outputCol="ISBN",
                               labels=indexer.labels)

    evaluator = RegressionEvaluator(metricName="rmse", labelCol="rating",
                                    predictionCol="prediction")

    rmse = evaluator.evaluate(predictions)

    print("Root-mean-square error = " + str(rmse))

    userRecs = model.recommendForAllUsers(10)

    flatUserRecs = userRecs.withColumn("songAndRating", explode(userRecs. recommendations)) \
    .select ( "userId", "songAndRating.*")

    flatUserRecs = labelConverter.transform(flatUserRecs)
    flatUserRecs.show()
    user85Recs = flatUserRecs.filter(userRecs['userId'] == 85).collect()
    # user85Recs.show()
    # print(user85Recs)

    spark.stop()
    
    ml = BookLens()
    ml.loadBookLensLatestSmall()
 
    for row in user85Recs:
        print(ml.getBookName(row.ISBN)+ ", ISBN：" + (row.ISBN))

