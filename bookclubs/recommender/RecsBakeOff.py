# -*- coding: utf-8 -*-
"""
Created on Thu May  3 11:11:13 2018

@author: Frank
"""

from BookLens import BookLens
from surprise import SVD
from surprise import NormalPredictor
from Evaluator import Evaluator
# from ContentKNNAlgorithm import ContentKNNAlgorithm

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

# Construct an Evaluator to, you know, evaluate them
evaluator = Evaluator(evaluationData, rankings)

# Throw in an SVD recommender
SVDAlgorithm = SVD(random_state=10)
evaluator.AddAlgorithm(SVDAlgorithm, "SVD")

# contentKNN = ContentKNNAlgorithm()
# evaluator.AddAlgorithm(contentKNN, "ContentKNN")

# Just make random recommendations
Random = NormalPredictor()
evaluator.AddAlgorithm(Random, "Random")


# Fight!
evaluator.Evaluate(False)

evaluator.SampleTopNRecs(ml)
