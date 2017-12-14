Overview

We've provided you with three basic tools for developing your PCFG.  All of the
tools revolve around flat tab separated grammar files (ending in .gr).  
lines beginning with the # symbol are considered comments.  These files contain 
rules of the form:

      weight <tab>  parent <tab> child1 <space> child2 ...

We've given you a set of grammar files to get you started, but which you should
modify as you please.  They have the following organization:

       S2.gr    # a baseline grammar which can generate any sentence over the vocab
       S1.gr    # a starter grammar which contains the top level smoothing rules and
       		      # gives a few simple example rules
       Vocab.gr # a grammar describing the part(s) of speech for each term in the vocab


PCFG Parser

This program takes in a sentence file and a sequence of grammar files and parses
each of the sentences with the grammar.  It will print out the maximum probability
parse tree and the log probability for that parse.  It also computes the perplexity
of your grammar on the given sentence file.  Because your grade will be a function
of your perplexity on the dev and test data sets, this is going to be the key tool
for evaluating your grammar.  To invoke the PCFGParser call:

    java -jar pcfg.jar parse dev.sen *.gr

to print the parse trees in the Penn treebank format use the -t option:

    java -jar pcfg.jar parse -t dev.sen *.gr


PCFG Generator

This program takes a sequence of grammar files and samples sentences from the
distribution of sentences described by your PCFG.  This can be useful for finding
glaring errors in your grammar, or undesirable biases.  To generate the default
number of sentences, 20, you can just call:

    java -jar pcfg.jar generate *.gr

or to generate an arbitrary number of sentences, use the -n option:

    java -jar pcfg.jar generate -n 100 *.gr

and to print the parse trees along with the actual sentences, use the -t option (first):

    java -jar pcfg.jar generate -t -n 100 *.gr

Validate Grammar

This program checks checks the terminals of your grammar against a hard-coded list
of allowed words (also given in the allowed words file). This is useful for making
sure that you haven't created any non-terminals which never generate a terminal.
While you won't be explicitly penalized for such mistakes, they will only hurt your
perplexity because they will hold out probability for symbols which never actually
occur in the dev or test set. It also makes sure that you have some rule which generates
every word in the list of allowed words. The starter grammar files already satisfy this,
but this will show you if you accidentally change things for the worse. This utility
operates sort of like the unix diff where the first file is implicitly the list of allowed
words. Specifically, it will print words in either set difference marked with the following
convention:

    java -jar pcfg.jar validate *.gr


Submit

To submit, run the following:

    java -jar pcfg.jar submit *.gr
