import json
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['geo_database']
collection = db['geo_collection']

# Load GeoJSON data
with open('../data/flooded_vector.geojson', 'r') as file:
    geojson_data = json.load(file)

# Insert GeoJSON data into MongoDB
if isinstance(geojson_data, dict) and 'features' in geojson_data:
    for feature in geojson_data['features']:
        collection.insert_one(feature)

# Create geospatial index
collection.create_index([("geometry", "2dsphere")])

print("GeoJSON polygon data has been saved to MongoDB.")