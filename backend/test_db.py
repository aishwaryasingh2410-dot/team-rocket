from backend.db.connection import options_collection
data = options_collection.find_one()

print("Connection Successful")
print(data)