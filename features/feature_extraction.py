#!/usr/bin/env python
"""Run this after running load_data_to_redis.

Usage example:
    python -m features.feature_extraction data initial_dataset
"""

import csv
import os
import redis
import sys
from features import *


def get_features_for_bidder(line, train=True):
    # Get features from previously loaded maps in redis
    bidder_id = line['bidder_id']

    row = {}
    row['bidder_id'] = bidder_id
    count = r.get(bidder_auctions_key(bidder_id))
    count = int(count) if count else 0
    row['num_auctions'] = count
    row['num_unique_auctions'] = r.pfcount(uniq_col_key('auction', bidder_id))
    row['num_unique_devices'] = r.pfcount(uniq_col_key('device', bidder_id))
    row['num_unique_ips'] = r.pfcount(uniq_col_key('ip', bidder_id))
    row['num_unique_urls'] = r.pfcount(uniq_col_key('url', bidder_id))
    if train:
        row['label'] = int(float(line['outcome']))
    return row


def generate_features(inputfile, outputfile, train=True):
    output_fields = [
        'bidder_id',
        'num_auctions',
        'num_unique_auctions',
        'num_unique_devices',
        'num_unique_ips',
        'num_unique_urls',
    ]
    if train:
        output_fields.append('label')

    with open(inputfile, 'r') as inf, open(outputfile, 'w') as of:
        csvreader = csv.DictReader(inf, delimiter=",")
        csvwriter = csv.DictWriter(of, output_fields, delimiter=',')
        csvwriter.writeheader()
        for line in csvreader:
            row = get_features_for_bidder(line, train)
            csvwriter.writerow(row)


def main():
    inputdir = sys.argv[1]
    dataset_label = sys.argv[2]
    generate_features(
        os.path.join(inputdir, 'train.csv'),
        os.path.join(inputdir, 'train_features_%s.csv' % dataset_label),
    )
    generate_features(
        os.path.join(inputdir, 'test.csv'),
        os.path.join(inputdir, 'test_features_%s.csv' % dataset_label),
        train=False,
    )


if __name__ == '__main__':
    main()
