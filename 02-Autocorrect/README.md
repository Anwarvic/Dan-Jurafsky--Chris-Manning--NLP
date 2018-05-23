# Introduction

This directory contains three files beside the README.md file:

- `CMP462 HW02 Autocorrect.pdf` file which contains a full description of the project.
- `CMP462 HW02 Data.zip` compressed file which has the project before being solved. (raw project)
- `CMP462 HW02 Data` folder which contains the project after being solved.

Special Thanks to:

- Prof. Danial Jurfasky and Christopher Manning for creating such an awesome project.
- Dr. Mohamed Aly for providing a full description of the project after being deleted from Coursera's Database.

---

# Description

In this assignment you will be training a language model to build a spell checker. Specifically, you will
be implementing part of a noisy-channel model for spelling correction. We will give the likelihood
term, or edit model, and your job is to make a language model, the prior distribution in the noisy
channel model. At test time you will be given a sentence with exactly one typing error. We then select
the correction which gets highest likelihood under the noisy-channel model, using your language
model as the prior. Your language models will be evaluated for accuracy, the number of valid
corrections, divided by the number of test sentences.



## Data

We will be using the writings of secondary-school children, collected by David Holbrook. The training
data is located in the `data/` directory. A summary of the contents:

- `holbrook-tagged-train.dat`: the corpus to train your language models.
- `holbrook-tagged-dev.dat`: a corpus of spelling errors for development.
- `count_1edit.txt`: a table listing counts of edits `x|w`, taken from Wikipedia. You don't need to modify any code which uses this.

Note that the data files do not contain \<s> and \</s> markers, but the code which reads in the data
adds them.



## Provided Code

### Datum.py

Here, I'm going to explain every method of the `Datum()` class.

`Datum` class is a convenient class that is used to process the words in the train and test corpus. It has two types of constructors that you can create:

- `Datum(word)`: which takes a string as input like `Datum('sister')`.


- `Datum(word, error)`: which contains the right word and the wrong spelling like `Datum('sister', 'siter')`.

Now, let's discuss the methods:

- **`fixError()`** method: 
  It returns the word without the wrong part. So, 

  ```python
  >>> Datum('sister','siter').fixError()
  sister
  ```


- **`hasError()`** method: 
  If the instance has an error part, it returns `True`. So;
  ```python
  >>> Datum('sister', 'siter').hasError()
  True
  >>> Datum('sister', '').hasError()
  False
  ```

- **`isValidTest()`** method: 
  This method tests if the given Datum is valid. By valid, I mean have these conditions:

  * the given instance has only letters. If it has any special characters or numbers, the method will return `False`
  * The given instance MUST have an error part.
  * the **Levenstein distance** between the right word and its wrong spelling MUST be less than one. So,
  ```python
  >>> Datum('sister', 'siter').isValidTest()    #one distance (inserting 's')
  True
  >>> Datum('sister', 'ster').isValidTest()
  False
  ```



### Sentence.py

`Sentence()` class takes a list of `Datum` as an input;
```python
>>> from Datum import Datum
>>> lst = [Datum("i"), Datum("love", "lov"), Datum("girls")]
>>> s = Sentence(lst)
>>> print s
i love (lov) playing soccer
>>> for datum in s.data:
...     print datum,
i love (lov) girls
```
The following are some simple methods:
```python
>>> len(s)
3
>>> s.get(1)
love (lov)
>>> s.put(0, Datum('I'))
>>> s
I hate girls
>>> s.isEmpty()
False
```

Now, let's get to the more important methods:

- **`getErrorSentence()`** method : 
  it returns the wrong spelling of the words if exists.

  ```python
  >>> s.getErrorSentence()
  ['I', 'lov', 'girls']
  ```

- **`getCorrectSentence()`** method: 
  This method returns the right spelling of the words.

  ```python
  >>> s.getCorrectSentence()
  ['I', 'love', 'girls']
  ```

- **`cleanSentence()`** method: 
  This method returns the right word but as a sentence. so;

  ```python
  >>> print s.cleanSentence()
  i love girls
  ```

- **`isCorrection()`** method: 
  This method takes a list of strings and it iterates every word in the list and compare it with the `Datum.data` member variable. So;

  ```python
  >>> s.isCorrection(["I", "love", "girls"])
  True
  >>> s.isCorrection(["I", "lov", "girls"])
  False
  >>> s.isCorrection(["I", "love", "Girls"])
  False
  ```

- **`getErrorIndex()`** method: 
  This method returns the index of the wrong word in the sentence and returns -1 if  there is no error. So;

  ```python
  >>> s.getErrorIndex()
  1
  ```



