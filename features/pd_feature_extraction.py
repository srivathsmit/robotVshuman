#!/usr/bin/env python
"""Usage:
    python -m features.pd_feature_extraction <data directory> <data label/version tag>

Outputs are written to data directory as train_features_<data_label>.csv and test
features_<data_label>.csv.
"""
import numpy as np
import pandas as pd
import os
import sys
from features import *


def merge_features(train_features, test_features, bidder_features):
    """Merge train_features, test_features with new columns in bidder_features.
    Replace all missing values with 0s

    Args:
        train_features - pandas Dataframe for train set with
            `bidder_id` column
        test_features - pandas Dataframe for test set with
            `bidder_id` column

    Returns:
        Updated merged train_features and test_features dataframes
    """
    train_features = train_features.merge(bidder_features, on='bidder_id', how='left')
    test_features = test_features.merge(bidder_features, on='bidder_id', how='left')
    new_columns = list(set(bidder_features.columns) -  set(['bidder_id']))
    train_features.fillna(0, inplace=True)
    test_features.fillna(0, inplace=True)
    return train_features, test_features


def calculate_features(bids_data, train_bidders, test_bidders):
    """Calculate features for the given set of bidders using bids_data

    Arguments:
        bids_data - A pandas dataframe loaded from bids.csv
        train_bidders - A pandas Dataframe with list of train `bidder_id`s
        test_bidders - A pandas Dataframe with list of test `bidder_id`s
    Returns:
        A pandas dataframe with features for each of the bidder
    """
    train_features = train_bidders
    test_features = test_bidders

    # Calculate num auctions
    def unique_counts(x):
        return np.unique(x).size
    def counts(x):
        return x.size

    bidder_auction_counts = bids_data.groupby(
        'bidder_id'
    )['auction'].aggregate(
        {'num_unique_auctions': unique_counts, 'num_auctions': counts}
    ).reset_index()
    train_features, test_features = merge_features(
        train_features, test_features, bidder_auction_counts
    )
    del bidder_auction_counts

    for category, merchandise in categories_to_merchandise.iteritems():
        bids_data_category = bids_data[bids_data.loc[:, 'merchandise'] == merchandise]
        column_name = 'num_auctions_' + category
        bidder_category_counts = bids_data_category.groupby(
            'bidder_id'
        )['auction'].aggregate(
            {column_name: counts}
        ).reset_index()
        train_features, test_features = merge_features(
            train_features, test_features, bidder_category_counts
        )

    for column in ['device', 'ip', 'url', 'country']:
        bidder_column_counts = bids_data.groupby(
            'bidder_id'
        )[column].aggregate(
            {'num_' + column: unique_counts}
        ).reset_index()
        train_features, test_features = merge_features(
            train_features, test_features, bidder_column_counts
        )

    print "Calculating ranks"
    # Add per auction ranks
    bids_data['rank'] = bids_data.groupby('auction')['time'].rank()

    def coef_var(a):
        return a.std() / a.mean()

    def rank_diff(a):
        return np.minimum(a.diff()[1:], 100)

    def time_diff(a):
        return a.diff()[1:]

    print "Aggregating bidder auction rank diffs"
    bidder_auction_rank_features = bids_data.loc[
        :, ('auction', 'bidder_id', 'rank',)
    ].groupby(
        ['auction', 'bidder_id']
    )['rank'].aggregate(
        {
            'rank_diff_mean': lambda x: rank_diff(x).mean(),
            'rank_diff_var': lambda x: rank_diff(x).var(),
            'rank_diff_coef_var': lambda x: coef_var(rank_diff(x)),
        }
    ).reset_index()
    bidder_auction_rank_features = bidder_auction_rank_features[
        np.logical_not(
            np.isnan(bidder_auction_rank_features.loc[:, 'rank_diff_coef_var'])
        )
    ]

    bidder_rank_features = bidder_auction_rank_features.loc[
        :, ('bidder_id', 'rank_diff_mean', 'rank_diff_var', 'rank_diff_coef_var')
    ].groupby('bidder_id').aggregate(np.mean).reset_index()
    train_features, test_features = merge_features(
        train_features, test_features, bidder_rank_features
    )
    del bidder_auction_rank_features
    del bidder_rank_features

    print "Aggregating bidder auction time diffs"
    bidder_auction_time_features = bids_data.loc[
        :, ('auction', 'bidder_id', 'time',)
    ].groupby(
        ['auction', 'bidder_id']
    )['time'].aggregate(
        {
            'time_diff_mean': lambda x: time_diff(x).mean(),
            'time_diff_var': lambda x: time_diff(x).var(),
            'time_diff_coef_var': lambda x: coef_var(time_diff(x)),
        }
    ).reset_index()
    bidder_auction_time_features = bidder_auction_time_features[
        np.logical_not(
            np.isnan(bidder_auction_time_features.loc[:, 'time_diff_coef_var'])
        )
    ]

    bidder_time_features = bidder_auction_time_features.loc[
        :, ('bidder_id', 'time_diff_mean', 'time_diff_var', 'time_diff_coef_var')
    ].groupby('bidder_id').aggregate(np.mean).reset_index()

    train_features, test_features = merge_features(
        train_features, test_features, bidder_time_features
    )

    del bidder_auction_time_features
    del bidder_time_features

    return train_features, test_features


def main():
    inputdir = sys.argv[1]
    datalabel = sys.argv[2]

    # load data
    bidfile = os.path.join(inputdir, 'bids.csv')
    bids_data = pd.read_csv(bidfile, index_col=False)

    trainfile = os.path.join(inputdir, 'train.csv')
    train_data = pd.read_csv(trainfile, usecols=['bidder_id', 'outcome'])

    testfile = os.path.join(inputdir, 'test.csv')
    test_bidders = pd.read_csv(testfile, usecols=['bidder_id'])

    train_features, test_features = calculate_features(
        bids_data, train_data, test_bidders
    )

    trainfile_output = os.path.join(inputdir, 'train_features_%s.csv' % datalabel)
    train_features.to_csv(trainfile_output, index=False)

    # Calculate test features
    testfile_output = os.path.join(inputdir, 'test_features_%s.csv' % datalabel)
    test_features.to_csv(testfile_output, index=False)


if __name__ == '__main__':
    main()
