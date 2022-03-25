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
#from dkeras import dKeras
import numpy as np
#import ray
from bookclubs.models import Book, ClubBookAverageRating, Club,BookRatingReview

def get_selected_club_books_average_ratings(club_id):
    ClubBookAverageRating.objects.all().delete()

    club = Club.objects.filter(id = club_id).first()
    members = club.get_moderators()|club.get_members()|club.get_management()
    for user in members:
        ratings = BookRatingReview.objects.all().filter(user=user)
        for rating in ratings:
            clubBookRating=ClubBookAverageRating.objects.all().filter(user=user,book=rating.book)
            if clubBookRating:
                clubBookRating.get().add_rating(clubBookRating.get().rate)
                clubBookRating.get().increment_number_of_ratings()
            else:
                ClubBookAverageRating.objects.create(
                user=user,
                book=rating.book,
                rate=rating.rate,
                number_of_ratings=1 #calculating the number of ratings giving in the club
                )

def get_data_for_recommendations():

    ratings = pd.DataFrame(list(ClubBookAverageRating.objects.all().values()))
    books = pd.DataFrame(list(Book.objects.all().values()))
    ratings['Book-Rating']=ratings['rate']/ratings['number_of_ratings']
    ratings['ISBN']=ratings['book_id']
    ratings['User-ID']=ratings['club_id']

    allratings = pd.read_csv('bookclubs/dataset/BX-Book-Ratings.csv', sep = ';', quotechar = '"', encoding = 'latin-1',header = 0)
    allbooks = pd.read_csv('bookclubs/dataset/BX-Books.csv', sep = ';', quotechar = '"', encoding = 'latin-1',header = 0 )
    ratings = pd.concat([ratings,allratings])
    books = pd.concat([books,allbooks])

    return (ratings, books)

def train():
    ratings = pd.read_csv('bookclubs/dataset/BX-Book-Ratings.csv', sep = ';', quotechar = '"', encoding = 'latin-1',header = 0 )
    books = pd.read_csv('bookclubs/dataset/BX-Books.csv', sep = ';', quotechar = '"', encoding = 'latin-1',header = 0 )
    ratings = ratings.loc[ratings["Book-Rating"] != 0]
    get_model(ratings)

def get_model(ratings):
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
    return (model,user2user_encoded,book2book_encoded,book_encoded2book)

def get_recommendations(userID):

    train()
    (ratings, books)=get_data_for_recommendations()
    (model,user2user_encoded,book2book_encoded,book_encoded2book)=get_model(ratings)
   

    user_id = np.int64(userID)

    books_watched_by_user = ratings[ratings['User-ID'] == user_id]
    # print(len(books_watched_by_user))
    # if (len(books_watched_by_user) == 0) :
    #     return []

    books_not_watched = books[
        ~books["ISBN"].isin(books_watched_by_user.ISBN.values)
    ]["ISBN"]

    #this means that club has read all books so there is no book to recommend
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
    


    # print("----" * 8)
    # print("Top 10 book recommendations")
    # print("----" * 8)
    recommended_books = books[books["ISBN"].isin(recommended_book_ids)]
    
    print(recommended_books['ISBN'])
    return recommended_books['ISBN']