### HolbrookCorpus.py

Here, I'll try to explain every method of the `HolbrookCorpus()` class:

-  **`processLine()`** method: 
     This method does the following:

     * remove these special characters ", . ! ' : ;
     * convert the letters into lower case. So, 'I' becomes 'i'.
     * puts \<s> at the beginning of the line and \</s> at the end.
     * The corpus marks the wrong word by the \<ERR> tag like so "\<ERR targ=sister> siter \</ERR>".
       This function take the previous tag and change it to `sister (siter)`.

     ```python
     >>> from Datum import Datum
     >>> from Sentence import Sentence
     >>>
     >>> h = HolbrookCorpus()
     >>> test = "'I love my Family, and my <ERR targ=sister> siter </ERR> ."
     >>> h.processLine(test)
     <s> i love my family and my sister (siter) </s>
     ```

     Every word is processed as a `Datum` class NOT a `str`. 

-  **`read_holbrook()`** method: 
     This method applies `proccessLine()` method to the corpus as it takes the filename of the corpus which is `../data/holbrook-tagged-train.dat` OR `../data/holbrook-tagged-dev.dat`and iterates over every line and apply `processLine()` to it.

-  **`generateTestCases()`** method: 
     This method returns just one error per line. So, if you have a line like this:

     " Then Bob \<ERR targ=started> straghted \</ERR> to get \<ERR targ=friendly> frendly \</ERR> with a man called \<ERR targ=James> Jame \</ERR> ."

     This function will return two test cases, each has just one wrong word like so:

     ```python
     >>> h = HolbrookCorpus('../data/holbrook-tagged-dev.dat')
     >>> h.generateTestCases()[0]
     <s> then bob started to get friendly (frendly) with a man called james </s>
     >>> h.generateTestCases()[1]
     <s> then bob started to get friendly with a man called james (jame) </s>
     ```



### EditModel.py

Here, I'm going to explain every method in the `EditModel()` class which takes the `../data/count_1edit.txt` file as an input.

- **`initVocabulary(corpus)`** method: 
  This method takes the corpus and saves the corpus as a set of strings and represents every word in the corpus without repetitions... So, if the corpus was just this sentence "I love bananas and I love apples", the vocabulary would be set(['I', 'love', 'bananas', 'and', 'apples'])

  ```python
  >>> h_cor = HolbrookCorpus('../data/holbrook-tagged-train.dat')
  >>> e = EditModel()
  >>> e.initVocabulary(h_cor)
  >>> len(e.vocabulary)
  1661
  ```

- **`read_edit_table(filename)`** method: 
  It takes the directory of the edit table which is `../data/count_1edit.txt` and saves the table as a dictionary where the key is like `hc|ch` and the value as `8` which represents how many it is occurred to replace `hc` with `ch`. So;

  ```python
  >>> e = EditModel()
  >>> e.read_edit_table('../data/count_1edit.txt')['hc|ch']
  8
  >>> e.read_edit_table('../data/count_1edit.txt')['e|i']
  917
  ```

- **`edit_count('st1', 'st2')`** method: 
  It takes two strings, and returns how many the 'st1' is replaced by 'st2'. So;

  ```python
  >>> e.edit_count('hc', 'ch')
  8
  >>> e.edit_count('e', 'i')
  917
  ```

- **`editProbabilities('st')`** method: 
  This method takes a string and calculate the probability of every form (that is just one distance away from the original word). So;

  ```python
  >>> e.editProbabilities('word')
  {'word': 0.9, 
   'work': 0.00967741935483871, 
   'worm': 0.00967741935483871, 
   'wood': 0.0032258064516129032, 
   'words': 0.04838709677419355, 
   'lord': 0.0064516129032258064, 
   'world': 0.02258064516129032
  }
  ```

The following is a function that doesn't belong to the `EditModel()` class. This function is called **`dameraulevenshtein(seq1, seq2)`**. This function calculates the distance between two strings. Distance is the number of additions, deletions, substitutions, and transpositions needed to transform the first sequence into the second. Transpositions are exchanges of *consecutive* characters; all other operations are self-explanatory.

Although generally used with strings, any sequences of comparable objects will work. This implementation is `O(N*M)` time and `O(M)` space, for `N` and `M` are the lengths of the two sequences. This function It's taken from http://mwh.geek.nz/2009/04/26/python-damerau-levenshtein-distance MIT license.

```python
>>> dameraulevenshtein('ba', 'abc')
2
>>> dameraulevenshtein('fee', 'deed')
2
```

