
# Introduction

This directory contains three files beside the README.md file:

- `CMP462 HW01 Spamlord.pdf` file which contains a full description of the project.
- `CMP462 HW01 Data.zip` compressed file which has the project before being solved. (raw project)
- `CMP462 HW01 Data` folder which contains the project after being solved.

Special Thanks to:

- Prof. Danial Jurfasky and Christopher Manning for creating such an awesome project.
- Dr. Mohamed Aly for providing a full description of the project after being deleted from Coursera's Database.

---

# Description

The goal of this assignment is so simple, it is to write regular expressions that extract phone numbers and regular expressions that extract email addresses from a bunch of files that will be given to you.



## Data

We will be using some data that has been extracted form the web. The data is divided into two groups:

- `devGold`: which is a file that has all the emails and phone numbers that you should extract. You should NOT change anything inside this file, because this file is used to evaluate your work.
- `dev`: which is a folder that contains html files that have been extracted form the web. You don't need to change anything inside this folder, but you might open some of the files to get some intuition about the form of some of the emails or phone numbers.

Here are some of the emails that you should extract (NOT LIMITED TO):

```
xxx@stanford.edu
xxx@cs.stanford.edu
xxx@lcs.mit.edu
xxx@cs.xxx.edu
xxx@robotics.stanford.edu
xxx@csl.stanford.edu
xxx@ogun.stanford.edu
xxx@graphics.stanford.edu
```



## Provided Code

There is only one file that is provided which is `SpamLord.py`. This file has five functions:

- **`process_file(f)`** function: 
  This function takes a file as an input, and searches for the provided regular expressions inside it, and returns a list of the matching parts.
- **`process_dir(path)`** function: 
  This function takes the directory that contains the files, which is `../data/dev`, as an input and apply `process_file()` function over each file in the directory.


    - **`get_gold(path)`** function: This function takes the directory that contains the gold file, which is `../data/devGOLD`, as an input. and saves them in a list `gold_list`.


    - **`score(guess_list, gold_list)`** function: This function takes two lists as an input. The `guess_list` is the parts that match the provided regualr expression which the output of the `process_dir()` function. And the second list is the `gold_list` which is the output of `get_gold()` function. This function prints three numbers:
        - _True Positives_: It displays e-mails and phone numbers which the starter code correctly extracts.
        - _False Positives_: It displays e-mails which the starter code regular expressions match but which are not correct.
        - _False Negatives_: It displays e-mails and phone numbers which the starter code did not match, but which do exist in the html files.

- **`main(data_path, gold_path)`** function: This function takes the directory of the raw files and the gold file and run the previous functions.


# Requirement

You are required to fill in the function `process_file()` and all required code to detect ALL emails and phone numbers in the dev set. So, you are required to obtain ZERO false positives and negatives. 

You should return a list of (filename, type, value) tuples where type is either an `e` or a `p` for e-mail or phone, and value is the formatted phone number or e-mail. The canonical formats are:

     (name, 'p', '###-###-#####')
     (name, 'e', 'someone@something')
If the numbers you submit are formatted differently they will not match the gold answers 



# My Solution

The output of my solution is:

![](http://www.mediafire.com/convkey/0f0f/9huqboaqhbytvs2zg.jpg)