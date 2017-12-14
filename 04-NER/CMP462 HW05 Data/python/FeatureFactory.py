# -*- coding: utf-8 -*-

import json, sys
import base64
from Datum import Datum
import nltk
import pandas as pd

###### HERE rest my function ########
def special_case(word):
    #This function is used to return "upper" in the names like the following name:
    #McCagu
    for i in range(1, len(word)):
        if word[i].isupper() and word[i].lower()==word[i-1]:
            if word[0].isupper():
                return "Title"

    return "None"

def get_case(word):
    if word.islower():
        return "Lower"
    elif word.istitle():
        return "Title"
    elif word.isupper():
        return "Upper"
    else:
        return special_case(word)

def word_shape(word):
    hymen = True
    output = ""
    for ch in word:
        if ch.isupper():
            output += "X"
            if not hymen:
                hymen = True
        elif ch.islower() and hymen:
            output += "x"
            hymen = False
        elif ch.islower() and not hymen:
            pass
        elif ch.isdigit():
            output += "d"
            hymen = True
        else: 
            output += ch
            hymen = True
    return output

def has_unicode(word):
    for ch in word:
        ord(ch) > 128
        return True
    return False

def smart_find(word, sub):
    test = word.find(sub)
    if test == -1:
        return "False"
    else:
        return "True"



