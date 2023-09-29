from fastapi import FastAPI, HTTPException, Body
from pymongo import MongoClient
from pydantic import BaseModel
from bson import json_util
import json
import subprocess
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

#  FastAPI instance
app = FastAPI()

#  CORS middleware to allow "OPTIONS" requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
)

# MongoDB database configuration
client = MongoClient('mongodb+srv://kenbinoy:ken101@cluster0.u9gx0jy.mongodb.net/')
db_flight = client['flight']
collection_routes = db_flight['newRoutes']
collection_airports = db_flight['Airports']

# MongoDB connection for the second collection
client2 = MongoClient("mongodb+srv://kenbinoy:ken101@cluster0.u9gx0jy.mongodb.net/")
db2 = client2["flight"]
collection2 = db2["newRoutes"]

#  route for airport autocompletion
class AutoCompleteInput(BaseModel):
    prefix: str

@app.post("/search")
async def autocomplete_airports(input: AutoCompleteInput):
    prefix = input.prefix

    pipelines = [
        {
            '$search': {
                'index': 'default',
                'compound': {
                    'should': [
                        {
                            'wildcard': {
                                'path': 'code',
                                'query': prefix,
                                'allowAnalyzedField': True
                            }
                        }, {
                            'autocomplete': {
                                'path': 'name',
                                'query': prefix
                            }
                        }, {
                            'autocomplete': {
                                'path': 'city',
                                'query': prefix
                            }
                        }
                    ]
                }
            }
        },
    ]
    a = collection_airports.aggregate(pipelines)

    b = []

    for each in a:
        each['id'] = str(each['_id'])
        del each['_id']
        b.append(each)

    return b

# request model to define the structure of the POST request data
class RouteRequest(BaseModel):
    fromiata: str
    toiata: str
    daynumber: int

# request model to accept a list of RouteRequest objects
class MultipleRouteRequests(BaseModel):
    routes: list[RouteRequest]

@app.post("/fetch_routes/")
async def fetch_routes(request_data: MultipleRouteRequests):
    if len(request_data.routes) > 3:
        raise HTTPException(status_code=400, detail="You can specify a maximum of 3 'from' and 'to' pairs.")

    routes_response = []

    for request_item in request_data.routes:
        fromiata = request_item.fromiata
        toiata = request_item.toiata
        daynumber = request_item.daynumber  # Retrieve the day number from the request

        # Ensure daynumber is within the valid range (1-7)
        if daynumber < 1 or daynumber > 7:
            raise HTTPException(status_code=400, detail="Day number must be between 1 and 7")

        # query based on the provided parameters
        query = {
            "airportFromIATA": fromiata,
            "airportToIATA": toiata,
            f"day{daynumber}": "yes",  # Filter flights where the specified day is "yes"
        }

        # Fetch routes from MongoDB based on the query
        routes = list(collection_routes.find(query))

        # Sort routes by flightNumber
        sorted_routes = sorted(routes, key=lambda x: x.get("flightNumber", ""))

        if not sorted_routes:
            routes_response.append({"routes": [], "message": "No routes found matching the criteria"})
        else:
            try:
                # Attempt to load the JSON string
                routes_json = json_util.dumps(sorted_routes, default=json_util.default)
                parsed_routes = json.loads(routes_json)
                routes_response.append({"routes": parsed_routes, "message": "Routes found"})
            except json.JSONDecodeError as e:
                # Handle JSON decoding error
                routes_response.append({"routes": [], "message": "Error decoding JSON: " + str(e)})

    # Use JSONResponse to format the response
    return routes_response

# Define the second route model for fetching detailed itinerary
class A(BaseModel):
    route_id: int

# Route for fetching detailed itinerary using the second collection
@app.post("/get_detailed_itinerary")
async def fetch_detailed_itinerary_post(input: A):
    pipeline = [
        {
            '$match': {
                'id': input.route_id
            }
        }, {
            '$lookup': {
                'from': 'Airports',
                'localField': 'airportFromIATA',
                'foreignField': 'code',
                'as': 'airportFrom'
            }
        }, {
            '$lookup': {
                'from': 'Airports',
                'localField': 'airportToIATA',
                'foreignField': 'code',
                'as': 'airportTo'
            }
        }, {
            '$lookup': {
                'from': 'Airlines',
                'localField': 'airlineIATA',
                'foreignField': 'IATA',
                'as': 'airline'
            }
        }, {
            '$unwind': {
                'path': '$airline',
                'includeArrayIndex': 'string',
                'preserveNullAndEmptyArrays': True
            }
        }, {
            '$unwind': {
                'path': '$airportTo',
                'includeArrayIndex': 'string',
                'preserveNullAndEmptyArrays': True
            }
        }, {
            '$unwind': {
                'path': '$airportFrom',
                'includeArrayIndex': 'string',
                'preserveNullAndEmptyArrays': True
            }
        }, {
            '$project': {
                'flyingfrom': {
                    'name': '$airportFrom.name',
                    'code': '$airportFrom.code',
                    'country': '$airportFrom.country',
                    'state': '$airportFrom.state',
                    'city': '$airportFrom.city'
                },
                'flying_to': {
                    'name': '$airportTo.name',
                    'code': '$airportTo.code',
                    'country': '$airportTo.country',
                    'state': '$airportTo.state',
                    'city': '$airportTo.city'
                },
                'airline': {
                    'callsign': '$airline.callsign',
                    'name': '$airline.name',
                    'country': '$airline.country',
                    'phone': '$airline.phone',
                    'url': '$airline.url'
                }
            }
        }
    ]

    # Execute the aggregation pipeline on the second MongoDB collection
    result = collection2.aggregate(pipeline)

    response_data = []
    for each in result:
        # Extract the required fields from the aggregation result
        flying_from = each.get('flyingfrom', {})
        flying_to = each.get('flying_to', {})
        airline = each.get('airline', {})

        # Create a dictionary to store the extracted fields
        response_item = {
            "flying_from": {
                "name": flying_from.get("name", ""),
                "code": flying_from.get("code", ""),
                "country": flying_from.get("country", ""),
                "state": flying_from.get("state", ""),
                "city": flying_from.get("city", ""),
            },
            "flying_to": {
                "name": flying_to.get("name", ""),
                "code": flying_to.get("code", ""),
                "country": flying_to.get("country", ""),
                "state": flying_to.get("state", ""),
                "city": flying_to.get("city", ""),
            },
            "airline": {
                "callsign": airline.get("callsign", ""),
                "name": airline.get("name", ""),
                "country": airline.get("country", ""),
                "phone": airline.get("phone", ""),
                "url": airline.get("url", ""),
            }
        }

        response_data.append(response_item)

    return response_data

if __name__ == "__main__":


    # Uvicorn to run the FastAPI application
    uvicorn.run(app, host="0.0.0.0", port=8000)
