#!/usr/bin/env python

import csv
import os
import sys
from collections import defaultdict


def get_features_for_bidder(bidder, auction_count_by_category):
    ret = { }
    ret['jewelry'] = auction_count_by_category[bidder]['jewelry']
    ret['mobile'] = auction_count_by_category[bidder]['mobile']
    ret['office_equipment'] = auction_count_by_category[bidder]['office equipment']
    ret['books_and_music'] = auction_count_by_category[bidder]['books and music']
    ret['sporting_goods'] = auction_count_by_category[bidder]['sporting goods']
    ret['home_goods'] = auction_count_by_category[bidder]['home goods']
    ret['computers'] = auction_count_by_category[bidder]['computers']
    ret['auto_parts'] = auction_count_by_category[bidder]['auto parts']
    ret['clothing'] = auction_count_by_category[bidder]['clothing']
    ret['furniture'] = auction_count_by_category[bidder]['furniture']
    return ret


def calculate_features(bidfile, bidders):
    auction_count_by_category = defaultdict(lambda: defaultdict(int)) # bidder -> category -> count
    # bidder -> auction -> bid timestamp
    # bidder -> key {device, ip, country, urls} -> list()
    categories = set()
    with open(bidfile, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            bidder_id = row['bidder_id']
            if bidder_id in bidders:
                categories.add(row['merchandise'])
                auction_count_by_category[bidder_id][row['merchandise']] += 1

    feature_dict = { }
    for bidder in bidders:
        feature_dict[bidder] = get_features_for_bidder(bidder,
            auction_count_by_category)

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
    inputdir = sys.argv[1]
    datalabel = sys.argv[2]
    bidfile = os.path.join(inputdir, 'bids.csv')
    trainfile = os.path.join(inputdir, 'train.csv')
    testfile = os.path.join(inputdir, 'test.csv')
    train_bidders, test_bidders = load_bidders(trainfile, testfile)
    features = calculate_features(bidfile, train_bidders | test_bidders)


if __name__ == '__main__':
    main()