class FeatureFactory:
    """
    Add any necessary initialization steps for your features here
    Using this constructor is optional. Depending on your
    features, you may not need to intialize anything.
    """
    def __init__(self):
        n = pd.read_csv('male_and_female.csv')['name']
        self.names = set(n)

    """
    Words is a list of the words in the entire corpus, previousLabel is the label
    for position-1 (or O if it's the start of a new sentence), and position
    is the word you are adding features for. PreviousLabel must be the
    only label that is visible to this method. 
    """

    def computeFeatures(self, words, previousLabel, position, followingLabel):
        features = []
        currentWord = words[position]

        """ Baseline Features """
        features.append("word=" + currentWord)
        features.append("prevLabel=" + previousLabel)
        features.append("word=" + currentWord + ", prevLabel=" + previousLabel)
	"""
        Warning: If you encounter "line search failure" error when
        running the program, considering putting the baseline features
	back. It occurs when the features are too sparse. Once you have
        added enough features, take out the features that you don't need. 
	"""
	""" TODO: Add your features here """
        # features.append("followingLabel=" + followingLabel)
        features.append("word=" + currentWord + ", prevLabel=" + previousLabel + ", followingLabel=" + followingLabel)      
        # features.append('GreekLetters='+str(has_unicode(currentWord)))
        # features.append("wordShape"+word_shape(currentWord))

        if currentWord in self.names:
            features.append("NAME"+'True')
        else:
            features.append("NAME"+'False')

        if len(currentWord)==2 and currentWord[1] == '.':
            features.append("intial"+'True' + ", case="+get_case(currentWord))
        elif "'" in currentWord and "." in currentWord:
            features.append("intial"+'True' + ", case="+get_case(currentWord))
        else:
            features.append("intial'"+'False' + ", case="+get_case(currentWord))
        
        try:
            followingWord = words[position+1]
        except IndexError:
            followingWord = "none"

        if followingWord =="and":
            features.append("andBetween"+'True' + ", case="+get_case(currentWord))
        else:
            features.append("andBetween"+'False' + ", case="+get_case(currentWord))
        if currentWord in "'\"-,":
            features.append("punctuationBefore"+'True' + ", case="+get_case(followingWord))
        else:
            features.append("punctuationBefore"+'False' + ", case="+get_case(followingWord))

        # try:
        #     followingWord = words[position+1]
        #     if followingWord =="'s":
        #         features.append("'s_After'"+'True' + ", case="+get_case(currentWord))
        #     else:
        #         features.append("'s_After'"+'False' + ", case="+get_case(currentWord))
        # except IndexError:
        #     features.append("'s_After'"+'False' + ", case="+get_case(currentWord))
     
        

        # THE FOLLOWING TWO FEATURES TAKE SO MUCH TIME
        # if position > 0:
        #     previousWord = words[position-1]
        # else:
        #     previousWord = 'None'
        # features.append("POS="+nltk.pos_tag([currentWord])[0][1])
        # features.append("prevPOS="+nltk.pos_tag([previousWord])[0][1])
        
        
        return features

    """ Do not modify this method """
    def readData(self, filename):
        data = [] 
        
        for line in open(filename, 'r'):
            line_split = line.split()
            # remove emtpy lines
            if len(line_split) < 2:
                continue
            word = line_split[0]
            label = line_split[1]

            datum = Datum(word, label)
            data.append(datum)

        return data

    """ Do not modify this method """
    def readTestData(self, ch_aux):
        data = [] 
        
        for line in ch_aux.splitlines():
            line_split = line.split()
            # remove emtpy lines
            if len(line_split) < 2:
                continue
            word = line_split[0]
            label = line_split[1]

            datum = Datum(word, label)
            data.append(datum)

        return data


    """ Do not modify this method """
    def setFeaturesTrain(self, data):
        newData = []
        words = []

        for datum in data:
            words.append(datum.word)

        ## This is so that the feature factory code doesn't
        ## accidentally use the true label info
        previousLabel = "O"
        followingLabel = "O"
        for i in range(0, len(data)):
            datum = data[i]
            ## MY EDIT
            if i != len(data)-1:
                followingDatum = data[i+1]
            else:
                followingDatum = datum

            newDatum = Datum(datum.word, datum.label)
            newDatum.followingLabel = followingDatum.label
            newDatum.features = self.computeFeatures(words, previousLabel, i, followingDatum.label)
            newDatum.previousLabel = previousLabel
            newData.append(newDatum)
            previousLabel = datum.label

        return newData

    """
    Compute the features for all possible previous labels
    for Viterbi algorithm. Do not modify this method
    """
    def setFeaturesTest(self, data):
        newData = []
        words = []
        labels = []
        labelIndex = {}

        for datum in data:
            words.append(datum.word)
            if not labelIndex.has_key(datum.label):
                labelIndex[datum.label] = len(labels)
                labels.append(datum.label)
        
        ## This is so that the feature factory code doesn't
        ## accidentally use the true label info
        for i in range(0, len(data)):
            datum = data[i]
            if i != len(data)-1:
                followingDatum = data[i+1]
            else:
                followingDatum = datum

            if i == 0:
                previousLabel = "O"
                datum.features = self.computeFeatures(words, previousLabel, i, followingDatum.label)

                newDatum = Datum(datum.word, datum.label)
                newDatum.followingLabel = followingDatum.label
                newDatum.features = self.computeFeatures(words, previousLabel, i, followingDatum.label)
                newDatum.previousLabel = previousLabel
                newData.append(newDatum)
            else:
                for previousLabel in labels:
                    datum.features = self.computeFeatures(words, previousLabel, i, followingDatum.label)

                    newDatum = Datum(datum.word, datum.label)
                    newDatum.followingLabel = followingDatum.label
                    newDatum.features = self.computeFeatures(words, previousLabel, i, followingDatum.label)
                    newDatum.previousLabel = previousLabel
                    newData.append(newDatum)

        return newData

    """
    write words, labels, and features into a json file
    Do not modify this method
    """
    def writeData(self, data, filename):
        outFile = open(filename + '.json', 'w')
        for i in range(0, len(data)):
            datum = data[i]
            jsonObj = {}
            jsonObj['_label'] = datum.label
            jsonObj['_word']= base64.b64encode(datum.word)
            jsonObj['_prevLabel'] = datum.previousLabel

            featureObj = {}
            features = datum.features
            for j in range(0, len(features)):
                feature = features[j]
                featureObj['_'+feature] = feature
            jsonObj['_features'] = featureObj
            
            outFile.write(json.dumps(jsonObj) + '\n')
            
        outFile.close()

