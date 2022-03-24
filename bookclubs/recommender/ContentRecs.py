# -*- coding: utf-8 -*-
"""
Created on Fri May  4 16:25:39 2018

@author: Frank
"""


from BookLens import BookLens
from ContentKNNAlgorithm import ContentKNNAlgorithm
from Evaluator import Evaluator
from surprise import NormalPredictor

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
print("before evaluate")

# Construct an Evaluator to, you know, evaluate them
evaluator = Evaluator(evaluationData, rankings)
print("after evaluator")
contentKNN = ContentKNNAlgorithm()
evaluator.AddAlgorithm(contentKNN, "ContentKNN")


evaluator.SampleTopNRecs(ml)


