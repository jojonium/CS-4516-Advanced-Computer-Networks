from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier

from sklearn.externals import joblib
import numpy as np
import pickle
import sys

filename = None

labeldict = {
    'youtube': 1,
    'browser': 2,
    'fruit_ninja': 3,
    'google_news': 4,
    'weather_channel': 5
}

if len(sys.argv) < 2:
    print("you gotta give some files as arguments")
    exit()

vectors = []
labels = []
i = 1
while i < len(sys.argv):
    filename = sys.argv[i]
    labelname = filename.split('/')[-1].split('.')[0]
    newvectors = pickle.load(open(filename, "rb"))
    vectors += newvectors
    labels += [labeldict[labelname]] * len(newvectors)
    i += 1

model = None

try:
    model = joblib.load('model.pkl')
except:
    print("no pkl file, so creating one")
    #model = SVC(kernel = 'poly', degree = 2, gamma = 1, coef0 = 0, probability = True)
    #model = SVC(kernel = 'linear')
    #model = RandomForestClassifier(n_estimators = 100)
    model = LinearSVC()

print("about to fit the vectors")
model = model.fit(vectors, labels)
print("fit new vectors with new labels")
joblib.dump(model, 'model.pkl')
print("dumped the training data to model.pkl")
