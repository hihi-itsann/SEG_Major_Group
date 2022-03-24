import numpy as np
import pandas as pd
import os
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.ml.recommendation import ALS, ALSModel
from pyspark.context import SparkContext
from pyspark.sql.session import SparkSession
from pyspark.mllib.evaluation import RegressionMetrics, RankingMetrics
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.tuning import ParamGridBuilder, CrossValidator
from pyspark import SparkFiles

sc = SparkContext('local')
spark = SparkSession(sc)
# continued failures led me to trim back on size of dataset - choose 10k
#df = pd.read_csv(self.ratingsPath, sep = ';',names = ['User-ID', 'ISBN', 'Book-Rating'], quotechar = '"', encoding = 'latin-1',header = 0 )
#books10k = pd.read_csv('bookclubs/ml-latest-small/BX_Books.csv', sep = ';',names = ['User-ID', 'ISBN', 'Book-Rating'], quotechar = '"', encoding = 'latin-1',header = 0 )
#ratings10k = pd.read_csv('bookclubs/ml-latest-small/BX-Book-Ratings.csv', sep = ';',names = ['User-ID', 'ISBN', 'Book-Rating'], quotechar = '"', encoding = 'latin-1',header = 0 )

books10k = spark.read.csv('bookclubs/ml-latest-small/BX_Books.csv', sep = ';',header = True)

ratings10k = spark.read.csv('bookclubs/ml-latest-small/BX-Book-Ratings.csv', sep = ';',header = True)
numerator = ratings10k.select('Book-Rating').count()
num_users = ratings10k.select("User-ID").distinct().count()
num_books = ratings10k.select("ISBN").distinct().count()
denominator = num_users * num_books
sparsity = (1.0 - (numerator * 1.0)/denominator) * 100

ratings10k.groupBy("ISBN").count().select(avg("count"))

ratings10k.groupBy("User-ID").count().select(avg("count"))
ratings10k=ratings10k.withColumnRenamed("User-ID","User").withColumnRenamed("Book-Rating","Rating")

ratings10k = ratings10k.select(ratings10k.User.cast("integer"),
                                        ratings10k.ISBN.cast("integer"),
                                        ratings10k.Rating.cast("float"))


ratings10k = ratings10k.filter(ratings10k.Rating ==0).drop()
# ratings10k.Book = ratings10k.Book.apply(lambda x: x[:-1] + "10" if x[-1] == "X" else x)
# ratings10k = ratings10k[ratings10k.Book.str.len() <= 11]
# ratings10k = spark.createDataFrame(ratings10k)

# correct the format to include zeros

users = ratings10k.select("User").distinct()
books = ratings10k.select("ISBN").distinct()

# Cross join users and products
cj = users.crossJoin(books)
ratings = cj.join(ratings10k, ["User", "ISBN"], "left").fillna(0)

(train, test) = ratings.randomSplit([0.80, 0.20], seed=731)

als_model = ALS(userCol = "User", itemCol = "ISBN", ratingCol = "Rating",
               nonnegative = True,
               coldStartStrategy = "drop",
               implicitPrefs = False)
model = als_model.fit(train)
predictions = model.transform(test)
evaluator = RegressionEvaluator(metricName = 'rmse', labelCol = 'Rating',
                               predictionCol = 'prediction')
rmse = evaluator.evaluate(predictions)
print("RMSE: "), rmse

# change rank only (chose 16 b/c it was recommended by Goodreads paper)
als_model2 = ALS(userCol = "User", itemCol = "ISBN", ratingCol = "Rating",
                 rank = 16, maxIter = 10, regParam = 1,
               nonnegative = True,
               coldStartStrategy = "drop",
               implicitPrefs = False)
model2 = als_model2.fit(train)
predictions2 = model2.transform(test)
evaluator = RegressionEvaluator(metricName = 'rmse', labelCol = 'Rating',
                               predictionCol = 'prediction')
rmse2 = evaluator.evaluate(predictions2)
print("RMSE: "), rmse2

param_grid = ParamGridBuilder().addGrid(als_model.rank, [5, 10, 15, 20]).addGrid(
    als_model.maxIter, [5, 10]).addGrid(als_model.regParam, [0.01, 0.05, 0.1, 0.15]).build()
evaluator = RegressionEvaluator(metricName = "rmse", labelCol = "Rating",
                               predictionCol = "prediction")
cv = CrossValidator(estimator = als_model,
                   estimatorParamMaps = param_grid,
                   evaluator = evaluator,
                   numFolds = 5)

modelcv = cv.fit(train)

best_model = modelcv.bestModel

test_predictions = best_model.transform(test)
rmse = evaluator.evaluate(test_predictions)
print(rmse)

# view recommendations
userRecs = best_model.recommendForAllUsers(10)


#
# # Look at user 60's ratings
# print("User 2's Ratings:")
# ratings.filter(col("User") == 2).sort("Book", ascending = False).show()
#
# # Look at the movies recommended to user 60
# print("User 2's Recommendations:")
# userRecs.filter(col("User") == 2).show()
#
# # Look at user 63's ratings
# print("User 63's Ratings:")
# ratings.filter(col("User") == 63).sort("Book", ascending = False).show()

# Look at the movies recommended to user 63
print("User 63's Recommendations:")
userRecs.filter(col("User") == 63).show()

exploded_recs = spark.sql("SELECT User, explode(recommendations) AS BookRec FROM ALS_recs_temp")
exploded_recs.show()
