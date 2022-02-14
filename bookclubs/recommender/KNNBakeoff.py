from BooksRecommender import BooksRecommender
from surprise import KNNBasic
from surprise import NormalPredictor
from Evaluator import Evaluator

import random
import numpy as np

def LoadBooksRecommenderData():
    ml = BooksRecommender()
    print("Loading movie ratings...")
    data = ml.loadBookRecommenderLatestSmall()
    print(data)
    print("\nComputing movie popularity ranks so we can measure novelty later...")
    rankings = ml.getPopularityRanks()
    return (ml, data, rankings)

np.random.seed(0)
random.seed(0)

# Load up common data set for the recommender algorithms
(ml, evaluationData, rankings) = LoadBooksRecommenderData()

# Construct an Evaluator to, you know, evaluate them
evaluator = Evaluator(evaluationData, rankings)

# User-based KNN
UserKNN = KNNBasic(sim_options = {'name': 'cosine', 'user_based': True})
evaluator.AddAlgorithm(UserKNN, "User KNN")

# Item-based KNN
ItemKNN = KNNBasic(sim_options = {'name': 'cosine', 'user_based': False})
evaluator.AddAlgorithm(ItemKNN, "Item KNN")

# Just make random recommendations
Random = NormalPredictor()
evaluator.AddAlgorithm(Random, "Random")

# Fight!
evaluator.Evaluate(False)

evaluator.SampleTopNRecs(ml)
