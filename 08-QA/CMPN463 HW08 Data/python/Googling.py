from collections import defaultdict
import re


#-------------------- These are some helping functions --------------------
def remove_tags(text):
    """
    This function takes a string as an input, and removes the unnecessary tags
    """
    for tag in ["<PERSON>", "</PERSON>", "<ORGANIZATION>", "</ORGANIZATION>", "<em>", "</em>"]:
        text = text.replace(tag, "")
    return text


def get_key_max_value(d):
    """
    Takes a dictionary as an input, and it returns the key that has maximum value
    """
    values = d.values()
    if not values:
        return ""
    idx = values.index(max(values))
    return d.keys()[idx]


def handle_acronyms(text):
    """
    This method is used to take a text and replace every acronym in it with what it stands for.
    Here, in our 'googleResults_tagged.txt' corpus, we have just two acronyms:
     -> NY for New York
     -> CA for California
    """
    acronyms = [(" NY ", " New York "), (" CA ", " California ")]
    for acronym in acronyms:
        text = text.replace(acronym[0], acronym[1])
    return text
#--------------------------------------------------------------------------


# defines the components of a query result from Google.
class GoogleQuery:  
    def __init__(self, title, snip, link):
        self.title = title
        self.snip = snip
        self.link = link
    
    #returns the title, snip, and link associated with a Google result
    def __str__(self):
        return ('title: ' + self.title + '\nsnip: ' + self.snip + '\nlink: ' + self.link)

# note that you should not need to use this class. this class defines the possible locations 
# of a landmark. it differs from the location object in that it stores multiple possible location
# objects, while the location object only stores one possible guess for a city location.
class LocationPossibilities:
    def __init__(self, cities, country):
        self.cities = cities
        self.country = country

    #returns the list of all the possible cities along with the country which contains the city
    def __str__(self):
        locations = ''
        for city in self.cities:
            locations += (city + ', ')
        locations = locations[:-2]
        return ('possible cities: ' + locations + '\ncountry: ' + self.country)

# defines the components of a location.
class Location:
    
    def __init__(self, city, country):
        self.city = city
        self.country = country

    '''
    returns the name of the city and country associated with the landmark
    '''
    def __str__(self):
        return ('city: ' + self.city + '\ncountry: ' + self.country)

