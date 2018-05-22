# Introduction

This directory contains three files beside the README.md file:

- `CMP462 HW03 Sentiment.pdf` file which contains a full description of the project.
- `CMP462 HW03 Data.zip` compressed file which has the project before being solved. (raw project)
- `CMP462 HW03 Data` folder which contains the project after being solved.

Special Thanks to:

- Prof. Danial Jurfasky and Christopher Manning for creating such an awesome project.
- Dr. Mohamed Aly for providing a full description of the project after being deleted from Coursera's Database.

---

# Description

Train a Naïve Bayes classifier on the imdb1 data set provided with the starter code. The starter code comes already set up for 10-fold cross-validation training and testing on this data. Recall that cross-validation involves dividing the data into several sections (10 in this case), then training and testing the classifier repeatedly, with a different section as the held-out test set each time. Your final accuracy is the average of the 10 runs. 

When using a movie review for training, you use the fact that it is positive or negative (the hand-labeled "true class") to help compute the correct statistics. But when the same review is used for testing, you only use this label to compute your accuracy. 

Our task is to implement the classifier training and testing code and evaluate them using the cross-validation mechanism. Next, evaluate your model again with the stop words removed. Does this approach affect average accuracy (for the current given data set)?



## Data

This is the actual Internet Movie Database review data used in the original Pang and Lee paper. So, the data of this project is a bunch of files, each file contain a review for a certain movie. The data is divided into two groups:

- `../data/pos`: which contains the files that are considered to be positive reviews for some movies.
- `../data/neg`: which contains the files that are considered to be negative reviews for some movies.



## Provided Code

There is only one file that is provided which is `NaiveBayes.py`. This file has just one class `NaiveBayes()` class. It class has two other classes in it:

  - **`Example()`**: 
    This class represents a document with a label. This class has two member variables in it:
    * `klass`: which is a string that takes just two values, either 'pos' as positive or 'neg' as negative.
    * `words`: which is a list of strings

  - **`TrainSplit`**: 
    This class represents a set of training/testing data and it has two variables as well:
    * `train`: which is a list of examples that are related to the TRAIN dataset.
    * `test`: which is a list of examples that are related to the TEST dataset.

The NaiveBayes classifier has three member variables in it:

* `FILTER_STOP_WORDS`: 
    It's a boolean variable. If it is set to 'True', then the Classifier will filter the stop words. And if it is set to 'False', then the calssifer won't filter the stop words.
* `stopList`: 
    It is a set of the stop words that are read from the file in `../data/english.stop` directory. This set will be used if the `FILTER_STOP_WORDS` variable is True.
* `numFolds`: 
    It is the number of folds, the default value is already set up for 10-fold cross-validation training and testing on this data. 
    Recall that cross-validation involves dividing the data into several sections (10 in this case), then training and testing the classifier repeatedly, with a different section as the held-out test set each time. The final accuracy is the average of the 10 runs. 

Now, let's talk about the methods that NaiveBayes classifier has:
- **`readfile(filename) & segmentWords()`**: 
    These two methods are used to read the `fielname` of the dataset.

- **`buildSplits()`**: 
    This method takes nothing and return `TrainSplit` instance. It splits the whole data into two parts (Train dataset 90% and Test dataset 10%). 

- **`trainSplit(trainDir)`**: 
    This method takes the training directory which is `../data/imdb1/` and returns one `TrainSplit` object that has the two kinds of data 'pos' and 'neg'.

- **`train(TrainSplit)`**: 
    This method take a `TrainSplit` object as an argument, and it filters the stop-words, if it was enabled, and returns nothing.




# My Solution

My solution to this project is done by implementing some methods:

- **`addExample(klass, words)`**:
  This method takes two inputs, `klass` which is a string that says that the following list of strings `words` should be considered as positive or negative.
- **`classify(words)`**:
  Takes a list of strings as an input, and counts the score of these words. Then, it returns either `pos` if the positive score was bigger than the negative score or `neg` otherwise. The score is calculated by summing the log probability of the given words.



#### THE FOLLOWING PART IS SUPER IMPORTANT:

Here, I will mention the methods I have deleted:

- crossValidationSplits()
- test()
- The parts that used these methods in the main function

These functions were made if you're curious about what happens if we don't use cross-validation and used the whole train data to train the classifier and the whole test to test it.

the original code was made to run it from console and used tags like [-f]. I deleted this part because it was stupid. Now the program trains the classifier 4 times:

- First, ordinary classifier without filtering stop words. 
- Second, ordinary classifier with filtering stop words.
- Third, boolean classifier without filtering stop words.
- Fourth, boolean classifier with filtering stop words.

The output of my code is:

![](http://www.mediafire.com/convkey/b4f1/pt3ai1ots6jbcnjzg.jpg)

