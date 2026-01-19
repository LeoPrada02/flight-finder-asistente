import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from config import CITY_TO_IATA

load_dotenv()

def get_amadeus_token():
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"

    data = {
        "grant_type": "client_credentials",
        "client_id": os.getenv("AMADEUS_API_KEY"),
        "client_secret": os.getenv("AMADEUS_API_SECRET"),
    }

    response = requests.post(url, data=data)
    response.raise_for_status()

    return response.json()["access_token"]



now = datetime.now()
tomorrow = now + timedelta(days=1)

def fetch_flight_price(origin_iata, destination_iata): #YYYY-MM-DD
    token = get_amadeus_token()

    url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    params = {
        "originLocationCode": origin_iata,
        "destinationLocationCode": destination_iata,
        "departureDate": tomorrow.strftime("%Y-%m-%d"),
        "adults": 1,
        "max": 1,
        "currencyCode": "ARS"
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    data = response.json()

    if not data["data"]:
        return "No flights found"

    price = data["data"][0]["price"]["total"]
    currency = data["data"][0]["price"]["currency"]

    return f"{price} {currency}", response.json()


def get_ticket_price(origin_city, destination_city):
    print(f"buscando vuelos {origin_city} -> {destination_city}")

    origin_iata = CITY_TO_IATA.get(origin_city.lower())
    destination_iata = CITY_TO_IATA.get(destination_city.lower())

    if not origin_iata or not destination_iata:
        return "Unknown origin or destination"

    try:
        return fetch_flight_price(origin_iata, destination_iata)
    except Exception as e:
        return f"API error: {str(e)}"