class Googling:

    # reads in data for a set of results for a single query
    def readInSegment(self, lines):
        queryResults = []
        for i in range(0, len(lines), 3):
            queryResults.append(GoogleQuery(lines[i], lines[i + 1], lines[i + 2]))
        return queryResults
    
    # reads in data from a string rather than a file. assumes the same text file structure as readInData
    def readString(self, infoString):
        queryData = []
        lines = infoString
        startline = 0
        endline = 0
        while startline < len(lines):
            i = startline
            while i < len(lines) and len(lines[i].strip()) > 0: # reads for a query until an empty line or the end of the file
                i += 1
            endline = i
            queryData.append(self.readInSegment(lines[startline:endline]))
            startline = endline + 1 
        return queryData
    
    # reads in the tagged query results output by Google. takes in the name of the file containing the tagged Google results.
    def readInData(self, googleResultsFile):
        queryData = []
        infile = open(googleResultsFile)
        lines = infile.readlines()
        infile.close()
        startline = 0
        endline = 0
        while startline < len(lines):
            i = startline
            while i < len(lines) and len(lines[i].strip()) > 0: # reads for a query until an empty line or the end of the file
                i += 1
            endline = i
            queryData.append(self.readInSegment(lines[startline:endline]))
            startline = endline + 1 
        return queryData
    
    # takes a line and parses out the correct possible locations of the landmark for that line.
    # returns a LocationPossibilities object as well as the associated landmark
    def readGoldEntry(self, line):
        parts = line.split('\t')
        locationParts = parts[2].split(',')
        cities = locationParts[0].split('/')
        return LocationPossibilities(cities, locationParts[1].lower().strip()), parts[1].lower().strip()
    
    # reads in a file containing data about the landmark and where it's located 
    # returns a list of LocationPossibilities object as well as a list of landmarks. takes 
    # in the name of the gold file
    def readInGold(self, goldFile):
        goldData = []
        landmarks = []
        infile = open(goldFile)
        lines = infile.readlines()
        infile.close()
        for line in lines:
            goldEntry, landmark = self.readGoldEntry(line)
            goldData.append(goldEntry)
            landmarks.append(landmark)
        return goldData, landmarks
            
    # in this method, you must return Location object, where the first parameter of the constructor is the city where
    # the landmark is located and the second parameter is the state or the country containing the city. 
    # the return parameter is a Location object. if no good answer is found, returns a GoogleQuery object with
    # empty strings as parameters
    
    # note that the method does not get passed the actual landmark being queried. you do not need this information,
    # as your primary task in this method is to simply extract a guess for the location of the landmark given
    # Google results. you can, however, extract the landmark name from the given queries if you feel that helps.
    def guessLocation(self, data):
        #TODO: use the GoogleQuery object for landmark to generate a tuple of the location
        # of the landmark
        city_regex = r"[^,] <LOCATION>([A-Za-z ]*)</LOCATION>"
        country_regex = r"<LOCATION>.*</LOCATION>, (<LOCATION>)?(([A-Z]\w* ?)+)(</LOCATION>)?"

        possible_cities = defaultdict(float)
        possible_countries = defaultdict(float)
        for result in data:
            text = result.title + result.snip
            text = remove_tags(text)
            text = handle_acronyms(text)
            city_matches = re.findall(city_regex, text)
            country_matches = re.findall(country_regex, text)
            if city_matches:
                for match in city_matches:
                    possible_cities[match.strip()] += 1.
            if country_matches:
                for match in country_matches:
                    possible_countries[match[1].strip()] += 1.

        candidate_city = get_key_max_value(possible_cities)
        candidate_country = get_key_max_value(possible_countries)
        if not candidate_city or not candidate_country:
            return Location("", "")
        return Location( candidate_city, candidate_country)
    
    # loops through each of the data associated with each query and passes it into the
    # guessLocation method, which returns the guess of the user
    def processQueries(self, queryData):
        #TODO: this todo is optional. this is for anyone who might want to write any initialization code that should only be performed once.
        guesses = [''] * len(queryData)
        for i in range(len(queryData)):
            guesses[i] = self.guessLocation(queryData[i])
        return guesses
    
    # prints out the results as described in the handout
    def printResults(self, correctCities, incorrectCities, noguessCities, correctCountries, incorrectCountries, noguessCountries, landmarks, guesses, gold):
        print('LANDMARK\tYOUR GUESSED CITY\tCORRECT CITY/CITIES\tYOUR GUESSED COUNTRY\tCORRECT COUNTRY')
        correctGuesses = set(correctCities).intersection(set(correctCountries))
        noGuesses = set(noguessCities).union(set(noguessCountries))
        incorrectGuesses = set(incorrectCities).union(set(incorrectCountries))
        print('=====CORRECT GUESSES=====')
        for i in correctGuesses:
            print(landmarks[i] + '\t' + guesses[i].city + '\t' + str(gold[i].cities) + '\t' + guesses[i].country + '\t' + gold[i].country)
        print('=====NO GUESSES=====')
        for i in noGuesses:
            print(landmarks[i] + '\t' + guesses[i].city + '\t' + str(gold[i].cities) + '\t' + guesses[i].country + '\t' + gold[i].country)
        print('=====INCORRECT GUESSES=====')
        for i in incorrectGuesses:
            print(landmarks[i] + '\t' + guesses[i].city + '\t' + str(gold[i].cities) + '\t' + guesses[i].country + '\t' + gold[i].country)
        print('=====TOTAL SCORE=====')
        correctTotal = len(correctCities) + len(correctCountries)
        noguessTotal = len(noguessCities) + len(noguessCountries)
        incorrectTotal = len(incorrectCities) + len(incorrectCountries)
        print('correct guesses: ' + str(correctTotal))
        print('no guesses: ' + str(noguessTotal))
        print('incorrect guesses: ' + str(incorrectTotal))
        print('total score: ' + str(correctTotal - incorrectTotal) + ' out of ' + str(correctTotal + noguessTotal + incorrectTotal))
    
    # takes a list of Location objects and prints a list of correct and incorrect answers as well as scores the results
    def scoreAnswers(self, guesses, gold, landmarks):
        correctCities = []
        incorrectCities = []
        noguessCities = []
        correctCountries = []
        incorrectCountries = []
        noguessCountries = []
        for i in range(len(guesses)):
            if guesses[i].city.lower() in gold[i].cities:
                correctCities.append(i)
            elif guesses[i].city == '':
                noguessCities.append(i)
            else:
                incorrectCities.append(i)
            if guesses[i].country.lower() == gold[i].country.lower():
                correctCountries.append(i)
            elif guesses[i].country == '':
                noguessCountries.append(i)
            else:
                incorrectCountries.append(i)
        self.printResults(correctCities, incorrectCities, noguessCities, correctCountries, incorrectCountries, noguessCountries, landmarks, guesses, gold)
    
if __name__ == '__main__':
    googleResultsFile = '../data/googleResults_tagged.txt' # file where Google query results are read
    goldFile = '../data/landmarks.txt' # contains the results 
    googling = Googling()
    queryData = googling.readInData(googleResultsFile)
    goldData, landmarks = googling.readInGold(goldFile)
    guesses = googling.processQueries(queryData)
    googling.scoreAnswers(guesses, goldData, landmarks)


"""
The Output is:
LANDMARK    YOUR GUESSED CITY   CORRECT CITY/CITIES YOUR GUESSED COUNTRY    CORRECT COUNTRY
=====CORRECT GUESSES=====
statue of liberty   Liberty Island  ['liberty island', 'new york harbor', 'new york city']  New York    new york
taj mahal   Agra    ['agra']    India   india
eiffel tower    Paris   ['paris']   France  france
forbidden city  Beijing ['beijing'] China   china
burj khalifa    Dubai   ['dubai']   United Arab Emirates    united arab emirates
parthenon   Athens  ['athenian acropolis', 'acropolis', 'athens']   Greece  greece
saint basil's cathedral Moscow  ['red square', 'moscow']    Russia  russia
christ the redeemer Rio de Janeiro  ['rio de janeiro']  Brazil  brazil
sydney opera house  Sydney  ['sydney']  Australia   australia
stanford university Stanford    ['palo alto', 'stanford']   California  california
=====NO GUESSES=====
=====INCORRECT GUESSES=====
=====TOTAL SCORE=====
correct guesses: 20
no guesses: 0
incorrect guesses: 0
total score: 20 out of 20
"""
