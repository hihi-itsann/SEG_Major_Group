from pyspark.sql import SparkSession
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.recommendation import ALS
from pyspark.sql import Row
from pyspark.ml.feature import StringIndexer, IndexToString
#from BookLens import BookLens
import pandas as pd
from pyspark.sql.functions import explode
from bookclubs.models import Book, ClubBookAverageRating, Club

import tensorflow_recommenders as tfrs
from typing import Dict, Text

import numpy as np
import tensorflow as tf
import tensorflow_datasets as tfds

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

def modelTrain(): #club_subject

    print("nice")
    ratings = pd.read_csv('bookclubs/dataset/BX-Book-Ratings.csv', sep = ';', quotechar = '"', encoding = 'latin-1',header = 0 ).head(10)
    ratings = tf.data.Dataset.from_tensor_slices((dict(ratings)))
    print("nice")
    books = pd.read_csv('bookclubs/dataset/BX-Books.csv', sep = ';', quotechar = '"', encoding = 'latin-1',header = 0 )[['ISBN']].head(10)
    books = tf.data.Dataset.from_tensor_slices((dict(books)))
    print("nice")

    ratings = ratings.map(lambda x: {
        "ISBN": x["ISBN"],
        "User-ID": x["User-ID"],
        # "Book-Rating": x["Book-Rating"]
    })
    books = books.map(lambda x: x["ISBN"])
    calculate_model(ratings,books)

def data_for_recommendations():
    print("hello")
    ClubBookAverageRating.objects.all().delete()

    get_club_books_average_rating()
    global ratings
    ratings = pd.DataFrame(list(ClubBookAverageRating.objects.all().values()))
    ratings['Book-Rating']=ratings['rate']/ratings['number_of_ratings']
    ratings['ISBN']=ratings['book_id']
    ratings['User-ID']=ratings['club_id']

    ratings = tf.data.Dataset.from_tensor_slices((dict(ratings)))

    global books
    books = pd.DataFrame(list(Book.objects.all().values()))[["ISBN"]]
    books = tf.data.Dataset.from_tensor_slices((dict(books)))
    books = books.map(lambda x: x["ISBN"])

    
def calculate_model(ratings, books):
    print("nice")
    isbn_vocabulary = tf.keras.layers.StringLookup()
    isbn_vocabulary.adapt(ratings.map(lambda x: x["ISBN"]))
    print("nice")
    isbn_vocabulary.adapt(books)
    print("nice")
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
    print("everything s fine")
    return model


def get_recommendations():
  # Use brute-force search to set up retrieval using the trained representations.

  #training
  modelTrain()

  
  data_for_recommendations()

  model=calculate_model(ratings,books)
  index = tfrs.layers.factorized_top_k.BruteForce(model.user_model)
  index.index_from_dataset(
      books.batch(100).map(lambda title: (title, model.movie_model(title))))

  # Get some recommendations.
  _, titles = index(np.array(["42"]))
  print(f"Top 3 recommendations for user 42: {titles[0, :3]}")



# Select the basic features.
