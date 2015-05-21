import os
import sys
import redis

import csv
from rvh import *

inputdir = sys.argv[1]

def _get_features_for_line(line):
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
    if 'outcome' in row:
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
    inf = open(inputfile, 'r')
    csvreader = csv.DictReader(inf, delimiter=",")
    of = open(outputfile, 'w')
    csvwriter = csv.DictWriter(of, output_fields, delimiter=',')
    csvwriter.writeheader()
    for line in csvreader:
        row = _get_features_for_line(line)
        if not train:
            print(row)
        csvwriter.writerow(row)

    of.close()
    inf.close()

generate_features(
    os.path.join(inputdir, 'train.csv'),
    os.path.join(inputdir, 'features1.csv'),
)
generate_features(
    os.path.join(inputdir, 'test.csv'),
    os.path.join(inputdir, 'features1_test.csv'),
    train=False,
)
