import redis

r = redis.StrictRedis(host='localhost', port=6379, db=0)

redis_prefix = "robotVsHuman"

def uniq_col_key(colname, bidder_id):
    return redis_prefix + ":" + "unique_value_map_for_" + colname + ":" + bidder_id

def bidder_auctions_key(bidder_id):
    return redis_prefix + ":" + "bidder_auction_counts" + ":" + bidder_id

CATEGORIES = [
    'jewelry',
    'mobile',
    'office_equipment',
    'books_and_music',
    'sporting_goods',
    'home_goods',
    'computers',
    'auto_parts',
    'clothing',
    'furniture',
]


categories_to_merchandise = {
    'jewelry': 'jewelry',
    'mobile': 'mobile',
    'office_equipment': 'office equipment',
    'books_and_music': 'books and music',
    'sporting_goods': 'sporting goods',
    'home_goods': 'home goods',
    'computers': 'computers',
    'auto_parts': 'auto parts',
    'clothing': 'clothing',
    'furniture': 'furniture',
}


