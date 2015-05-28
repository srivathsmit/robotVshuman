#!/usr/bin/env python

import os
import csv
import sys
import pandas as pd
import numpy as np
from sklearn.cross_validation import cross_val_score
from sklearn.cross_validation import Bootstrap
from models.common import *


def get_model():
    return SvmModel()


def shuffle(df):
    index = list(df.index)
    np.random.shuffle(index)
    df = df.ix[index]
    df.reset_index()
    return df


def cross_validation(model, X, y, n_cv=5):
    cvs = cross_val_score(model, X, y, scoring=None, cv=n_cv)
    print(cvs.mean(), cvs.std())


def bootstrap(model, X, y, n_iter=50):
    auc = []
    full_idx = set(range(X.shape[0]))
    for i in xrange(n_iter):
        train_idx = np.random.choice(X.shape[0], X.shape[0], replace=True)
        test_idx = list(full_idx - set(train_idx))
        model.fit(X[train_idx,:], y[train_idx])
        auc.append(model.score(X[test_idx,:], y[test_idx]))
    print(np.mean(auc), np.std(auc))


def main():
    inputdir = sys.argv[1]
    datalabel = sys.argv[2]
    inputfile = os.path.join(inputdir, 'train_features_%s.csv' % datalabel)

    # Preprocess data
    data = pd.read_csv(inputfile)
    data = shuffle(data)
    y = np.array(data.loc[:, 'outcome'].astype('int'))
    data.drop(['outcome', 'bidder_id'], inplace=True, axis=1)
    data = data.astype(float)
    X = preprocess_features(data)

    # Evaluate model
    cross_validation(get_model(), X, y)
    bootstrap(get_model(), X, y)

if __name__ == '__main__':
    main()
