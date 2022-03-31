import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
from bookclubs.models import Book, ClubBookAverageRating, Club, BookRatingReview


def get_club_books_average_rating(clubID):
    """ Saves the average rating of books read by users of each club (banned member are not included) """
    club = Club.objects.get(id=clubID)
    members = club.get_moderators() | club.get_members() | club.get_management()
    for user in members:
        ratings = BookRatingReview.objects.all().filter(user=user)
        for rating in ratings:
            clubBookRating = ClubBookAverageRating.objects.all().filter(club=club, book=rating.book)
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


def get_data_for_recommendations(clubID):
    club_ratings = pd.DataFrame(list(ClubBookAverageRating.objects.all().values()))
    books = pd.DataFrame(list(Book.objects.all().values()))
    club_ratings['Book-Rating'] = club_ratings['rate'] / club_ratings['number_of_ratings']
    club_ratings['ISBN'] = club_ratings['book_id']
    club_ratings['User-ID'] = club_ratings['club_id']
    club_ratings = club_ratings.drop(columns=['id', 'club_id', 'book_id', 'rate', 'number_of_ratings'])
    ratings = pd.DataFrame(list(BookRatingReview.objects.all().values()))
    ratings['Book-Rating'] = ratings['rate']
    ratings['ISBN'] = ratings['book_id']
    ratings['User-ID'] = ratings['user_id']
    ratings = ratings.drop(columns=['id', 'user_id', 'book_id', 'rate', 'review', 'created_at'])

    ratings = pd.concat([club_ratings, csv_ratings, ratings])
    return (ratings, books)


def train():
    get_model(csv_ratings)


def get_model(ratings):
    user_ids = ratings["User-ID"].unique().tolist()
    user2user_encoded = {x: i for i, x in enumerate(user_ids)}
    book_ids = ratings["ISBN"].unique().tolist()
    book2book_encoded = {x: i for i, x in enumerate(book_ids)}
    book_encoded2book = {i: x for i, x in enumerate(book_ids)}
    ratings["user"] = ratings["User-ID"].map(user2user_encoded)
    ratings["book"] = ratings["ISBN"].map(book2book_encoded)

    num_users = len(user2user_encoded)
    num_books = len(book_encoded2book)
    ratings["rating"] = ratings["Book-Rating"].values.astype(np.float32)

    ratings = ratings.sample(frac=1, random_state=42)
    x = ratings[["user", "book"]].values
    y = ratings["rating"].values
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
            x = dot_user_book + user_bias + book_bias
            return tf.nn.sigmoid(x)

    model = RecommenderNet(num_users, num_books, EMBEDDING_SIZE)

    model.compile(optimizer="adam", loss=tf.keras.losses.MeanSquaredError(),
                  metrics=[tf.keras.metrics.TopKCategoricalAccuracy(k=1), tf.keras.metrics.RootMeanSquaredError()])

    model.fit(
        x=x_train,
        y=y_train,
        batch_size=65536,
        epochs=5,
        verbose=1,
        validation_data=(x_val, y_val),
    )
    return (model, user2user_encoded, book2book_encoded, book_encoded2book)


import operator


def get_10_books_with_highest_rating():
    book_ratings = pd.DataFrame(list(BookRatingReview.objects.all().values()))
    avg_book_rating = dict()
    for book in book_ratings['book_id']:
        if not avg_book_rating.get(book):
            avg_book_rating[book] = float((Book.objects.all().get(ISBN=book)).getAverageRate())
    sorted_d = dict(sorted(avg_book_rating.items(), key=operator.itemgetter(1), reverse=True))

    return list(sorted_d)[:10]


def get_recommendations(userID):
    global csv_ratings
    csv_ratings = pd.read_csv('bookclubs/dataset/BX-Book-Ratings.csv', sep=';', quotechar='"', encoding='latin-1',
                              header=0)
    csv_ratings = csv_ratings.loc[csv_ratings["Book-Rating"] != 0]

    train()

    ClubBookAverageRating.objects.all().delete()
    get_club_books_average_rating(userID)
    if len(ClubBookAverageRating.objects.all()) == 0:
        recommended_books = get_10_books_with_highest_rating()
        return recommended_books
    else:

        (ratings, books) = get_data_for_recommendations(userID)
        (model, user2user_encoded, book2book_encoded, book_encoded2book) = get_model(ratings)

        user_id = np.int64(userID)

        books_watched_by_user = ratings[ratings['User-ID'] == user_id]

        books_not_watched = books[
            ~books["ISBN"].isin(books_watched_by_user.ISBN.values)
        ]["ISBN"]

        if len(books_not_watched) == 0:
            return []
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

        recommended_books = books[books["ISBN"].isin(recommended_book_ids)]

        return recommended_books['ISBN']
