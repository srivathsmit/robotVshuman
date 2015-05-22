#!/usr/bin/env python
"""Usage example:
    python -m features.load_data_to_redis data
"""

import csv
import os
import sys
from features import *


def main():
    inputdir = sys.argv[1]
    bidfile = os.path.join(inputdir, 'bids.csv')

    # Clears db completely
    r.flushdb()

    with open(bidfile, 'r') as f:
        csvreader = csv.DictReader(f, delimiter=",")
        counter = 0
        for row in csvreader:
            if counter % 10000 == 0:
                print counter
            bidder_id = row['bidder_id']
            cur_count = r.get(bidder_auctions_key(bidder_id))
            cur_count = 0 if cur_count is None else int(cur_count)
            r.set(bidder_auctions_key(bidder_id), cur_count + 1)
            for colname in ['auction', 'device', 'ip', 'url', 'time', 'merchandise', 'country']:
                value = row[colname]
                redis_keyname = redis_prefix + ":" + "unique_map_for_" + colname + ":" + bidder_id
                r.pfadd(uniq_col_key(colname, bidder_id), value)
            counter += 1


if __name__ == '__main__':
    main()
