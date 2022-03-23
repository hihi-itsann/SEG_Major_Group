import pandas as pd
import numpy as np
from zipfile import ZipFile
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from pathlib import Path
import matplotlib.pyplot as plt
from keras import backend as K
from tensorflow.keras.applications import ResNet50
from dkeras import dKeras
import numpy as np
import ray

def getTenISBN(userID):

    ratings = pd.read_csv('../dataset/BX-Book-Ratings.csv', sep = ';', quotechar = '"', encoding = 'latin-1',header = 0 )
    books = pd.read_csv('../dataset/BX-Books.csv', sep = ';', quotechar = '"', encoding = 'latin-1',header = 0 )
    ratings = ratings.loc[ratings["Book-Rating"] != 0]

    user_ids = ratings["User-ID"].unique().tolist()
    user2user_encoded = {x: i for i, x in enumerate(user_ids)}
    userencoded2user = {i: x for i, x in enumerate(user_ids)}
    book_ids = ratings["ISBN"].unique().tolist()
    book2book_encoded = {x: i for i, x in enumerate(book_ids)}
    book_encoded2book = {i: x for i, x in enumerate(book_ids)}
    ratings["user"] = ratings["User-ID"].map(user2user_encoded)
    ratings["book"] = ratings["ISBN"].map(book2book_encoded)

    num_users = len(user2user_encoded)
    num_books = len(book_encoded2book)
    ratings["rating"] = ratings["Book-Rating"].values.astype(np.float32)
    # min and max ratings will be used to normalize the ratings later
    min_rating = min(ratings["rating"])
    max_rating = max(ratings["rating"])

    # print(
    #     "Number of users: {}, Number of Books: {}, Min rating: {}, Max rating: {}".format(
    #         num_users, num_books, min_rating, max_rating
    #     )
    # )

    ratings = ratings.sample(frac=1, random_state=42)
    x = ratings[["user", "book"]].values
    # Normalize the targets between 0 and 1. Makes it easy to train.
    # y = ratings["rating"].apply(lambda x: (x - min_rating) / (max_rating - min_rating)).values
    y = ratings["rating"].values
    # Assuming training on 90% of the data and validating on 10%.
    train_indices = int(0.6 * ratings.shape[0])
    x_train, x_val, y_train, y_val = (
        x[:train_indices],
        x[train_indices:],
        y[:train_indices],
        y[train_indices:],
    )


    EMBEDDING_SIZE = 50


    class RecommenderNet(keras.Model):
        def __init__(self, num_users, num_books, embedding_size, **kwargs):
            super(RecommenderNet, self).__init__(**kwargs)
            self.num_users = num_users
            self.num_books = num_books
            self.embedding_size = embedding_size
            self.user_embedding = layers.Embedding(
                num_users,
                embedding_size,
                embeddings_initializer="he_normal",
                embeddings_regularizer=keras.regularizers.l2(1e-6),
            )
            self.user_bias = layers.Embedding(num_users, 1)
            self.book_embedding = layers.Embedding(
                num_books,
                embedding_size,
                embeddings_initializer="he_normal",
                embeddings_regularizer=keras.regularizers.l2(1e-6),
            )
            self.book_bias = layers.Embedding(num_books, 1)

        def call(self, inputs):
            user_vector = self.user_embedding(inputs[:, 0])
            user_bias = self.user_bias(inputs[:, 0])
            book_vector = self.book_embedding(inputs[:, 1])
            book_bias = self.book_bias(inputs[:, 1])
            dot_user_book = tf.tensordot(user_vector, book_vector, 2)
            # Add all the components (including bias)
            x = dot_user_book + user_bias + book_bias
            # The sigmoid activation forces the rating to between 0 and 1
            return tf.nn.sigmoid(x)


    model = RecommenderNet(num_users, num_books, EMBEDDING_SIZE)

    model.compile(optimizer = "adam", loss = tf.keras.losses.MeanSquaredError(),
                  metrics =[tf.keras.metrics.TopKCategoricalAccuracy(k=1), tf.keras.metrics.RootMeanSquaredError()])

    history = model.fit(
        x=x_train,
        y=y_train,
        batch_size=65536,
        epochs=5,
        verbose=1,
        validation_data=(x_val, y_val),
    )

    user_id = userID

    books_watched_by_user = ratings[ratings['User-ID'] == user_id]
    if (len(books_watched_by_user) == 0) :
        return []

    books_not_watched = books[
        ~books["ISBN"].isin(books_watched_by_user.ISBN.values)
    ]["ISBN"]

    books_not_watched = list(
        set(books_not_watched).intersection(set(book2book_encoded.keys()))
    )

    books_not_watched = [[book2book_encoded.get(x)] for x in books_not_watched]
    user_encoder = user2user_encoded.get(user_id)
    user_book_array = np.hstack(
        ([[user_encoder]] * len(books_not_watched), books_not_watched)
    )
    ratings = model.predict(user_book_array).flatten()
    top_ratings_indices = ratings.argsort()[-10:][::-1]

    recommended_book_ids = [
        book_encoded2book.get(books_not_watched[x][0]) for x in top_ratings_indices
    ]

    return recommended_book_ids

getTenISBN(11677)
