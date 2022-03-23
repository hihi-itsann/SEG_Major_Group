# -*- coding: utf-8 -*-
"""
Created on Thu May  3 11:11:13 2018

@author: Frank
"""

from BookLens import BookLens
from surprise import KNNBasic
from surprise import NormalPredictor
from Evaluator import Evaluator

import random
import numpy as np

def LoadBookLensData():
    ml = BookLens()
    print("Loading book ratings...")
    data = ml.loadBookLensLatestSmall()
    print("\nComputing book popularity ranks so we can measure novelty later...")
    rankings = ml.getPopularityRanks()
    return (ml, data, rankings)

np.random.seed(0)
random.seed(0)

# Load up common data set for the recommender algorithms
(ml, evaluationData, rankings) = LoadBookLensData()
print("after loadbooklens")
# Construct an Evaluator to, you know, evaluate them
evaluator = Evaluator(evaluationData, rankings)
print("after evaluator")
# User-based KNN
UserKNN = KNNBasic(sim_options = {'name': 'cosine', 'user_based': True})
evaluator.AddAlgorithm(UserKNN, "User KNN")
print("after knnbasic")
# # Item-based KNN
# ItemKNN = KNNBasic(sim_options = {'name': 'cosine', 'user_based': False})
# evaluator.AddAlgorithm(ItemKNN, "Item KNN")

# print("after random")
# # Fight!
# evaluator.Evaluate(False)
# print("after evaluate")
evaluator.SampleTopNRecs(ml)
print("after simp")