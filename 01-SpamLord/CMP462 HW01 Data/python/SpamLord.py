import sys
import os
import re
import pprint


# MAIL PATTERNS
# stanford.com
first_regex = r'(([\w\.-]+)\s?(@|%20at%20| at | where )\s?(stanford|-s-t-a-n-f-o-r-d-|gradiance)(\.|%20dot%20| dot | dom | dt )(edu|-e-d-u|com))'
second_regex = r'(([\w\.]+)\s?\(followed by (\"|&ldquo;)@(cs\.)?stanford.edu(\"|&rdquo;)\))'
third_regex = r'(obfuscate\(\'([\w\.]+)\'\,\'([\w\.]+)\'\);)'

# cs.stanford.com
fourth_regex = r'(([\w\.-]+)\s?(@|%20at%20| at | where |&#x40;)\s?(cs|graphics|ogun|lcs|robotics|csl)(\.| dot |;)(stanford|-s-t-a-n-f-o-r-d-|mit|gmu|jhu)(.|%20dot%20| dot | dom )(edu|-e-d-u))'
fifth_regex = r'(([\w\.-]+)\s? at cs stanford edu)'


# PHONE PATTERNS   (650)814-1478
sixth_regex = r'((\(\d{3}\)) ?(\d{3})\-(\d{4}))'
seventh_regex = r'((\d{3})[ |\-](\d{3})[ |\-](\d{4}))'

def delete_WS(text):
    """
    This simple function is used to delete all whitespaces in the text and returns the 
    text without any whitespace. So, if the text is 'mohamed  anwar  @ gmail  . com' the output will
    be 'mohamedanwar@gmail.com'
    """
    white_space = " \t\n"
    output = ''
    for ch in text:
        if ch in white_space:
            pass
        elif ch == ';':         # TO handle some stupid case :(
            output += '.'
        else:
            output += ch
    return output

def handle_at_dot(text):
    """
    I've made this function. It's used to handle some cases where the email is written like:
    mohamed%20at%20gmail%20dot%20com    OR      mohamed at gmail dot com
    as you can see the '@' is replace with either '%20at%20' or ' at ' and '.' with '%20dot%20' or ' dot '

    This function takes an email like the former, and returns the right form which is
    mohamed@gmail.com
    """
    if "%20at%20" in text:
        lst = text.split('%20')
    elif ' at ' in text:
        lst = text.split(' ')
    elif ' WHERE ' in text:
        lst = text.split(' ')
    elif ' WHERE ' in text:
        lst = text.split(' ')
    elif '-@-' in text:
        lst = text.split('-')
    elif '&#x40;' in text:
        lst = text.partition('&#x40;')
    else:
        return delete_WS(text)

    output = ""
    for word in lst:
        if word == 'at' or word == 'WHERE' or word == '&#x40;':
            output += '@'

        elif word == 'dot' or word == 'DOM' or word == 'dt':
            output += '.'

        else:
            output += str(word)
    
    return delete_WS(output)

def handle_at(text):
    """
    This is used to handle some cases where the email is written like:
    mohamed at gmail com
    as you can see the '@' is replace with either ' at '

    This function takes an email like the former, and returns the right form which is
    mohamed@gmail.com
    """
    index = text.find(' at ')
    output = text[:index]+"@"
    lst = text[index+4:].split(' ')
    for word in lst:
        output += str(word)
        if word != lst[-1]:
            output += '.'
    
    return delete_WS(output)

def handle_followed_by(text):
    """
    This function is made to handle just one email in the corpus... this email is written in a 
    fu**ing stupid way. It written like so:
    'teresa.lynn (followed by "@stanford.edu")'
    which should be:
    'teresa.lynn@stanford.edu'

    So, i have to fu**ing handle this very case!!! So, i created this function -_-
    """
    lst = text.split(" (followed by ")
    output = str(lst[0])+str(lst[1][1:-2])
    if '&rdquo' in output:
        output = output.replace('ldquo;', '')
        output = output.replace('&rdquo', '')
    return output

