from __future__ import division
# Name: Jason Lustbader and Juliusz Choinski (jal584 and jcc068)
# Date: 5/24/15
# Description: make sure this file is in the same directory as the movie reviews!!!!
#
#

import math, os, pickle, re, nltk
from random import shuffle

class Bayes_Classifier:

    def __init__(self, testing = False):
        """This method initializes and trains the Naive Bayes Sentiment Classifier.  If a
        cache of a trained classifier has been stored, it loads this cache.  Otherwise,
        the system will proceed through training.  After running this method, the classifier
        is ready to classify input text."""

        if testing:
            self.train(testing)
            return

        try:
            f = open("posFreq.dat", "r")
            u = pickle.Unpickler(f)
            self.posWords = u.load()
            f.close()

            f = open("negFreq.dat", "r")
            u = pickle.Unpickler(f)
            self.negWords = u.load()
            f.close()

        except IOError:
            print "Hasn't been trained yet"
            self.train()

    def train(self, testing = None):
        """Trains the Naive Bayes Sentiment Classifier."""
        IFileList = []
        negWords = []
        posWords = []

        if not testing:
            for fFileObj in os.walk("."):
                IFileList = fFileObj[2]
                print(IFileList)
                for file in IFileList[2:]:
                    if re.search('movies\u20131', file):
                        review = self.loadFile(file)
                        yy = self.tokenize(review)
                        negWords.append(yy)

                    elif re.search('movies\u20135', file):
                        review = self.loadFile(file)
                        posWords.append(self.tokenize(review))

                    else:
                        print("The movie review didn't start with a 1 or 5.")
                break
            negWords = [item for sublist in negWords for item in sublist]
            posWords = [item for sublist in posWords for item in sublist]

            mostCommon = [',', '.', 'the', 'of', 'and', 'to', 'a', 'in', 'for', 'is', 'on', 'that', 'by', 'this', 'with', 'I',
                      'you', 'it', 'not', 'or', 'be', 'are', 'from', 'at', 'as', 'your', 'all', 'have', 'new', 'more', 'an', 'was']
    
            for word in negWords:
                if word in mostCommon:
                    negWords.remove(word)

            for word in posWords:
                if word in mostCommon:
                    posWords.remove(word)
        else: #if training for 10 fold cross validation

            mostCommon = [',', '.', 'the', 'of', 'and', 'to', 'a', 'in', 'for', 'is', 'on', 'that', 'by', 'this', 'with', 'I',
                      'you', 'it', 'not', 'or', 'be', 'are', 'from', 'at', 'as', 'your', 'all', 'have', 'new', 'more', 'an', 'was']

            for file in testing:
                if "movies-1" in file:
                    review = self.loadFile(file)
                    yy = self.tokenize(review)
                    for i in yy:
                        if i not in mostCommon:
                            negWords.append(i)

                elif "movies-5" in file:
                    review = self.loadFile(file)
                    yy = self.tokenize(review)
                    for i in yy:
                        if i not in mostCommon:
                            posWords.append(i)

                else:
                    print("The movie review didn't start with a 1 or 5.")

                #negWords = negWords[0]
                #posWords = posWords[0]



        negFreq = nltk.FreqDist(negWords)
        posFreq = nltk.FreqDist(posWords)
        print posFreq
        print negFreq
        f = open("posFreq.dat", "w")
        p = pickle.Pickler(f)
        p.dump(posFreq)
        f.close()
        f = open("negFreq.dat", "w")
        p = pickle.Pickler(f)
        p.dump(negFreq)
        f.close()
        self.negWords = negFreq
        self.posWords = posFreq


    def classify(self, sText):
        """Given a target string sText, this function returns the most likely document
        class to which the target string belongs (i.e., positive, negative or neutral).
        """
        tokText = self.tokenize(sText)
        posSum = 0.0
        negSum = 0.0

        for token in tokText:
            posSum = posSum + math.log((float(self.posWords[token] + 1)) / (float(sum(self.posWords.values()) + 1)))
            negSum = negSum + math.log((float(self.negWords[token] + 1)) / (float(sum(self.negWords.values()) + 1)))

        epsilon = 0.25

        if posSum > negSum and posSum - negSum > epsilon:
            return "positive"
        elif negSum > posSum and negSum - posSum > epsilon:
            return "negative"
        else:
            return "neutral"



    def loadFile(self, sFilename):
        """Given a file name, return the contents of the file as a string."""

        f = open(sFilename, "r")
        sTxt = f.read()
        f.close()
        return sTxt

    def save(self, dObj, sFilename):
        """Given an object and a file name, write the object to the file using pickle."""

        f = open(sFilename, "w")
        p = pickle.Pickler(f)
        p.dump(dObj)
        f.close()

    def load(self, sFilename):
        """Given a file name, load and return the object stored in the file."""

        f = open(sFilename, "r")
        u = pickle.Unpickler(f)
        dObj = u.load()
        f.close()
        return dObj

    def tokenize(self, sText):
        """Given a string of text sText, returns a list of the individual tokens that
        occur in that string (in order)."""

        lTokens = []
        sToken = ""
        for c in sText:
            if re.match("[a-zA-Z0-9]", str(c)) != None or c == "\"" or c == "_" or c == "-":
                sToken += c
            else:
                if sToken != "":
                    lTokens.append(sToken)
                    sToken = ""
                if c.strip() != "":
                    lTokens.append(str(c.strip()))

        if sToken != "":
            lTokens.append(sToken)

        return lTokens

"""
def testingxoxo():
    """does 10 fold cross validation to test"""
    training = []
    for fFileObj in os.walk("."):
        training.append(fFileObj[2])

    training = [item for sublist in training for item in sublist]
    training = training[4:]
    shuffle(training)

    num_folds = 10
    subset_size = int(len(training)/num_folds)
    trueP = 0
    falseP = 0
    falseN = 0

    for i in range(num_folds):
        testing_this_round = (training[i*subset_size:])[:subset_size]
        training_this_round = training[:i*subset_size] + training[(i+1)*subset_size:]

        tester = Bayes_Classifier(training_this_round)

        for file in testing_this_round:
            if ("movies-5" in file):
                if tester.classify(tester.loadFile(file)) == 'positive':
                    trueP = trueP + 1
                else:
                    falseN = falseN + 1

            elif ("movies-1" in file):
                if tester.classify(tester.loadFile(file)) == 'positive':
                    falseP = falseP + 1


    print trueP
    print falseP
    print falseN

"""
#testingxoxo()




