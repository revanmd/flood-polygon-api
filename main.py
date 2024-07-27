from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field
from pymongo import MongoClient, GEOSPHERE
from typing import List, Dict, Any
import uvicorn

app = FastAPI()

# MongoDB connection
client = MongoClient("mongodb://localhost:27017")
db = client['geo_database']
collection = db['geo_collection']

# Ensure the collection has a 2dsphere index
collection.create_index([("geometry", GEOSPHERE)])

class Point(BaseModel):
    lat: float = Field(..., description="Latitude of the point")
    lon: float = Field(..., description="Longitude of the point")

class PolygonFeature(BaseModel):
    type: str
    geometry: Dict[str, Any]
    properties: Dict[str, Any] = None

class PolygonFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[PolygonFeature]

@app.get("/api/polygons", response_model=PolygonFeatureCollection)
def get_polygons(lat: float = Query(..., description="Latitude of the center point"),
                 lon: float = Query(..., description="Longitude of the center point"),
                 radius: float = Query(..., description="Radius in meters")):
    try:
        # Convert radius from meters to radians for geospatial queries
        radius_in_radians = radius / 6378137.0

        # Create a point for the center of the circular area
        center_point = {
            "type": "Point",
            "coordinates": [lon, lat]
        }

        # Query MongoDB for polygons that are within the circular area
        query = {
            "geometry": {
                "$geoWithin": {
                    "$centerSphere": [[lon, lat], radius_in_radians]
                }
            }
        }
        results = list(collection.find(query))

        # Convert MongoDB results to GeoJSON format
        features = []
        for result in results:
            result['_id'] = str(result['_id'])
            features.append({
                "type": "Feature",
                "geometry": result['geometry'],
                "properties": result.get('properties', {})
            })

        geojson = {
            "type": "FeatureCollection",
            "features": features
        }

        return geojson
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
