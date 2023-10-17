# Flight Route API

The Flight Route API is built using FastAPI, a modern web framework for building APIs with Python. This section provides an overview of the API, its features, and the endpoints available.

### Features

- **Airport Autocompletion**: The API allows you to search for airports by providing a prefix, which can be a part of the airport code, name, or city. This feature is useful for quickly finding airports.

- **Fetch Flight Routes**: You can retrieve flight routes using this API based on specific criteria. You need to specify the source airport (fromiata), destination airport (toiata), and the day of the week. The API will return matching flight routes that meet these criteria.

- **Detailed Itinerary**: The API also provides the ability to obtain detailed information about a specific flight route. You can provide the `route_id`, and the API will return detailed information about the departure and arrival airports, the airline, and more.

### Prerequisites

Before running the API, ensure you have the following dependencies installed:

- **Python (3.6 or higher)**: The programming language used to build the API.

- **FastAPI**: The web framework used for creating the API.

- **Pydantic**: A data validation library used for defining request and response models.

- **pymongo**: The Python driver for MongoDB, used for database interaction.

- **bson**: A library for handling Binary JSON (BSON) data, which is used for interacting with MongoDB.

- **uvicorn**: A lightweight ASGI server used to run the FastAPI application.

- **MongoDB**: A NoSQL database used for storing flight data.

Please install these dependencies using `pip` before running the API.

### Configuration

The API is configured to connect to a MongoDB database for storing and retrieving flight data. To set up your MongoDB connection, update the MongoDB connection settings in the code. Specifically, modify the following line with your database connection details:

```python
client = MongoClient('mongodb+srv://username:password@your-mongodb-cluster-url')
```

Replace `'username'`, `'password'`, and `'your-mongodb-cluster-url'` with your MongoDB credentials and cluster URL.

### Installation

To run the API, follow these installation steps:

1. Clone this repository to your local machine to get the API source code.

2. Install the required Python dependencies using `pip` as follows:

   ```bash
   pip install fastapi pydantic pymongo uvicorn
   ```

3. Update the MongoDB connection settings in the code as mentioned in the "Configuration" section.

### Usage

To use the API, follow these steps:

1. Run the FastAPI application using Uvicorn. Replace `'your_program_filename'` with the name of the Python file containing your FastAPI application:

   ```bash
   uvicorn your_program_filename:app --host 0.0.0.0 --port 8000
   ```

   This command starts the API and makes it accessible over the network.

2. Access the API using a web browser, Postman, or any HTTP client. You can make HTTP requests to the provided API endpoints.

Certainly, let's expand the "Endpoints" section of the README with sample payloads for each of the API endpoints. This will provide a clear understanding of how to structure requests when interacting with the API.

### Endpoints

The API provides the following endpoints, along with sample payloads for request bodies and explanations:

#### 1. **Airport Autocompletion Endpoint**

- **URL**: `/search`
- **Method**: POST
- **Input**: Provide a JSON body with the `prefix` parameter, containing the search prefix. For example:

```json
{
  "prefix": "LAX"
}
```

   - **Explanation**: In this example, we're searching for airports that match the prefix "LAX." The API will return airports whose code, name, or city contain "LAX."

- **Output**: The endpoint returns a JSON array of matching airports. Sample response:

```json
[
  {
    "id": "1",
    "code": "LAX",
    "name": "Los Angeles International Airport",
    "city": "Los Angeles",
    "country": "United States",
    "state": "California"
  },
  {
    "id": "2",
    "code": "KLAX",
    "name": "Los Angeles International Airport",
    "city": "Los Angeles",
    "country": "United States",
    "state": "California"
  }
]
```

   - **Explanation**: The response includes an array of airports that match the provided prefix. Each airport object includes an ID, airport code, name, city, country, and state.

#### 2. **Fetch Flight Routes Endpoint**

- **URL**: `/fetch_routes`
- **Method**: POST
- **Input**: Provide a JSON body with a list of flight route criteria. For example:

```json
{
  "routes": [
    {
      "fromiata": "JFK",
      "toiata": "LAX",
      "daynumber": 3
    }
  ]
}
```

   - **Explanation**: In this example, we're requesting flight routes from John F. Kennedy International Airport (JFK) to Los Angeles International Airport (LAX) for day 3 (Wednesday).

- **Output**: The endpoint returns a JSON array of matching flight routes. Sample response:

```json
[
  {
    "routes": [
      {
        "airportFromIATA": "JFK",
        "airportToIATA": "LAX",
        "flightNumber": "AA101",
        "day3": "yes",
        "departureTime": "09:00 AM",
        "arrivalTime": "11:30 AM",
        "airlineIATA": "AA"
      }
    ],
    "message": "Routes found"
  }
]
```

   - **Explanation**: The response includes an array of flight routes that match the specified criteria. Each route object contains details such as source airport (airportFromIATA), destination airport (airportToIATA), flight number, and more.

#### 3. **Detailed Itinerary Endpoint**

- **URL**: `/get_detailed_itinerary`
- **Method**: POST
- **Input**: Provide a JSON body with the `route_id` parameter to fetch detailed information about a specific flight route. For example:

```json
{
  "route_id": 1
}
```

   - **Explanation**: In this example, we're requesting detailed information about the flight route with ID 1.

- **Output**: The endpoint returns a JSON object with detailed itinerary information. Sample response:

```json
[
  {
    "flying_from": {
      "name": "John F. Kennedy International Airport",
      "code": "JFK",
      "country": "United States",
      "state": "New York",
      "city": "New York"
    },
    "flying_to": {
      "name": "Los Angeles International Airport",
      "code": "LAX",
      "country": "United States",
      "state": "California",
      "city": "Los Angeles"
    },
    "airline": {
      "callsign": "AA",
      "name": "American Airlines",
      "country": "United States",
      "phone": "+1-800-433-7300",
      "url": "https://www.aa.com/"
    }
  }
]
```

   - **Explanation**: The response includes detailed information about the specified flight route, including the departure and arrival airports and airline information.

These sample payloads and explanations should help users understand how to structure requests when using the API and what to expect in the API's responses.

### Contributors

- Ken Binoy

- binoy.ken@gmail.com



