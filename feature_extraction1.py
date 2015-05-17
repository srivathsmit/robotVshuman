import os
import sys
import csv

inputdir = sys.argv[1]

def load_bid_file():
    bid_file = os.path.join(inputdir, 'bids.csv')
    bid_file_h = open(bid_file, 'r')
    csvreader = csv.reader(bid_file_h, delimiter=",")
    header = csvreader.next()
    bid_rows = []
    for line in csvreader:
        bid_rows.append(line)
    bid_file_h.close()
    return header, bid_rows

header, bid_rows = load_bid_file()

def load_bidder_id_to_unique_values(colname):
    bidder_col = header.index('bidder_id')
    colnum = header.index('auction')
    bidder_id_to_unique_values = {}
    for row in bid_rows:
        bidder_id = row[bidder_col]
        value = row[colnum]
        if bidder_id not in bidder_id_to_unique_values:
            bidder_id_to_unique_values[bidder_id] = set()
        bidder_id_to_unique_values[bidder_id].add(value)
    return bidder_id_to_unique_values

def extract_bidder_num_auctions():
    bidder_col = header.index('bidder_id')
    auction_col = header.index('auction')
    bidder_id_to_num_auctions = {}
    for row in bid_rows:
        bidder_id = row[bidder_col]
        auction_id = row[auction_col]
        bidder_id_to_num_auctions[bidder_id] = bidder_id_to_num_auctions.setdefault(bidder_id, 0) + 1
    return bidder_id_to_num_auctions

bidder_id_to_num_auctions = extract_bidder_num_auctions()
bidder_id_to_unique_auctions = load_bidder_id_to_unique_values('auction')
bidder_id_to_unique_devices = load_bidder_id_to_unique_values('device')
bidder_id_to_unique_ips = load_bidder_id_to_unique_values('ip')
bidder_id_to_unique_urls = load_bidder_id_to_unique_values('url')
   
# bidder_id -> avg frequency

# bidder_id -> max frequency

# bidder_id -> min frequency

# Generate data set
train_file = open(os.path.join(inputdir, 'train.csv'), 'r')
csvreader = csv.reader(train_file, delimiter=",")
header = csvreader.next()
outputfile = open(os.path.join(inputdir, 'features1.csv'), 'w')
csvwriter = csv.wrter(outputfile, delimiter=',')
for line in csvreader:
    # Get features from previously loaded maps
    bidder_id = line[0]
    row = []
    row.append(bidder_id_to_num_auctions.get(bidder_id, 0))
    row.append(bidder_id_to_unique_auctions.get(bidder_id, 0))
    row.append(bidder_id_to_unique_devices.get(bidder_id, 0))
    row.append(bidder_id_to_unique_ips.get(bidder_id, 0))
    row.append(bidder_id_to_unique_urls.get(bidder_id, 0))
    csvwriter.writerow(row)

outputfile.close()
train_file.close()
    
