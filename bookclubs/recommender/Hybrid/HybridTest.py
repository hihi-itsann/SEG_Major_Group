# -*- coding: utf-8 -*-
"""
Created on Thu May  3 11:11:13 2018

@author: Frank
"""

from bookclubs.recommender.Hybrid.BookLens import BookLens
from bookclubs.recommender.Hybrid.RBMAlgorithm import RBMAlgorithm
from bookclubs.recommender.Hybrid.ContentKNNAlgorithm import ContentKNNAlgorithm
from bookclubs.recommender.Hybrid.HybridAlgorithm import HybridAlgorithm
from bookclubs.recommender.Hybrid.Evaluator import Evaluator

import random
import numpy as np

def LoadBookLensData():
    ml = BookLens()
    print("Loading movie ratings...")
    data = ml.loadBookLensLatestSmall()
    print("\nComputing movie popularity ranks so we can measure novelty later...")
    rankings = ml.getPopularityRanks()
    return (ml, data, rankings)

np.random.seed(0)
random.seed(0)

# Load up common data set for the recommender algorithms
(ml, evaluationData, rankings) = LoadBookLensData()

# Construct an Evaluator to, you know, evaluate them
evaluator = Evaluator(evaluationData, rankings)

#Simple RBM
SimpleRBM = RBMAlgorithm(epochs=40)
#Content
ContentKNN = ContentKNNAlgorithm()

#Combine them
Hybrid = HybridAlgorithm([SimpleRBM, ContentKNN], [0.5, 0.5])

evaluator.AddAlgorithm(SimpleRBM, "RBM")
evaluator.AddAlgorithm(ContentKNN, "ContentKNN")
evaluator.AddAlgorithm(Hybrid, "Hybrid")

# Fight!
evaluator.Evaluate(False)

evaluator.SampleTopNRecs(ml)
