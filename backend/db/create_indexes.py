from backend.db.connection import options_collection

options_collection.create_index("datetime")
options_collection.create_index("strike")
options_collection.create_index([("symbol",1),("expiry",1),("datetime",1)])

print("Indexes created successfully")