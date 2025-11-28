from flask import Flask, jsonify
import requests
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

env_locations = [
    Path(__file__).parent / '.env',          
    Path(__file__).parent.parent / '.env',   
    Path('.env'),                             
]

for env_file in env_locations:
    if env_file.exists():
        print(f"📁 Loading .env from: {env_file}")
        load_dotenv(dotenv_path=env_file)
        break
else:
    print("⚠️ No .env file found, checking environment variables...")
    load_dotenv()  

app = Flask(__name__)

# Get your free API key from https://openweathermap.org/api
# API_KEY = "c1e5437f731b74d1a78ab5e73e2cfc28" 
API_KEY = os.getenv('OPENWEATHER_API_KEY') 

if not API_KEY:
    raise ValueError("⚠️ OPENWEATHER_API_KEY not set! Check your .env file")

def get_real_weather(city):
    """Get REAL weather data from OpenWeatherMap API"""
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=en"
        
        print(f"🌐 Fetching REAL weather for: {city}")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            return {
                "city": data["name"],
                "country": data["sys"]["country"],
                "temperature": round(data["main"]["temp"]),
                "feels_like": round(data["main"]["feels_like"]),
                "condition": data["weather"][0]["main"],
                "description": data["weather"][0]["description"],
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"],
                "pressure": data["main"]["pressure"],
                "visibility": data.get("visibility", "N/A"),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source": "OpenWeatherMap API",
                "coordinates": {
                    "lat": data["coord"]["lat"],
                    "lon": data["coord"]["lon"]
                }
            }
        else:
            return {"error": f"City '{city}' not found or API error"}
            
    except requests.exceptions.Timeout:
        return {"error": "Weather API timeout"}
    except Exception as e:
        return {"error": f"API call failed: {str(e)}"}

@app.route('/')
def home():
    return """
    <h1>🌤️ Real Weather Microservice</h1>
    <p>Try these endpoints:</p>
    <ul>
        <li><a href="/weather/amizour">/weather/amizour</a></li>
        <li><a href="/weather/algiers">/weather/algiers</a></li>
        <li><a href="/weather/paris">/weather/paris</a></li>
        <li><a href="/health">/health</a></li>
    </ul>
    <p><em>Real-time data from OpenWeatherMap API</em></p>
    """

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy", 
        "service": "real-weather",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/weather/<city>')
def get_weather(city):
    print(f"📍 Received request for: {city}")
    
    weather_data = get_real_weather(city)
    
    if "error" in weather_data:
        return jsonify({
            "error": weather_data["error"],
            "try_cities": ["amizour", "algiers", "paris", "london", "newyork"],
            "api_guide": "Get free API key from https://openweathermap.org/api"
        }), 404
    
    return jsonify(weather_data)

@app.route('/compare/<city1>/<city2>')
def compare_weather(city1, city2):
    """Compare real weather between two cities"""
    weather1 = get_real_weather(city1)
    weather2 = get_real_weather(city2)
    
    return jsonify({
        "comparison": {
            "city1": weather1,
            "city2": weather2
        },
        "warmer": city1 if weather1.get("temperature", 0) > weather2.get("temperature", 0) else city2
    })

if __name__ == '__main__':
    print("🚀 Starting REAL Weather Microservice...")
    print("🌐 Using Live OpenWeatherMap API")
    print("📡 Endpoint: http://localhost:5001/weather/amizour")
    print("⚠️  Don't forget to add your REAL API key!")
    app.run(host='0.0.0.0', port=5001, debug=True)