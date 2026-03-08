from backend.db.connection import options_collection

def get_options_cursor(last_seen=None, limit=100):

    query = {}

    if last_seen:
        query["datetime"] = {"$gt": last_seen}

    cursor = (
        options_collection
        .find(query)
        .sort("datetime", 1)
        .limit(limit)
    )

    return list(cursor)