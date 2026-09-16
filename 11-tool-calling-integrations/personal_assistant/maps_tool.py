"""Maps as an agent tool — wraps topic 6's geocode/directions logic."""

import googlemaps
from langchain.tools import tool

from personal_assistant import config

_gmaps = googlemaps.Client(key=config.MAPS_API_KEY)


@tool
def get_address_details(place: str) -> str:
    """Look up the full formatted address and coordinates for a place or
    partial address."""
    results = _gmaps.geocode(place)
    if not results:
        return f"No results found for '{place}'."
    top = results[0]
    return f"{top['formatted_address']} (lat/lng: {top['geometry']['location']})"


@tool
def get_directions(origin: str, destination: str, mode: str = "driving") -> str:
    """Get directions and estimated travel time between two places.
    mode can be 'driving', 'walking', 'bicycling', or 'transit'."""
    results = _gmaps.directions(origin, destination, mode=mode)
    if not results:
        return f"No route found from '{origin}' to '{destination}'."
    leg = results[0]["legs"][0]
    return f"{leg['distance']['text']}, about {leg['duration']['text']} by {mode}."
