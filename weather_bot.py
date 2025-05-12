import requests

def get_coordinates(city):
    url = "https://nominatim.openstreetmap.org/search"
    headers = {
        "User-Agent": "PokemonWeatherBot (email@example.com)"
    }
    params = {
        "q": city,
        "format": "json",
        "limit": 1
    }
    response = requests.get(url, headers=headers, params=params).json()
    if not response:
        return None
    return {
        "lat": response[0]["lat"],
        "lon": response[0]["lon"]
    }

def get_weather(lat, lon):
    points_url = f"https://api.weather.gov/points/{lat},{lon}"
    points_response = requests.get(points_url).json()
    
    if "properties" not in points_response:
        return None

    forecast_url = points_response["properties"]["forecast"]
    forecast_response = requests.get(forecast_url).json()
    
    if "properties" not in forecast_response:
        return None
    
    current_weather = forecast_response["properties"]["periods"][0]
    return {
        "condition": current_weather["shortForecast"],
        "temperature": current_weather["temperature"],
        "unit": current_weather["temperatureUnit"]
    }

def main():
    city = input("Enter a city/state: ")
    
    coords = get_coordinates(city)
    if not coords:
        print("Error: Location not found.")
        return
    
    weather = get_weather(coords["lat"], coords["lon"])
    if not weather:
        print("Error: Couldn't fetch weather.")
        return
        
    print(f"Weather in {city}:")
    print(f"Condition: {weather['condition']}")
    print(f"Temperature: {weather['temperature']}°{weather['unit']}")

if __name__ == "__main__":
    main()