It works with arbitrary sequences too:
```python
>>> dameraulevenshtein('abcd', ['b', 'a', 'c', 'd', 'e'])
2
```



### SpellingResult.py

This file is used to evaluate the Language models you will be creating. The Accuracy is calculated by number of valid corrections, divided by the number of test sentences.

![img](http://latex.codecogs.com/gif.latex?%24%24%20Accuracy%20%3D%20%5Cfrac%7Bno.Correct%7D%7Btotal%7D%20%24%24)



### UnifromLanguageModel.py

This file is just a dummy language model to show you how to use the variables and how the function should look like. This Language Model deals with all the words the same. No wonder it get such a terrible accuracy.



## Requirements

In this project, we will have to:

- Create a `Laplace Unigram Language Model`.
- Create a `Laplace Bigram Language Model`.
- Create a `Stupid Backoff Language Model`.
- create a `Custom Language Model`.



# My Solution

## LaplaceUnigramLanguageModel.py

In this file, I have created a Laplace Unigram Language Model which has two member variables. `total` which represents the total count of the words in the train corpus, and `LaplaceUnigramCounts` which is a dictionary that represents how many counts for every word in the corpus:

![LaplaceUnigramLanguageModel UML](http://www.mediafire.com/convkey/c1e6/4q5n6tu0y2go195zg.jpg)



This model has two methods:

- **`train(corpus)`**:
  This method takes the train corpus located at `'../data/holbrook-tagged-train.dat` as an input. Then, it initializes the `LaplaceUnigramCounts` and `total` variables.

- **`score(sentence)`**:
  This method takes a list of strings as argument and returns the log-probability of the sentence using Laplace unigram language model.
  
![eq](http://latex.codecogs.com/gif.latex?score%20%3D%5Csum%5Cleft%20%5Blog%28WordCount%20&plus;%201%29%20-%20log%28total%29%20%5Cright%20%5D)

We have added 1 as a way of smoothing, because some words in the dev corpus that weren't in the train corpus.



## LaplaceBigramLanguageModel.py

In this file, I have created the `Bigram Language Model` which has three member variables:

- **`LaplaceUnigramCounts`**:
  It is a dictionary that contains the count of every word.
- **`LaplaceBigramCounts`**:
  It is a dictionary that contains the count of every two words.
- **`total`**:
  Which is the count of all words in the train corpus

![Laplace Bigram Language Model](http://www.mediafire.com/convkey/6a64/c83qogy55rdcpyczg.jpg)

This model has also three methods:

- **`train(corpus)`**:
  This method takes the train corpus located at `'../data/holbrook-tagged-train.dat` as an input. Then, it initializes the `LaplaceBigramCounts` and `total` variables.

- **`group_i_words(sentence, i)`**:This function takes two arguments:

    - a `sentece` as a list of strings.
    - an integer `i` which represents the number of words you want to group.

  And it returns a list containing the word grouped out of that sentence putting every `i` words with each other. So;

  ```python
  >>> from 
  >>> h_cor = HolbrookCorpus('../data/holbrook-tagged-train.dat')
  >>> example = ['<s>', 'my', 'mum', 'goes', 'out', 'sometimes', '</s>']
  >>> 
  >>> model = LaplaceBigramLanguageModel()
  >>> model.group_i_words(example, 2)
  ['<s> my', 'my mum', 'mum goes', 'goes out', 'out sometimes', 'sometimes </s>']
  >>> model.group_i_words(example, 3)
  ['<s> my mum', 'my mum goes', 'mum goes out', 'goes out sometimes', 'out sometimes </s>']
  ```

- **`score(sentence)`**:
  This method takes a list of strings as argument and returns the log-probability of the sentence using Laplace unigram language model.
  
![eq](http://latex.codecogs.com/gif.latex?score%20%3D%5Csum%5Cleft%20%5Blog%28WordCount%20&plus;%201%29%20-%20log%28total%29%20%5Cright%20%5D)

We have added one as a way of smoothing, because some words in the dev corpus that weren't in the train corpus.



## StupidBackoffLanguageModel.py

In this file, I have creates the Stupid Back-off Model. If you don't know about Stupid Back-off Model, it's basically a combination of Bigram and Unigram models. It uses the Bigram and Unigram combination at first, but when it fails it uses the Unigram Model only with some additive score

The Model contains  three member variables:

- **`LaplaceUnigramCounts`**:
  It is a dictionary that contains the count of every word.
- **`LaplaceBigramCounts`**:
  It is a dictionary that contains the count of every two words.
- **`total`**:
  Which is the count of all words in the train corpus

![StupidBackoffLanguageModel UML](http://www.mediafire.com/convkey/e1fe/9udlhas2ka3f5s4zg.jpg)

And it has three member functions:

- **`train(corpus)`**:
  This method takes the train corpus located at `'../data/holbrook-tagged-train.dat` as an input. 

- **`group_i_words(sentence, i)`**:This function takes two arguments:

  - a `sentece` as a list of strings.
  - an integer `i` which represents the number of words you want to group.

  And it returns a list containing the word grouped out of that sentence putting every `i` words with each other. So;

  ```python
  >>> h_cor = HolbrookCorpus('../data/holbrook-tagged-train.dat')
  >>> example = ['<s>', 'my', 'mum', 'goes', 'out', 'sometimes', '</s>']
  >>> 
  >>> model = LaplaceBigramLanguageModel()
  >>> model.group_i_words(example, 2)
  ['<s> my', 'my mum', 'mum goes', 'goes out', 'out sometimes', 'sometimes </s>']
  >>> model.group_i_words(example, 3)
  ['<s> my mum', 'my mum goes', 'mum goes out', 'goes out sometimes', 'out sometimes </s>']
  ```

- **`score(sentence)`**:

  This method takes a list of strings as argument and returns the log-probability of the sentence according to the following formula:

  ![](http://www.mediafire.com/convkey/e988/4bf39ajrpazcbwozg.jpg)

> 

## GoodTuringUnigram.py

This file contains the Unigram Model but with using Good Turing as a smoothing method. 

![Good Turing Unigram Model](http://www.mediafire.com/convkey/47b6/mwbejlb5l4edwjvzg.jpg)

This model has four member variables:

- **`Unicounts`**:
  It is a dictionary that contains the count of every word. In other words, it's the `LaplaceUnigramCounts` in the Unigram model.
- **`newCounts`**:
  It's a dictionary that has word as the key and the smoothed count of that word as a value.
- **`N`**:
  Which is the count of all words. In other words, it's the **`total`** in the Unigram model.
- **`N_1`**:
  It's the count of the words that have been mentioned just one time inside the train corpus.

And it has two member methods:

- **`train(corpus)`**:
  This method takes the train corpus located at `'../data/holbrook-tagged-train.dat` as an input. 
- **`score(sentence)`**:
  This method takes a list of strings as argument and returns the log-probability of the sentence using Laplace unigram language model along with Good Turing smoothing.



## CustomLanguageModel.py

This file contains a combination of Unigram and Bigram using Kneser-Ney Smoothing. This model has five member variables:

- **`Unigramcounts`**:
  It is a dictionary that contains the count of every word.
- **`BigramCounts`**:
  It is a dictionary that contains the count of every two words.
- **`total`**:
  It's the count of all words. In other words.
- **`BeforeCounts`**:
  It's a dictionary that has a word as a key and a set as the value.
- **`AfterCounts`**:
  It's a dictionary that has a word as a key and a set as the value.

![Custom Language Model UML](http://www.mediafire.com/convkey/2e64/dbzihpagz5btz0bzg.jpg)

And it has three member functions:

- **`train(corpus)`**:
  This method takes the train corpus located at `'../data/holbrook-tagged-train.dat` as an input. 

- **`group_i_words(sentence, i)`**:This function takes two arguments:

  - a `sentece` as a list of strings.
  - an integer `i` which represents the number of words you want to group.

  And it returns a list containing the word grouped out of that sentence putting every `i` words with each other. So;

  ```python
  >>> h_cor = HolbrookCorpus('../data/holbrook-tagged-train.dat')
  >>> example = ['<s>', 'my', 'mum', 'goes', 'out', 'sometimes', '</s>']
  >>> 
  >>> model = LaplaceBigramLanguageModel()
  >>> model.group_i_words(example, 2)
  ['<s> my', 'my mum', 'mum goes', 'goes out', 'out sometimes', 'sometimes </s>']
  >>> model.group_i_words(example, 3)
  ['<s> my mum', 'my mum goes', 'mum goes out', 'goes out sometimes', 'out sometimes </s>']
  ```

- **`score(sentence)`**:

  This method takes a list of strings as argument and returns the log-probability of the sentence according to the following formula:

  ![](http://www.mediafire.com/convkey/32d9/m5rm2jizumf5kcozg.jpg)



## SpellCorrect.py

This file is the file that should be run. This file calls all the models above, and evaluate their performance. This is the output of running this file:

![](http://www.mediafire.com/convkey/cb08/u4w63p594ydb22nzg.jpg)

