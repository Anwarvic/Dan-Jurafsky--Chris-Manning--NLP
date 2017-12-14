import sys, os
from subprocess import Popen, PIPE
from FeatureFactory import FeatureFactory

"""
Do not modify this class
The submit script does not use this class
It directly calls the methods of FeatureFactory and MEMM classes.
"""
def main():
    
    print 'USAGE: python NER.py trainFile testFile'
    featureFactory = FeatureFactory()

    # read the train and test data
    trainData = featureFactory.readData("../data/train")
    testData = featureFactory.readData("../data/dev")

    # add the features
    trainDataWithFeatures = featureFactory.setFeaturesTrain(trainData);
    testDataWithFeatures = featureFactory.setFeaturesTest(testData);

    # write the updated data into JSON files
    featureFactory.writeData(trainDataWithFeatures, 'trainWithFeatures');
    featureFactory.writeData(testDataWithFeatures, 'testWithFeatures');

    # run MEMM
    output = Popen(['java','-cp', 'classes', '-Xmx1G' ,'MEMM'
                    ,'trainWithFeatures.json', 'testWithFeatures.json', '-print'], 
                    stdout=PIPE).communicate()[0]

    print output

if __name__ == '__main__':
    main()



