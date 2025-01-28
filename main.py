from flask import Flask, jsonify

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from dotenv import load_dotenv
import os, requests, json

import redis
import time

#We manage API_KEY with .env
load_dotenv()
API_KEY = os.getenv("API_KEY")

app = Flask(__name__)#Initialize API.

#Limit API with default_limits.
limiter = Limiter(
    get_remote_address,
    app=app,
    storage_uri="redis://localhost:6379",
    storage_options={"socket_connect_timeout": 30},
    strategy="fixed-window",
    default_limits=["10 per day", "10 per hour"],
)

#Connection with redis cache.
r = redis.Redis(host='localhost', port=6379, db=0)

def timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()  # Start the timer
        result = func(*args, **kwargs)  # Call the actual function
        end_time = time.time()  # End the timer
        elapsed_time = end_time - start_time
        print(f"Function '{func.__name__}' executed in {elapsed_time:.4f} seconds.")
        return result
    return wrapper

#Endpoint for find weather by city or country.
@app.route("/<city>")
@limiter.limit("100 per hour")
@timer
def city_weather(city: str):
    #Check first cache information.
    bytes_data = r.get(city)
    if bytes_data is not None:
        decode_data = bytes_data.decode('utf-8')
        dict_data = json.loads(decode_data)
        return jsonify(dict_data), 200
    else: 
        #We get the total weather information from the third api.
        url = f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}?key={API_KEY}'
        response = requests.get(url)
        
        #If the country is not found we get 404 with jsonify.
        if response.status_code == 400:
            return jsonify("Error: We don't find {city}"), 404
            # return f"Error: We don't find {city}"
        elif response.status_code != 200:
            return jsonify({"error": f"Unexpected error: {response.status_code}"}), response.status_code
        #We manage the information with json because redis doesn't save dicts.
        organized_data = clear_response(response.json())
        info = json.dumps(organized_data)

        #We put expiration time by seconds and we save the information in the redis cache.
        r.set(city, info, ex=10)
        
        return jsonify(organized_data), 200



#We classify the weather information.
def clear_response(data: dict):
    return {"City": data["address"],
            "Date": data["days"][0]["datetime"],
            "Temperature": data["days"][0]["temp"],
            "Humidity": data["days"][0]["humidity"],
            "Wind": data["days"][0]["windspeed"]
            }

#Endpoint to clean the cache if the expiration time is deleted.
@app.route("/clear")
def clear_cache():
    cache = r.get_cache()
    cache.flush()
    return "Cache cleaned"


