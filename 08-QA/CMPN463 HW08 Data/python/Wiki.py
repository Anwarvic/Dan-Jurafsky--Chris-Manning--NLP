import sys, traceback
import re


#-------------------- These some helping functions I created --------------------
def get_info_boxes(wiki_file):
    """
    Takes the whole wiki file 'small-wiki.xml' and returns a list of list, 
    each has lines of an infobox.
    """
    output = []
    infobox = []
    start = False
    lines = wiki_file.readlines()
    for line in lines:
        if "{{Infobox" in line and not start:
            infobox.append(line)
            start = True
        elif start and line == "}}\n":
            infobox.append(line)
            start = False
            output.append(infobox)
            infobox = []
        elif start:
            infobox.append(line)
        else:
            pass
    return output


def get_spouse_relation(info_boxes_list):
    """
    Takes a list of infoboxes, and it returns a dictionary with:
     -> husband name as the key
     -> list of wives as value
    """
    husband_spouse_dict = {}
    for infobox in info_boxes_list:
        name_line = [line for line in infobox if re.search(r"\|\s*[Nn]ame", line)]
        spouse_line = [line for line in infobox if re.search(r"\|\s*[Ss]pouse", line)]
        if name_line and spouse_line:
            name_matches = re.findall(r"(([A-Z][\w\.]*[ ]?){2,})", name_line[0])
            spouse_matches = re.findall(r"(([A-Z][\w\.]*([ ]| of )?){2,})", spouse_line[0])

        if name_matches:
            husband_name = name_matches[0][0].strip()
            wives = [match[0].strip() for match in spouse_matches]
            if husband_name not in husband_spouse_dict.keys():
                husband_spouse_dict[husband_name] = wives
    
    return husband_spouse_dict

def get_married_lines(wiki_file):
    """
    Takes the whole corpus file 'small-wiki.xml' and returns the lines that 
    contains the word 'married' to be used later to extract spouse relations
    """
    return [line for line in wiki_file.readlines() if "married" in line]

def get_title_names(wiki_file):
    """
    Takes the whole coprus file 'small-wiki.xml' and returns the list of names of the wiki articles
    that are in the corpus
    """
    wiki_file.seek(0)
    regex = r"<title>(.*)</title>"
    return re.findall(regex, wiki_file.read())

def get_full_name(whole_names, part_name):
    if len(part_name.split(" ")) > 1:
        return part_name

    for name in whole_names:
        if part_name in name:
            return name
    
#--------------------------------------------------------------------------------

class Wiki:
    
    # reads in the list of wives
    def addWives(self, wivesFile):
        try:
            input = open(wivesFile)
            wives = input.readlines()
            input.close()
        except IOError:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback)
            sys.exit(1)    
        return wives
    

    # read through the wikipedia file and attempts to extract the matching husbands. note that you will need to provide
    # two different implementations based upon the useInfoBox flag. 
    def processFile(self, f, wives, useInfoBox):
        
        husbands = []
        #-------------------- useInfoBox == True --------------------
        if useInfoBox:
            husband_spouse_dict = get_spouse_relation(get_info_boxes(f))
            for wife in wives:
                wife = wife.strip()
                answer = False
                for husband, spouses in husband_spouse_dict.iteritems():
                    for spouse in spouses:
                        if wife in spouse or spouse in wife:
                            husbands.append("Who is " + husband + "?")
                            answer = True
                if not answer:
                    husbands.append('No Answer')
        

        #-------------------- useInfoBox == False --------------------
        else:
            regex = r"(\[\[)?(([A-Z][\w\.]*[ ]?)+)(\[\[)? ?(has been|is|was|who)?( married | married to )(\[\[)?(([A-Z][\w\.]*[ ]?)+)(\[\[)?"
            
            X, Y = [], [] #'X' for men and 'Y' for their spouses
            married_lines = get_married_lines(f)
            for line in married_lines:
                matches = re.findall(regex, line)
                if matches:
                    match = matches[0]
                    if match[4] == "who":
                        X.append(match[-3].strip())
                        Y.append(match[1].strip())
                    else:
                        X.append(match[1].strip())
                        Y.append(match[-3].strip())

            assert len(X) == len(Y)
            whole_names = get_title_names(f)
            for wife in wives:
                wife = wife.strip()
                try:
                    idx = Y.index(wife)
                    husband = get_full_name(whole_names, X[idx])
                    husbands.append("Who is " + husband + "?")
                except ValueError:
                    husbands.append('No Answer')

        f.close()
        return husbands
    
    # scores the results based upon the aforementioned criteria
    def evaluateAnswers(self, useInfoBox, husbandsLines, goldFile):
        correct = 0
        wrong = 0
        noAnswers = 0
        score = 0 
        try:
            goldData = open(goldFile)
            goldLines = goldData.readlines()
            goldData.close()
            
            goldLength = len(goldLines)
            husbandsLength = len(husbandsLines)
            
            if goldLength != husbandsLength:
                print('Number of lines in husbands file should be same as number of wives!')
                sys.exit(1)
            for i in range(goldLength):
                if husbandsLines[i].strip() in set(goldLines[i].strip().split('|')):
                    correct += 1
                    score += 1
                elif husbandsLines[i].strip() == 'No Answer':
                    noAnswers += 1
                else:
                    wrong += 1
                    score -= 1
        except IOError:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback)
        if useInfoBox:
            print('Using Info Box...')
        else:
            print('No Info Box...')
        print('Correct Answers: ' + str(correct))
        print('No Answers: ' + str(noAnswers))
        print('Wrong Answers: ' + str(wrong))
        print('Total Score: ' + str(score)) 



if __name__ == '__main__':
    wikiFile = '../data/small-wiki.xml'
    wivesFile = '../data/wives.txt'
    goldFile = '../data/gold.txt'
    wiki = Wiki()
    wives = wiki.addWives(wivesFile)
    for choice in [True, False]:
        useInfoBox = choice
        husbands = wiki.processFile(open(wikiFile), wives, useInfoBox)
        wiki.evaluateAnswers(useInfoBox, husbands, goldFile)
        print 
"""
The output is:
Using Info Box...
Correct Answers: 8
No Answers: 2
Wrong Answers: 0
Total Score: 8

No Info Box...
Correct Answers: 6
No Answers: 4
Wrong Answers: 0
Total Score: 6
"""