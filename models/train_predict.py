import os
import csv
import sys
from sklearn.linear_model import LogisticRegression
from sklearn.cross_validation import cross_val_score
from sklearn import preprocessing
import pandas as pd

inputdir = sys.argv[1]
inputfile = os.path.join(inputdir, 'features1.csv')

# Train model
data = pd.read_csv(inputfile)
X = data.loc[:, ['num_auctions', 'num_unique_auctions', 'num_unique_devices', 'num_unique_ips', 'num_unique_urls']].astype(float)
scaler = preprocessing.StandardScaler().fit(X)
X = scaler.transform(X)
y = data.loc[:, 'label'].astype('int')
lr = LogisticRegression(penalty='l1')
cvs = cross_val_score(lr, X, y, scoring='roc_auc', cv=5)
print(cvs.mean(), cvs.std(), cvs)

# Do a final fit
lr.fit(X, y)

# Run on test
testfile = os.path.join(inputdir, 'features1_test.csv')
test_data = pd.read_csv(testfile)
test_X = test_data.loc[:, ['num_auctions', 'num_unique_auctions', 'num_unique_devices', 'num_unique_ips', 'num_unique_urls']].astype(float)
test_X = scaler.transform(test_X)
y = data.loc[:, 'label']
predictions = lr.predict_proba(test_X)[:, 1]

submission_file = os.path.join(inputdir, 'submission.csv')
sub_f = open(submission_file, 'w')
csvwriter = csv.DictWriter(sub_f, ['bidder_id', 'prediction'], delimiter=',')
csvwriter.writeheader()
for pred, bidder_id in zip(predictions, test_data.loc[:, 'bidder_id']):
    csvwriter.writerow({'bidder_id': bidder_id, 'prediction': pred})
sub_f.close()
