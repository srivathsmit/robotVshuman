#!/usr/bin/env python

import csv
import os
import pandas as pd
import sys
from common import *
from sklearn.linear_model import LogisticRegression
from sklearn.cross_validation import cross_val_score
from sklearn import preprocessing


def get_model():
    return LogisticRegressionModel()


def main():
    inputdir = sys.argv[1]
    datalabel = sys.argv[2]
    inputfile = os.path.join(inputdir, 'train_features_%s.csv' % datalabel)
    testfile = os.path.join(inputdir, 'test_features_%s.csv' % datalabel)
    submission_file = os.path.join(inputdir, 'submission.csv')

    # Preprocess data and train model
    data = pd.read_csv(inputfile)
    y = np.array(data.loc[:, 'outcome'].astype('int'))
    data.drop(['outcome', 'bidder_id'], inplace=True, axis=1)
    data = data.astype(float)
    X = preprocess_features(data)
    model = get_model()
    model.fit(X, y)

    # Run on test data
    test_data = pd.read_csv(testfile)
    bidder_id = test_data.loc[:, 'bidder_id']
    test_data.drop('bidder_id', inplace=True, axis=1)
    test_data = test_data.astype(float)
    test_X = preprocess_features(test_data)
    predictions = model.predict(test_X)

    # Write submission file
    sub_f = open(submission_file, 'w')
    csvwriter = csv.DictWriter(sub_f, ['bidder_id', 'prediction'], delimiter=',')
    csvwriter.writeheader()
    for pred, bidder_id in zip(predictions, bidder_id):
        csvwriter.writerow({'bidder_id': bidder_id, 'prediction': pred})
    sub_f.close()

if __name__ == '__main__':
    main()
