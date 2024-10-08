from flask import Flask, jsonify

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import os, requests, json, redis
from redis.cache import CacheConfig

#We manage API_KEY with .env
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
r = redis.Redis(
    protocol=3,
    cache_config=CacheConfig(),
    encoding= "utf-8",
    decode_responses=True
)

#Endpoint for find weather by city or country.
@app.route("/<city>")
@limiter.limit("100 per hour")

def city_weather(city: str):
    #Check first cache information.
    cache =  check_cache(city)
    if cache:
        return jsonify(cache), 200
    else:
        #We get the total weather information from the third api.
        url = f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}?key={API_KEY}'
        response = requests.get(url)
        
        #If the country is not found we get 404 with jsonify.
        if response.status_code != 200:
            return jsonify("Error: We don't find {city}"), 404
            # return f"Error: We don't find {city}"

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

#Get values from the cache if it have previous information.
def check_cache(city):
    try:
        cache_response: dict = r.get(city)
        return cache_response
    except:
        return False

#Endpoint to clean the cache if the expiration time is deleted.
@app.route("/clear")
def clear_cache():
    cache = r.get_cache()
    cache.flush()
    return "Cache cleaned"


