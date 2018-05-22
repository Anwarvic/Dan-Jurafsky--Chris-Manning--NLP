# Introduction

This directory contains three files beside the README.md file:

- `CMP462 HW08 IR.pdf` file which contains a full description of the project.
- `CMP462 HW08 Data.zip` compressed file which has the project before being solved. (raw project)
- `CMP462 HW08 Data` folder which contains the project after being solved.

Special Thanks to:

- Prof. Danial Jurfasky and Christopher Manning for creating such an awesome project.
- Dr. Mohamed Aly for providing a full description of the project after being deleted from Coursera's Database.

---

# Description

In this assignment you will be improving upon a rather poorly-made information retrieval system. You will build an inverted index to quickly retrieve documents that match queries and then make it even better by using term-frequency inverse-document-frequency weighting and cosine similarity to compare queries to your data set. Your IR system will be evaluated for accuracy on the correct documents retrieved for different queries and the correctly computed tf-idf values and cosine similarities.



## Data

The data is a collection of 60 short stories by the famed _Rider Haggard_. In the `data` directory, you will find:

- **`RiderHaggard`** directory which has the training data. Within this directory you will see yet another directory `raw\` which  contains the raw text files of 60 different short stories written by Rider Haggard. 
- **`queries.txt`** file which has some keywords that we will be used as queries for the models you will create.
- **`solutions.txt`** file is the correct answer for the queries in the `queries.txt` file.

The past two files are used as you begin implementing your IR system.



## Provided Code

There are two files provided inside the `python` directory. The first file is **`PorterStemmer.py`** which is used to stem data inside the `raw` directory.  By Stemming, I mean to remove all the common prefixes and suffixes from the word. So, we can put all similar words into one group which has one label on it, this label represents all of these similar words which are in the group, this label we call (stem) or (the root). 

![](http://www.mediafire.com/convkey/50e0/w49mnjnbv35vq8zzg.jpg)

And the second file is `IRSystem.py`. In this file, we have one class which is `IRSystem()` that has five member variables:

- **`titles`**: it's a list of strings that contains the titles of the short stories, and they are 60 titles.
- **`docs`**: it's a list of list of strings that contains the stemmed words of the short stories. For example `docs[0]` is the list of stemmed words that are in the first file.
- **`vocab`**: it's a list of all the unique words that are in the whole corpus.
- **`alphanum`**: it's a SRE patterns that is used to delete any white space within the word.
- **`p`**: it's a Port stemmer model that is used to stem the raw files.

![IRSystem UML](http://www.mediafire.com/convkey/9011/vm3z4az4wvpl6eizg.jpg)

This class has five methods:

- **`read_data(directory)`** method: 
  Given the location of the 'data' directory, reads in the documents to be indexed. It uses either of the following two functions:
  - **`__read_raw_data(diectory)`** method:
    It's used only the first time you run the code to read the data. Then, the data goes to be stemmed creating a folder called `stemmed` in the `../data/RiderHaggard` directory.
  - **`__read_stemmed_data(diectory)`** method:
    This method is used after stemming the data. It reads the stemmed data which saves a ton of time.
- **`process_query(query)`** method: 
  Given a query string, this processes it and returns the list of lowercase, alphanumeric, stemmed words in the string.


- **`query_retrieve(query))`** method:
  Given a string, this method processes it and then returns the list of matching documents found by `boolean_retrieve()`.
- **`query_rank(query)`** method:
  Given a string, this method processes it and then returns the list of the top matching documents, rank-ordered.
- **`get_posting_unstemmed(word)`** method:
  Given a word, this method *stems* the word and then calls `get_posting()` on the stemmed word to get its postings list. 


There are also two other functions that you should know about:

- **`run_tests()`** function:
  This function is used to run some test over your work and evaluate it.
- **`main()`** function:
  This function is used to run your work in a sequence.

The previous methods and functions should *NOT* need to be changed.



# Requirement

In this project, we need to implement three models:

- **Inverted Index Model** which is a mapping from words to the documents in which they occur using the method `index()` and `get_posting` methods.
- **Boolean Retrieval Model** in which you return the list of documents that contain all words in a query using the `boolean_retrieve()`method.
- **TF-IDF Model** which computes and stores the term-frequency inverse-document- frequency value for every word-document co-occurrence using the `compute_tfidf()` and `get_tfidf()` methods.
- Improve the TF-IDF Model by using **Cosine-Similarity** using the `rank_retrieve()` method.

So, we need to fill the following methods:

- **`index()`**:
  This is where you will build the inverted index. The documents will have already been read in for you at this point, so you will want to look at some of the instance variables in the class.
- **`get_posting(word)`**:
  This method returns a list of integers (document IDs) that identifies the documents in which the word is found. This is basically just an API into your inverted index, but you must implement it in order to be evaluated fully.
- **`boolean_retrieve(query)`**:
  This method performs Boolean retrieval, returning a list of document IDs corresponding to the documents in which all the words in query occur.
- **`compute_tfidf()`**:
  This function computes and stores the tf-idf values for words and documents. For this you will probably want to be aware of the class variables vocab and documents which hold, respectively, the list of all unique words and the list of documents, where each document is a list of words.
- **`get_tfidf(word, doc)`**: 
  You must implement this method to return the tf-idf weight for a particular word and document ID.
- **`rank_retrieve(query)`**: 
  This method returns a list of the top ranked documents for a given query. Right now it ranks documents according to their Jaccard similarity with the query, but you will replace this method of ranking with a ranking using the cosine similarity between the documents and query.

We suggest you work on them in that order, because some of them build on each other. It also gets a bit more complex as you work down this list.



# My Solution

In the following snippets of codes, I'm assuming that we have imported all the dependencies. And they are:

```python
import json
import math
import os
import re
from collections import defaultdict, Counter
import numpy as np
from PorterStemmer import PorterStemmer
```

And we also have to add this shebang:

```python
#!/usr/bin/env python
```

## index

In the `index()` method, I have created two member variables:

- `tf` which stands for Term Frequency, and it will be used in later methods
- `inv_index` which is a dictionary that has a word as a key and a set of files indices as a value. Let's understand what I mean by an example:

```python
>>> irsys = IRSystem()
>>> irsys.read_data('../data/RiderHaggard')
>>> irsys.index()
>>> irsys.inv_index['winter']
set([0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 13, 14, 15, 17, 18, 19, 20, 22, 23, 25, 26, 27, 28, 29, 30, 32, 33, 34, 36, 37, 38, 40, 41, 42, 44, 45, 46, 47, 48, 49, 50, 51, 53, 54, 55, 56, 57, 58, 59])
```

This means that the word 'winter' has been mentioned in short stories that have these indices. After that, we return that member variable using the method `get_posting()`. 



## boolean_retrieve

The `boolean_retrieve()` method is given a list of queries. Then,  I used the `inv_index` member variable that i have created in the `index()` method to get the indices of each word in the query list. Then, get the indices that are common among these words and return it.



## compute_tfidf

In this method, I have created two member variables:

- `doc_tfidf` which will be used in the Cosine Similarity part.
- `tfidf` which is a dictionary of a dictionary that the index of the file as the first key, and the word as the second key. The value is the tf_idf score.

it calculated the tf_idf score by applying this formula:


![equation](http://latex.codecogs.com/gif.latex?tfidf%20%3D%20%281%20&plus;%20log%28tf%29%29*log%28%5Cfrac%7BTotal%20Documents%7D%7Bno.documents%7D%29)

where:

- `tf` is the member variable that we have created in `index()` method.
- `Total Documents` which is the total number of documents which are 60.
- `No. Documents` is the output of `get_posting()` method which represents the number of documents that the given word is mentioned in out of the 60 documents.

Then, we use `get_tfidf()` method to return that score.



## rank_retrieve

This method is the last method that we need to implement. This method calculates the cosine score for each document by applying the following formula:
$$
score =\frac{ \sum_{w} tfidf * (1 + log(TFquery))}{\sqrt(Document TFIDF)}
$$
where;

- `tfidf` is the tfidf score given the word and the document.
- `TFquery` is the term frequency of the query. In other words, how many times each word is mentioned in the query. So, if the query was "ra ra oh oh ga ga oh la la Caught in a bad romance", then the `TFquery` of "oh" is 3.
- `Document TFIDF` is the `doc_tfidf` that we have created in `compute_tfidf()` method.

Then, it saves these scores into a list and return that list in a sorted manner. Finally, we use the `query_rank()` method to get this sored list given a query string.



The output of my solution in the first time is:

![](http://www.mediafire.com/convkey/4b57/6adu1ac6j7zif7nzg.jpg)

As you can see, it take around 100 seconds to stem our data. After that, our model will read from the stemmed data which will save a lot of time. 

![](http://www.mediafire.com/convkey/2109/gvihdv64iuwi6przg.jpg)

The program after stemming take around 30 seconds.



#### VERY IMPORTANT NOTE:

I have changed the main part in the `IRSystem.py` file to be able to run it without any parameters or tags.
