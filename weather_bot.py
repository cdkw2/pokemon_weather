import os
import json
from pathlib import Path
import discord
import requests
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

def load_pokemon_mappings():
    try:
        with open(Path(__file__).parent / "pokemon_mappings.json") as f:
            data = json.load(f)
            return data["mappings"]
    except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
        print(f"Error loading mappings: {e}")
        return {}

POKEMON_MAPPINGS = load_pokemon_mappings()

def get_coordinates(city):
    url = "https://nominatim.openstreetmap.org/search"
    headers = {"User-Agent": "PokemonWeatherBot/1.0"}
    params = {"q": city, "format": "json", "limit": 1}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return {"lat": data[0]["lat"], "lon": data[0]["lon"]} if data else None
    except requests.RequestException:
        return None

def get_weather(lat, lon):
    try:
        points_url = f"https://api.weather.gov/points/{lat},{lon}"
        points_response = requests.get(points_url, timeout=10)
        points_response.raise_for_status()
        forecast_url = points_response.json()["properties"]["forecast"]
        
        forecast_response = requests.get(forecast_url, timeout=10)
        forecast_response.raise_for_status()
        return forecast_response.json()["properties"]["periods"][0]
    except (requests.RequestException, KeyError):
        return None

@tree.command(name="pokeweather", description="Get Pokémon-themed weather!")
async def pokeweather(interaction: discord.Interaction, location: str):
    await interaction.response.defer()
    
    coords = get_coordinates(location)
    if not coords:
        return await interaction.followup.send("⚠️ Location not found!")
    
    weather = get_weather(coords["lat"], coords["lon"])
    if not weather:
        return await interaction.followup.send("⚠️ Weather data unavailable!")
    
    condition = weather["shortForecast"]
    pokemon = POKEMON_MAPPINGS.get(condition, POKEMON_MAPPINGS["_default"])
    
    embed = discord.Embed(
        title=pokemon["message"],
        color=discord.Color.random()
    )
    embed.add_field(name="Location", value=location, inline=True)
    embed.add_field(name="Temperature", value=f"{weather['temperature']}°{weather['temperatureUnit']}", inline=True)
    embed.add_field(name="Condition", value=condition, inline=False)
    embed.set_image(url=pokemon["gif"])
    embed.set_footer(text=f"Featured Pokémon: {pokemon['pokemon']}")
    
    await interaction.followup.send(embed=embed)

@client.event
async def on_ready():
    print(f"Logged in as {client.user.name} (ID: {client.user.id})")
    await tree.sync()

client.run(TOKEN)
