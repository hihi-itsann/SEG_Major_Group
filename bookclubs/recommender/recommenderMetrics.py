import itertools

from surprise import accuracy
from collections import defaultdict

class RecommenderMetrics:

    def MAE(predictions):
        return accuracy.mae(predictions, verbose=False)

    def RMSE(predictions):
        return accuracy.rmse(predictions, verbose=False)

    def GetTopN(predictions, n=10, minimumRating=4.0):
        topN = defaultdict(list)


<<<<<<< HEAD
        for userID, isbn, actualRating, estimatedRating, _ in predictions:
            # print(isbn)
            if (estimatedRating >= minimumRating):
                topN[int(userID)].append((isbn, estimatedRating))
=======
        for userID, bookISBN, actualRating, estimatedRating, _ in predictions:
            if (estimatedRating >= minimumRating):
                topN[int(userID)].append((int(bookISBN), estimatedRating))
>>>>>>> c4047505c36492e38ce7ec85d13edd50508de6af

        for userID, ratings in topN.items():
            ratings.sort(key=lambda x: x[1], reverse=True)
            topN[int(userID)] = ratings[:n]

        return topN

    def HitRate(topNPredicted, leftOutPredictions):
        hits = 0
        total = 0

        # For each left-out rating
        for leftOut in leftOutPredictions:
            userID = leftOut[0]
<<<<<<< HEAD
            leftOutISBN = leftOut[1]
            # Is it in the predicted top 10 for this user?
            hit = False
            for isbn, predictedRating in topNPredicted[int(userID)]:
                if (leftOutISBN == isbn):
=======
            leftOutbookISBN = leftOut[1]
            # Is it in the predicted top 10 for this user?
            hit = False
            for bookISBN, predictedRating in topNPredicted[int(userID)]:
                if (int(leftOutbookISBN) == int(bookISBN)):
>>>>>>> c4047505c36492e38ce7ec85d13edd50508de6af
                    hit = True
                    break
            if (hit) :
                hits += 1

            total += 1

        # Compute overall precision
        return hits/total

    def CumulativeHitRate(topNPredicted, leftOutPredictions, ratingCutoff=0):
        hits = 0
        total = 0

        # For each left-out rating
<<<<<<< HEAD
        for userID, leftOutISBN, actualRating, estimatedRating, _ in leftOutPredictions:
=======
        for userID, leftOutbookISBN, actualRating, estimatedRating, _ in leftOutPredictions:
>>>>>>> c4047505c36492e38ce7ec85d13edd50508de6af
            # Only look at ability to recommend things the users actually liked...
            if (actualRating >= ratingCutoff):
                # Is it in the predicted top 10 for this user?
                hit = False
<<<<<<< HEAD
                for isbn, predictedRating in topNPredicted[int(userID)]:
                    if (leftOutISBN == isbn):
=======
                for bookISBN, predictedRating in topNPredicted[int(userID)]:
                    if (int(leftOutbookISBN) == bookISBN):
>>>>>>> c4047505c36492e38ce7ec85d13edd50508de6af
                        hit = True
                        break
                if (hit) :
                    hits += 1

                total += 1

        # Compute overall precision
        return hits/total

    def RatingHitRate(topNPredicted, leftOutPredictions):
        hits = defaultdict(float)
        total = defaultdict(float)

        # For each left-out rating
<<<<<<< HEAD
        for userID, leftOutISBN, actualRating, estimatedRating, _ in leftOutPredictions:
            # Is it in the predicted top N for this user?
            hit = False
            for isbn, predictedRating in topNPredicted[int(userID)]:
                if (leftOutISBN == isbn):
=======
        for userID, leftOutbookISBN, actualRating, estimatedRating, _ in leftOutPredictions:
            # Is it in the predicted top N for this user?
            hit = False
            for bookISBN, predictedRating in topNPredicted[int(userID)]:
                if (int(leftOutbookISBN) == bookISBN):
>>>>>>> c4047505c36492e38ce7ec85d13edd50508de6af
                    hit = True
                    break
            if (hit) :
                hits[actualRating] += 1

            total[actualRating] += 1

        # Compute overall precision
        for rating in sorted(hits.keys()):
            print (rating, hits[rating] / total[rating])

    def AverageReciprocalHitRank(topNPredicted, leftOutPredictions):
        summation = 0
        total = 0
        # For each left-out rating
<<<<<<< HEAD
        for userID, leftOutISBN, actualRating, estimatedRating, _ in leftOutPredictions:
            # Is it in the predicted top N for this user?
            hitRank = 0
            rank = 0
            for isbn, predictedRating in topNPredicted[int(userID)]:
                rank = rank + 1
                if (leftOutISBN == isbn):
=======
        for userID, leftOutbookISBN, actualRating, estimatedRating, _ in leftOutPredictions:
            # Is it in the predicted top N for this user?
            hitRank = 0
            rank = 0
            for bookISBN, predictedRating in topNPredicted[int(userID)]:
                rank = rank + 1
                if (int(leftOutbookISBN) == bookISBN):
>>>>>>> c4047505c36492e38ce7ec85d13edd50508de6af
                    hitRank = rank
                    break
            if (hitRank > 0) :
                summation += 1.0 / hitRank

            total += 1

        return summation / total

    # What percentage of users have at least one "good" recommendation
    def UserCoverage(topNPredicted, numUsers, ratingThreshold=0):
        hits = 0
        for userID in topNPredicted.keys():
            hit = False
<<<<<<< HEAD
            for isbn, predictedRating in topNPredicted[userID]:
=======
            for bookISBN, predictedRating in topNPredicted[userID]:
>>>>>>> c4047505c36492e38ce7ec85d13edd50508de6af
                if (predictedRating >= ratingThreshold):
                    hit = True
                    break
            if (hit):
                hits += 1

        return hits / numUsers

    def Diversity(topNPredicted, simsAlgo):
        n = 0
        total = 0
        simsMatrix = simsAlgo.compute_similarities()
        for userID in topNPredicted.keys():
            pairs = itertools.combinations(topNPredicted[userID], 2)
            for pair in pairs:
<<<<<<< HEAD
                movie1 = pair[0][0]
                movie2 = pair[1][0]
                innerID1 = simsAlgo.trainset.to_inner_iid(str(movie1))
                innerID2 = simsAlgo.trainset.to_inner_iid(str(movie2))
=======
                book1 = pair[0][0]
                book2 = pair[1][0]
                innerID1 = simsAlgo.trainset.to_inner_iid(str(book1))
                innerID2 = simsAlgo.trainset.to_inner_iid(str(book2))
>>>>>>> c4047505c36492e38ce7ec85d13edd50508de6af
                similarity = simsMatrix[innerID1][innerID2]
                total += similarity
                n += 1

        S = total / n
        return (1-S)

    def Novelty(topNPredicted, rankings):
        n = 0
        total = 0
        for userID in topNPredicted.keys():
            for rating in topNPredicted[userID]:
<<<<<<< HEAD
                isbn = rating[0]
                rank = rankings[isbn]
=======
                bookISBN = rating[0]
                rank = rankings[bookISBN]
>>>>>>> c4047505c36492e38ce7ec85d13edd50508de6af
                total += rank
                n += 1
        return total / n
