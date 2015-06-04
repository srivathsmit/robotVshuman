#!/usr/bin/env python
"""Usage:
    python -m features.inmemory_feature_extraction <data directory> <data label/version tag>

Outputs are written to the data directory as train_features_<data_label>.csv and test_features_<data_label>.csv.
"""

import csv
import os
import pandas as pd
import sys
from collections import defaultdict


def get_features_for_bidder(bid_info, bidder_attributes, bids_per_auction):
    """Get features for a single bidder.

    Arguments:
        bid_info - defaultdict of defaultdicts; category -> auction id -> (bid timestamp, device, ip, country, url)
        bidder_attributes - defaultdict; attribute {device, ip, country, urls} -> set of unique values
        bids_per_auction - defaultdict; auction id -> number of bids in that auction

    Returns:
        dict of features for this bidder
    """
    ret = { }
    num_auctions = sum([len(bid_info[x]) for x in bid_info.keys()])
    ret['jewelry'] = len(bid_info['jewelry'])
    ret['mobile'] = len(bid_info['mobile'])
    ret['office_equipment'] = len(bid_info['office equipment'])
    ret['books_and_music'] = len(bid_info['books and music'])
    ret['sporting_goods'] = len(bid_info['sporting goods'])
    ret['home_goods'] = len(bid_info['home goods'])
    ret['computers'] = len(bid_info['computers'])
    ret['auto_parts'] = len(bid_info['auto parts'])
    ret['clothing'] = len(bid_info['clothing'])
    ret['furniture'] = len(bid_info['furniture'])
    ret['num_devices'] = len(bidder_attributes['device'])
    ret['num_ips'] = len(bidder_attributes['ip'])
    ret['num_countries'] = len(bidder_attributes['country'])
    ret['num_urls'] = len(bidder_attributes['url'])
    return ret


def calculate_features(bidfile, bidders):
    # initialize the dictionaries in which we want to store the bids data
    # auction id -> num bids
    bids_per_auction = defaultdict(int)
    # bidder -> category -> auction id -> (bid timestamp, device, ip, country, url)
    bid_info = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    # bidder -> key {device, ip, country, urls} -> set()
    bidder_attributes = defaultdict(lambda: defaultdict(set))

    # populate the dictionaries
    with open(bidfile, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            bidder_id = row['bidder_id']
            if bidder_id not in bidders:
                continue
            bids_per_auction[row['auction']] += 1
            bid_info[bidder_id][row['merchandise']][row['auction']].append((
                int(row['time']),
                row['device'],
                row['ip'],
                row['country'],
                row['url'],
            ))
            bidder_attributes[bidder_id]['device'].add(row['device'])
            bidder_attributes[bidder_id]['ip'].add(row['ip'])
            bidder_attributes[bidder_id]['country'].add(row['country'])
            bidder_attributes[bidder_id]['url'].add(row['url'])

    # calculate features for each bidder
    feature_dict = { }
    for bidder in bidders:
        feature_dict[bidder] = get_features_for_bidder(
            bid_info[bidder],
            bidder_attributes[bidder],
            bids_per_auction,
        )
        feature_dict[bidder]['bidder_id'] = bidder

    return feature_dict


def load_bidders(trainfile, testfile):
    train_bidders = set()
    test_bidders = set()

    with open(trainfile, 'r') as trf:
        reader = csv.DictReader(trf)
        for line in reader:
            train_bidders.add(line['bidder_id'])

    with open(testfile, 'r') as tef:
        reader = csv.DictReader(tef)
        for line in reader:
            test_bidders.add(line['bidder_id'])

    return (train_bidders, test_bidders)


def main():
    # input options
    inputdir = sys.argv[1]
    datalabel = sys.argv[2]

    # load data and calculate features
    bidfile = os.path.join(inputdir, 'bids.csv')
    trainfile = os.path.join(inputdir, 'train.csv')
    testfile = os.path.join(inputdir, 'test.csv')
    train_bidders, test_bidders = load_bidders(trainfile, testfile)
    features = calculate_features(bidfile, train_bidders | test_bidders)

    # write features to output
    trainfile_output = os.path.join(inputdir, 'train_features_%s.csv' % datalabel)
    testfile_output = os.path.join(inputdir, 'test_features_%s.csv' % datalabel)
    train_features = pd.DataFrame([features[bidder_id] for bidder_id in train_bidders])
    test_features = pd.DataFrame([features[bidder_id] for bidder_id in test_bidders])
    traindata = pd.read_csv(trainfile, usecols=['bidder_id', 'outcome'])
    train_output = pd.merge(train_features, traindata, left_on='bidder_id', right_on='bidder_id', sort=False)
    train_output.to_csv(trainfile_output, index=False)
    test_features.to_csv(testfile_output, index=False)


if __name__ == '__main__':
    main()
