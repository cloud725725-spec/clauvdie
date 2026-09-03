import os

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"


def fetch_weather(city: str) -> dict:
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    try:
        resp = requests.get(BASE_URL, params=params, timeout=10)
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if resp.status_code == 404:
            raise ValueError("City not found")
        raise
    except requests.exceptions.RequestException:
        raise ValueError("Failed to reach weather service")

    data = resp.json()
    return {
        "city": f"{data['name']}, {data['sys']['country']}",
        "temp": round(data["main"]["temp"], 1),
        "feels_like": round(data["main"]["feels_like"], 1),
        "humidity": data["main"]["humidity"],
        "pressure": data["main"]["pressure"],
        "wind_speed": data["wind"]["speed"],
        "description": data["weather"][0]["description"].capitalize(),
        "icon": data["weather"][0]["icon"],
    }


def fetch_forecast(city: str) -> list:
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    try:
        resp = requests.get(FORECAST_URL, params=params, timeout=10)
        resp.raise_for_status()
    except requests.exceptions.HTTPError:
        raise ValueError("Forecast not available")
    except requests.exceptions.RequestException:
        raise ValueError("Failed to reach weather service")

    data = resp.json()
    forecast = []
    seen = set()
    for entry in data["list"]:
        date = entry["dt_txt"].split(" ")[0]
        if date not in seen:
            seen.add(date)
            forecast.append(
                {
                    "date": date,
                    "temp": round(entry["main"]["temp"], 1),
                    "description": entry["weather"][0]["description"].capitalize(),
                    "icon": entry["weather"][0]["icon"],
                }
            )
        if len(forecast) >= 5:
            break
    return forecast


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/weather")
def weather():
    city = request.args.get("city", "").strip()
    if not city:
        return jsonify({"error": "City parameter is required"}), 400

    try:
        current = fetch_weather(city)
        forecast = fetch_forecast(city)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

    return jsonify({"current": current, "forecast": forecast})


if __name__ == "__main__":
    app.run(debug=True)