def get_number(text):
    output =""
    for ch in text:
        if ch.isdigit():
            output += ch
    return output[:3] + '-' + output[3:6] + '-' + output[6:]

"""
TODO
This function takes in a filename along with the file object (actually
a StringIO object at submission time) and
scans its contents against regex patterns. It returns a list of
(filename, type, value) tuples where type is either an 'e' or a 'p'
for e-mail or phone, and value is the formatted phone number or e-mail.
The canonical formats are:
     (name, 'p', '###-###-#####')
     (name, 'e', 'someone@something')
If the numbers you submit are formatted differently they will not
match the gold answers

NOTE: ***don't change this interface***, as it will be called directly by
the submit script

NOTE: You shouldn't need to worry about this, but just so you know, the
'f' parameter below will be of type StringIO at submission time. So, make
sure you check the StringIO interface if you do anything really tricky,
though StringIO should support most everything.
"""
def process_file(name, f):
    # note that debug info should be printed to stderr
    # sys.stderr.write('[process_file]\tprocessing file: %s\n' % (path))
    res = []
    for line in f:
        matches = re.findall(first_regex, line, flags=re.IGNORECASE)
        matches.extend(re.findall(fourth_regex, line, flags=re.IGNORECASE))
        for m in matches:
            res.append((name,'e',handle_at_dot(m[0])))

        matches = re.findall(second_regex, line, flags=re.IGNORECASE)
        for m in matches:
            res.append((name,'e',handle_followed_by(m[0])))

        matches = re.findall(third_regex, line, flags=re.IGNORECASE)
        for m in matches:
            res.append((name,'e',m[2]+'@'+m[1]))

        matches = re.findall(fifth_regex, line, flags=re.IGNORECASE)
        for m in matches:
            res.append((name,'e',handle_at(m[0])))

        matches = re.findall(sixth_regex, line)
        matches.extend(re.findall(seventh_regex, line))
        for m in matches:
            res.append((name,'p',get_number(m[0])))

    return res

"""
You should not need to edit this function, nor should you alter
its interface as it will be called directly by the submit script
"""
def process_dir(data_path):
    # get candidates
    guess_list = []
    for fname in os.listdir(data_path):
        if fname[0] == '.':
            continue
        path = os.path.join(data_path,fname)
        f = open(path,'r')
        f_guesses = process_file(fname, f)
        guess_list.extend(f_guesses)
    return guess_list

"""
You should not need to edit this function.
Given a path to a tsv file of gold e-mails and phone numbers
this function returns a list of tuples of the canonical form:
(filename, type, value)
"""
def get_gold(gold_path):
    # get gold answers
    gold_list = []
    f_gold = open(gold_path,'r')
    for line in f_gold:
        gold_list.append(tuple(line.strip().split('\t')))
    return gold_list

"""
You should not need to edit this function.
Given a list of guessed contacts and gold contacts, this function
computes the intersection and set differences, to compute the true
positives, false positives and false negatives.  Importantly, it
converts all of the values to lower case before comparing
"""
def score(guess_list, gold_list):
    guess_list = [(fname, _type, value.lower()) for (fname, _type, value) in guess_list]
    gold_list = [(fname, _type, value.lower()) for (fname, _type, value) in gold_list]
    guess_set = set(guess_list)
    gold_set = set(gold_list)

    tp = guess_set.intersection(gold_set)
    fp = guess_set - gold_set
    fn = gold_set - guess_set

    pp = pprint.PrettyPrinter()
    #print 'Guesses (%d): ' % len(guess_set)
    #pp.pprint(guess_set)
    #print 'Gold (%d): ' % len(gold_set)
    #pp.pprint(gold_set)
    print "---------------------------------------"
    print 'True Positives (%d): ' % len(tp)
    pp.pprint(tp)
    print 'False Positives (%d): ' % len(fp)
    pp.pprint(fp)
    print 'False Negatives (%d): ' % len(fn)
    pp.pprint(fn)
    print 'Summary: tp=%d, fp=%d, fn=%d' % (len(tp),len(fp),len(fn))

