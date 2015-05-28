#!/usr/bin/env python

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.base import BaseEstimator
from sklearn import preprocessing
from sklearn.metrics import roc_auc_score
from sklearn.svm import SVC, LinearSVC


class RocScorerMixin(object):
    def score(self, X_test, y_test):
        return roc_auc_score(y_test, self.predict(X_test))


class LogisticRegressionModel(BaseEstimator, RocScorerMixin):
    def __init__(self):
        self.lr = LogisticRegression(penalty='l1')

    def fit(self, X, y):
        self.scaler = preprocessing.StandardScaler().fit(X)
        X = self.scaler.transform(X)
        self.lr.fit(X, y)

    def predict(self, X_test):
        X_test = self.scaler.transform(X_test)
        probabilities = self.lr.predict_proba(X_test)[:,1]
        return probabilities


class SvmModel(BaseEstimator, RocScorerMixin):
    def __init__(self):
        self.model = SVC(C=1e-5, gamma=100)

    def fit(self, X, y):
        self.scaler = preprocessing.StandardScaler().fit(X)
        X = self.scaler.transform(X)
        self.model.fit(X, y)

    def predict(self, X_test):
        X_test = self.scaler.transform(X_test)
        scores = self.model.decision_function(X_test)
        scores.shape = scores.shape[0]
        return scores


class LinearSvmModel(BaseEstimator, RocScorerMixin):
    def __init__(self):
        self.model = LinearSVC(C=0.0000000001, loss='l1', penalty='l2')

    def fit(self, X, y):
        self.scaler = preprocessing.StandardScaler().fit(X)
        X = self.scaler.transform(X)
        self.model.fit(X, y)

    def predict(self, X_test):
        X_test = self.scaler.transform(X_test)
        scores = self.model.decision_function(X_test)
        scores.shape = scores.shape[0]
        return scores

class LogRegAndSvmModel(BaseEstimator, RocScorerMixin):
    def __init__(self):
        self.svm_model = SVC(C=1e-5, gamma=100)
        self.lr_model = LogisticRegression(penalty='l1')

    def fit(self, X, y):
        self.scaler = preprocessing.StandardScaler().fit(X)
        X = self.scaler.transform(X)
        self.svm_model.fit(X, y)
        self.lr_model.fit(X, y)
        svm_scores = self.svm_model.decision_function(X)
        lr_scores = self.lr_model.predict_proba(X)[:,1]
        self.svm_mean = np.mean(svm_scores)
        self.lr_mean = np.mean(lr_scores)
        self.svm_sd = np.std(svm_scores)
        self.lr_sd = np.std(lr_scores)

    def predict(self, X_test):
        X_test = self.scaler.transform(X_test)
        svm_scores = (self.svm_model.decision_function(X_test) - self.svm_mean)/self.svm_sd
        lr_scores = (self.lr_model.predict_proba(X_test)[:,1] - self.lr_mean)/self.lr_sd
        svm_scores.shape = svm_scores.shape[0]
        return (.5*svm_scores + .5*lr_scores)
