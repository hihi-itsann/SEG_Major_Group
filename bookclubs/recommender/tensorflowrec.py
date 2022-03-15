from pyspark.sql import SparkSession
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.recommendation import ALS
from pyspark.sql import Row
from pyspark.ml.feature import StringIndexer, IndexToString
from BookLens import BookLens
import pandas as pd
from pyspark.sql.functions import explode
# if __name__ == "__main__":
#     spark = SparkSession\
#         .builder\
#         .appName("ALSExample")\
#         .config("spark.executor.cores", '4')\
#         .getOrCreate()
#
#     spark.sparkContext.setCheckpointDir("/tmp/checkpoints")
#
#     df = pd.read_csv('../dataset/BX-Book-Ratings.csv', sep = ';',names = ['User-ID', 'ISBN', 'Book-Rating'], quotechar = '"', encoding = 'latin-1',header = 0 )
#     df = df[df.loc[:]!=0].dropna()
#     df = spark.createDataFrame(df)
#
#
#     indexer = StringIndexer(inputCol="ISBN", outputCol="bookID").fit(df)
#     indexed = indexer.transform(df)
#     ratings = indexed.drop("ISBN")
#
#     (training, test) = ratings.randomSplit([0.8, 0.2])
#
#     als = ALS(maxIter=5, regParam=0.01, userCol="User-ID", itemCol="bookID", ratingCol="Book-Rating",
#               coldStartStrategy="drop")
#     model = als.fit(training)
#     predictions = model.transform(test)
#     labelConverter = IndexToString(inputCol="bookID", outputCol="ISBN",
#                                labels=indexer.labels)
#     evaluator = RegressionEvaluator(metricName="rmse", labelCol="Book-Rating",
#                                     predictionCol="prediction")
#     rmse = evaluator.evaluate(predictions)
#     print("Root-mean-square error = " + str(rmse))
#
#
#     userRecs = model.recommendForAllUsers(10)
#
#     flatUserRecs = userRecs.withColumn("bookAndRating", explode(userRecs.recommendations)) \
#     .select ( "User-ID", "bookAndRating.*")
#
#     flatUserRecs = labelConverter.transform(flatUserRecs).filter(userRecs['User-ID'] == 276726)
#     user85Recs = flatUserRecs.collect()
#     # user85Recs.show()
#
#
#     spark.stop()
#     ml = BookLens()
#     ml.loadBookLensLatestSmall()
#     print(len(user85Recs))
#     for row in user85Recs:
#         print(ml.getBookName(row.ISBN))




# import tensorflow_datasets as tfds
import tensorflow_recommenders as tfrs
from typing import Dict, Text

import numpy as np
import tensorflow as tf
import tensorflow_datasets as tfds

print("nice")
ratings = pd.read_csv('../dataset/BX-Book-Ratings.csv', sep = ';', quotechar = '"', encoding = 'latin-1',header = 0 ).head(10)
ratings = tf.data.Dataset.from_tensor_slices((dict(ratings)))
print("nice")
books = pd.read_csv('../dataset/BX-Books.csv', sep = ';', quotechar = '"', encoding = 'latin-1',header = 0 )[['ISBN']].head(10)
books = tf.data.Dataset.from_tensor_slices((dict(books)))
print("nice")

ratings = ratings.map(lambda x: {
    "ISBN": x["ISBN"],
    "User-ID": x["User-ID"],
    # "Book-Rating": x["Book-Rating"]
})
books = books.map(lambda x: x["ISBN"])

print("nice")
isbn_vocabulary = tf.keras.layers.StringLookup()
isbn_vocabulary.adapt(ratings.map(lambda x: x["ISBN"]))
print("nice")
isbn_vocabulary.adapt(books)
print("nice")
class MovieLensModel(tfrs.Model):
  # We derive from a custom base class to help reduce boilerplate. Under the hood,
  # these are still plain Keras Models.

  def __init__(
      self,
      user_model: tf.keras.Model,
      movie_model: tf.keras.Model,
      task: tfrs.tasks.Retrieval):
    super().__init__()

    # Set up user and movie representations.
    self.user_model = user_model
    self.movie_model = movie_model

    # Set up a retrieval task.
    self.task = task

  def compute_loss(self, features: Dict[Text, tf.Tensor], training=False) -> tf.Tensor:
    # Define how the loss is computed.

    user_embeddings = self.user_model(features["User-ID"])
    movie_embeddings = self.movie_model(features["ISBN"])

    return self.task(user_embeddings, movie_embeddings)


user_model = tf.keras.Sequential([
    isbn_vocabulary,
    tf.keras.layers.Embedding(isbn_vocabulary.vocabulary_size(), 64)
])
movie_model = tf.keras.Sequential([
    isbn_vocabulary,
    tf.keras.layers.Embedding(isbn_vocabulary.vocabulary_size(), 64)
])

# Define your objectives.
task = tfrs.tasks.Retrieval(metrics=tfrs.metrics.FactorizedTopK(
    books.batch(128).map(movie_model)
  )
)

# Create a retrieval model.
model = MovieLensModel(user_model, movie_model, task)
model.compile(optimizer=tf.keras.optimizers.Adagrad(0.5))

# Train for 3 epochs.
model.fit(ratings.batch(4096), epochs=3)

# Use brute-force search to set up retrieval using the trained representations.
index = tfrs.layers.factorized_top_k.BruteForce(model.user_model)
index.index_from_dataset(
    books.batch(100).map(lambda title: (title, model.movie_model(title))))

# Get some recommendations.
_, titles = index(np.array(["42"]))
print(f"Top 3 recommendations for user 42: {titles[0, :3]}")



# Select the basic features.
