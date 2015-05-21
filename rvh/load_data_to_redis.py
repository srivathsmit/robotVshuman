import sys
import os
import csv
from rvh import *

inputdir = sys.argv[1]

r.flushdb()

bid_file = os.path.join(inputdir, 'bids.csv')
bid_file_h = open(bid_file, 'r')
csvreader = csv.reader(bid_file_h, delimiter=",")
header = csvreader.next()

for row in csvreader:
    bidder_col = header.index('bidder_id')
    bidder_id = row[bidder_col]
    cur_count = r.get(bidder_auctions_key(bidder_id))
    cur_count = 0 if cur_count is None else int(cur_count)
    r.set(bidder_auctions_key(bidder_id), cur_count + 1)
    for colname in ['auction', 'device', 'ip', 'url']:
        colnum = header.index(colname)
        value = row[colnum]
        redis_keyname = redis_prefix + ":" + "unique_map_for_" + colname + ":" + bidder_id
        r.pfadd(uniq_col_key(colname, bidder_id), value)

