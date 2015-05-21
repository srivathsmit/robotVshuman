import redis

r = redis.StrictRedis(host='localhost', port=6379, db=0)

redis_prefix = "robotVsHuman"

def uniq_col_key(colname, bidder_id):
    return redis_prefix + ":" + "unique_value_map_for_" + colname + ":" + bidder_id

def bidder_auctions_key(bidder_id):
    return redis_prefix + ":" + "bidder_auction_counts" + ":" + bidder_id
