from __future__ import division
# Name: Jason Lustbader and Juliusz Choinski (jal584 and jcc068)
# Date: 5/24/15
# Description: make sure this file is in the same directory as the movie reviews!!!!
#
#

import math, os, pickle, re, nltk

class Bayes_Classifier:

    def __init__(self):
        """This method initializes and trains the Naive Bayes Sentiment Classifier.  If a
        cache of a trained classifier has been stored, it loads this cache.  Otherwise,
        the system will proceed through training.  After running this method, the classifier
        is ready to classify input text."""

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

    def train(self):
        """Trains the Naive Bayes Sentiment Classifier."""
        IFileList = []
        negWords = []
        posWords = []
        for fFileObj in os.walk("."):
            IFileList = fFileObj[2]
            print(IFileList)
            for file in IFileList[2:]:
                if re.search("movies-1", file):
                    review = self.loadFile(file)
                    yy = self.tokenize(review)
                    negWords.append(yy)

                elif re.search("movies-5", file):
                    review = self.loadFile(file)
                    posWords.append(self.tokenize(review))

                else:
                    print("The movie review didn't start with a 1 or 5.")
            break

        negWords = [item for sublist in negWords for item in sublist]
        posWords = [item for sublist in posWords for item in sublist]
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
        posSum = 0
        negSum = 0

        for token in tokText:
            posSum = posSum + math.log((float(self.posWords[token] + 1)) / (float(sum(self.posWords.values()) + 1)))
            negSum = negSum + math.log((float(self.negWords[token] + 1)) / (float(sum(self.negWords.values()) + 1)))

        epsilon = 0.5

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