"""
You should not need to edit this function.
It takes in the string path to the data directory and the
gold file
"""
def main(data_path, gold_path):
    guess_list = process_dir(data_path)
    gold_list =  get_gold(gold_path)
    score(guess_list, gold_list)

"""
commandline interface takes a directory name and gold file.
It then processes each file within that directory and extracts any
matching e-mails or phone numbers and compares them to the gold file
"""
if __name__ == '__main__':
    if (len(sys.argv) == 1):
        main('../data/dev', '../data/devGOLD')
    elif (len(sys.argv) == 3):
        main(sys.argv[1],sys.argv[2])
    else:
        print 'usage:\tSpamLord.py <data_dir> <gold_file>'
        sys.exit(0)

"""
The output is:
---------------------------------------
True Positives (117): 
set([('ashishg', 'e', 'ashishg@stanford.edu'),
     ('ashishg', 'e', 'rozm@stanford.edu'),
     ('ashishg', 'p', '650-723-1614'),
     ('ashishg', 'p', '650-723-4173'),
     ('ashishg', 'p', '650-814-1478'),
     ('balaji', 'e', 'balaji@stanford.edu'),
     ('bgirod', 'p', '650-723-4539'),
     ('bgirod', 'p', '650-724-3648'),
     ('bgirod', 'p', '650-724-6354'),
     ('cheriton', 'e', 'cheriton@cs.stanford.edu'),
     ('cheriton', 'e', 'uma@cs.stanford.edu'),
     ('cheriton', 'p', '650-723-1131'),
     ('cheriton', 'p', '650-725-3726'),
     ('dabo', 'e', 'dabo@cs.stanford.edu'),
     ('dabo', 'p', '650-725-3897'),
     ('dabo', 'p', '650-725-4671'),
     ('dlwh', 'e', 'dlwh@stanford.edu'),
     ('engler', 'e', 'engler@lcs.mit.edu'),
     ('engler', 'e', 'engler@stanford.edu'),
     ('eroberts', 'e', 'eroberts@cs.stanford.edu'),
     ('eroberts', 'p', '650-723-3642'),
     ('eroberts', 'p', '650-723-6092'),
     ('fedkiw', 'e', 'fedkiw@cs.stanford.edu'),
     ('hager', 'e', 'hager@cs.jhu.edu'),
     ('hager', 'p', '410-516-5521'),
     ('hager', 'p', '410-516-5553'),
     ('hager', 'p', '410-516-8000'),
     ('hanrahan', 'e', 'hanrahan@cs.stanford.edu'),
     ('hanrahan', 'p', '650-723-0033'),
     ('hanrahan', 'p', '650-723-8530'),
     ('horowitz', 'p', '650-725-3707'),
     ('horowitz', 'p', '650-725-6949'),
     ('jks', 'e', 'jks@robotics.stanford.edu'),
     ('jurafsky', 'e', 'jurafsky@stanford.edu'),
     ('jurafsky', 'p', '650-723-5666'),
     ('kosecka', 'e', 'kosecka@cs.gmu.edu'),
     ('kosecka', 'p', '703-993-1710'),
     ('kosecka', 'p', '703-993-1876'),
     ('kunle', 'e', 'darlene@csl.stanford.edu'),
     ('kunle', 'e', 'kunle@ogun.stanford.edu'),
     ('kunle', 'p', '650-723-1430'),
     ('kunle', 'p', '650-725-3713'),
     ('kunle', 'p', '650-725-6949'),
     ('lam', 'e', 'lam@cs.stanford.edu'),
     ('lam', 'p', '650-725-3714'),
     ('lam', 'p', '650-725-6949'),
     ('latombe', 'e', 'asandra@cs.stanford.edu'),
     ('latombe', 'e', 'latombe@cs.stanford.edu'),
     ('latombe', 'e', 'liliana@cs.stanford.edu'),
     ('latombe', 'p', '650-721-6625'),
     ('latombe', 'p', '650-723-0350'),
     ('latombe', 'p', '650-723-4137'),
     ('latombe', 'p', '650-725-1449'),
     ('levoy', 'e', 'ada@graphics.stanford.edu'),
     ('levoy', 'e', 'melissa@graphics.stanford.edu'),
     ('levoy', 'p', '650-723-0033'),
     ('levoy', 'p', '650-724-6865'),
     ('levoy', 'p', '650-725-3724'),
     ('levoy', 'p', '650-725-4089'),
     ('manning', 'e', 'dbarros@cs.stanford.edu'),
     ('manning', 'e', 'manning@cs.stanford.edu'),
     ('manning', 'p', '650-723-7683'),
     ('manning', 'p', '650-725-1449'),
     ('manning', 'p', '650-725-3358'),
     ('nass', 'e', 'nass@stanford.edu'),
     ('nass', 'p', '650-723-5499'),
     ('nass', 'p', '650-725-2472'),
     ('nick', 'e', 'nick.parlante@cs.stanford.edu'),
     ('nick', 'p', '650-725-4727'),
     ('ok', 'p', '650-723-9753'),
     ('ok', 'p', '650-725-1449'),
     ('ouster', 'e', 'ouster@cs.stanford.edu'),
     ('ouster', 'e', 'teresa.lynn@stanford.edu'),
     ('pal', 'e', 'pal@cs.stanford.edu'),
     ('pal', 'p', '650-725-9046'),
     ('psyoung', 'e', 'patrick.young@stanford.edu'),
     ('rajeev', 'p', '650-723-4377'),
     ('rajeev', 'p', '650-723-6045'),
     ('rajeev', 'p', '650-725-4671'),
     ('rinard', 'e', 'rinard@lcs.mit.edu'),
     ('rinard', 'p', '617-253-1221'),
     ('rinard', 'p', '617-258-6922'),
     ('serafim', 'e', 'serafim@cs.stanford.edu'),
     ('serafim', 'p', '650-723-3334'),
     ('serafim', 'p', '650-725-1449'),
     ('shoham', 'e', 'shoham@stanford.edu'),
     ('shoham', 'p', '650-723-3432'),
     ('shoham', 'p', '650-725-1449'),
     ('subh', 'e', 'subh@stanford.edu'),
     ('subh', 'e', 'uma@cs.stanford.edu'),
     ('subh', 'p', '650-724-1915'),
     ('subh', 'p', '650-725-3726'),
     ('subh', 'p', '650-725-6949'),
     ('thm', 'e', 'pkrokel@stanford.edu'),
     ('thm', 'p', '650-725-3383'),
     ('thm', 'p', '650-725-3636'),
     ('thm', 'p', '650-725-3938'),
     ('tim', 'p', '650-724-9147'),
     ('tim', 'p', '650-725-2340'),
     ('tim', 'p', '650-725-4671'),
     ('ullman', 'e', 'support@gradiance.com'),
     ('ullman', 'e', 'ullman@cs.stanford.edu'),
     ('ullman', 'p', '650-494-8016'),
     ('ullman', 'p', '650-725-2588'),
     ('ullman', 'p', '650-725-4802'),
     ('vladlen', 'e', 'vladlen@stanford.edu'),
     ('widom', 'e', 'siroker@cs.stanford.edu'),
     ('widom', 'e', 'widom@cs.stanford.edu'),
     ('widom', 'p', '650-723-0872'),
     ('widom', 'p', '650-723-7690'),
     ('widom', 'p', '650-725-2588'),
     ('zelenski', 'e', 'zelenski@cs.stanford.edu'),
     ('zelenski', 'p', '650-723-6092'),
     ('zelenski', 'p', '650-725-8596'),
     ('zm', 'e', 'manna@cs.stanford.edu'),
     ('zm', 'p', '650-723-4364'),
     ('zm', 'p', '650-725-4671')])
False Positives (0): 
set([])
False Negatives (0): 
set([])
Summary: tp=117, fp=0, fn=0
"""