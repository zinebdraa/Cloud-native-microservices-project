from flask import Flask, jsonify, request
import requests
import time
from datetime import datetime, timedelta
from flask_cors import CORS  

app = Flask(__name__)
CORS(app)  

# Service URLs
WEATHER_SERVICE = "http://localhost:5001"
OUTFIT_SERVICE = "http://localhost:5002"
WARDROBE_SERVICE = "http://localhost:5003"

# Circuit breaker state
service_status = {
    "weather": {"healthy": True, "last_failure": None, "failure_count": 0},
    "outfit": {"healthy": True, "last_failure": None, "failure_count": 0},
    "wardrobe": {"healthy": True, "last_failure": None, "failure_count": 0}
}

def circuit_breaker(service_name):
    """Simple circuit breaker pattern"""
    service = service_status[service_name]
    
    if not service["healthy"] and service["last_failure"]:
        time_since_failure = datetime.now() - service["last_failure"]
        if time_since_failure < timedelta(minutes=1):
            return False
    return True

def report_service_failure(service_name):
    service_status[service_name]["healthy"] = False
    service_status[service_name]["last_failure"] = datetime.now()
    service_status[service_name]["failure_count"] += 1
    print(f"🔴 {service_name} service marked as unhealthy")

def report_service_success(service_name):
    service_status[service_name]["healthy"] = True
    print(f"🟢 {service_name} service recovered")

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy", 
        "service": "gateway",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/service-status')
def service_status_route():
    status = {}
    
    # Check weather service
    try:
        response = requests.get(f"{WEATHER_SERVICE}/health", timeout=2)
        status["weather"] = {"status": "healthy", "response": response.json()}
        report_service_success("weather")
    except:
        status["weather"] = {"status": "unhealthy", "error": "Cannot connect"}
        report_service_failure("weather")
    
    # Check outfit service
    try:
        response = requests.get(f"{OUTFIT_SERVICE}/health", timeout=2)
        status["outfit"] = {"status": "healthy", "response": response.json()}
        report_service_success("outfit")
    except:
        status["outfit"] = {"status": "unhealthy", "error": "Cannot connect"}
        report_service_failure("outfit")
        
    # Check wardrobe service
    try:
        response = requests.get(f"{WARDROBE_SERVICE}/health", timeout=2)
        status["wardrobe"] = {"status": "healthy", "response": response.json()}
        report_service_success("wardrobe")
    except:
        status["wardrobe"] = {"status": "unhealthy", "error": "Cannot connect"}
        report_service_failure("wardrobe")
    
    return jsonify({
        "microservices_status": status,
        "circuit_breaker_state": service_status
    })

def get_weather_with_fallback(city):
    if not circuit_breaker("weather"):
        print(f"⏸️ Circuit breaker open for weather service, using fallback")
        return fallback_weather(city)
    
    try:
        response = requests.get(f"{WEATHER_SERVICE}/weather/{city}", timeout=3)
        if response.status_code == 200:
            report_service_success("weather")
            return response.json()
        else:
            report_service_failure("weather")
            return fallback_weather(city)
    except Exception as e:
        print(f"❌ Weather service error: {e}")
        report_service_failure("weather")
        return fallback_weather(city)

def fallback_weather(city):
    print(f"🔄 Using fallback weather data for {city}")
    return {
        "city": city,
        "temperature": 20,
        "condition": "clear",
        "humidity": 50,
        "source": "fallback",
        "message": "Using cached data while weather service recovers"
    }

def get_outfit_with_fallback(temperature, condition):
    if not circuit_breaker("outfit"):
        print(f"⏸️ Circuit breaker open for outfit service, using fallback")
        return fallback_outfit(temperature, condition)
    
    try:
        response = requests.get(f"{OUTFIT_SERVICE}/recommend/{temperature}/{condition}", timeout=3)
        if response.status_code == 200:
            report_service_success("outfit")
            return response.json()
        else:
            report_service_failure("outfit")
            return fallback_outfit(temperature, condition)
    except Exception as e:
        print(f"❌ Outfit service error: {e}")
        report_service_failure("outfit")
        return fallback_outfit(temperature, condition)

def fallback_outfit(temperature, condition):
    print("🔄 Using fallback outfit recommendation")
    
    if temperature > 25:
        outfit = {"base": "t-shirt", "footwear": "sandals", "accessories": ["sunglasses"]}
    elif temperature > 15:
        outfit = {"base": "long sleeves", "footwear": "sneakers", "accessories": []}
    else:
        outfit = {"base": "sweater", "footwear": "boots", "accessories": ["scarf"]}
    
    return {
        "recommendation": {
            **outfit,
            "layers": ["jacket"] if temperature < 20 else [],
            "style_tip": "Fallback recommendation while service recovers",
            "source": "fallback"
        }
    }


@app.route('/smart-outfit/<city>')
def get_smart_outfit_from_wardrobe(city):
    """
    ULTIMATE endpoint: Real weather + recommendations + YOUR actual clothes!
    """
    print(f"🎯 Getting SMART outfit for {city} using real wardrobe")
    
    # 1. Get real weather
    weather_data = get_weather_with_fallback(city)
    
    # 2. Get general recommendation
    temperature = weather_data["temperature"]
    condition = weather_data["condition"].lower()
    outfit_recommendation = get_outfit_with_fallback(temperature, condition)
    
    # 3. Match with actual clothes from wardrobe
    wardrobe_data = {}
    try:
        if circuit_breaker("wardrobe"):
            wardrobe_url = f"{WARDROBE_SERVICE}/clothes/match"
            wardrobe_payload = {
                "temperature": temperature,
                "condition": condition,
                "recommendation": outfit_recommendation["recommendation"],
                "user_id": "user123"
            }
            
            wardrobe_response = requests.post(wardrobe_url, json=wardrobe_payload, timeout=5)
            
            if wardrobe_response.status_code == 200:
                wardrobe_data = wardrobe_response.json()
                report_service_success("wardrobe")
            else:
                wardrobe_data = {"error": "Wardrobe service unavailable"}
                report_service_failure("wardrobe")
        else:
            wardrobe_data = {"error": "Wardrobe circuit breaker open"}
    except Exception as e:
        print(f"❌ Wardrobe service error: {e}")
        wardrobe_data = {"error": "Cannot connect to wardrobe service"}
        report_service_failure("wardrobe")
    
    # 4. Build complete response
    result = {
        "city": city,
        "real_weather": weather_data,
        "general_recommendation": outfit_recommendation["recommendation"],
        "your_actual_outfit": wardrobe_data.get("matched_outfit", {}),
        "wardrobe_confidence": wardrobe_data.get("match_confidence", 0),
        "system_status": {
            "weather_service": "live" if weather_data.get("source") != "fallback" else "fallback",
            "outfit_service": "live" if outfit_recommendation["recommendation"].get("source") != "fallback" else "fallback",
            "wardrobe_service": "live" if "error" not in wardrobe_data else "fallback"
        },
        "fun_message": generate_fun_message(temperature, condition)
    }
    
    return jsonify(result)

@app.route('/outfit-for-city/<city>')
def get_outfit_for_city(city):
    """
    BASIC endpoint: Real weather + general recommendations
    """
    print(f"🎯 Getting BASIC outfit for {city}")
    
    # 1. Get weather (with fallback)
    weather_data = get_weather_with_fallback(city)
    
    # 2. Get outfit recommendation (with fallback)
    temperature = weather_data["temperature"]
    condition = weather_data["condition"].lower()
    
    outfit_data = get_outfit_with_fallback(temperature, condition)
    
    # 3. Build response
    result = {
        "city": city,
        "real_weather": weather_data,
        "outfit_recommendation": outfit_data["recommendation"],
        "system_status": {
            "weather_service": "live" if weather_data.get("source") != "fallback" else "fallback",
            "outfit_service": "live" if outfit_data["recommendation"].get("source") != "fallback" else "fallback"
        },
        "fun_message": generate_fun_message(temperature, condition)
    }
    
    return jsonify(result)

def generate_fun_message(temp, condition):
    messages = {
        "rainy": "Perfect day for cozy clothes and a good book! ☔",
        "sunny": "Sun's out! Perfect weather for outdoor adventures! ☀️",
        "cloudy": "Cloudy skies but your style will shine! ⛅",
        "snow": "Winter wonderland! Stay warm and enjoy the snow! ❄️",
        "clear": "Beautiful clear day ahead! 🌟"
    }
    return messages.get(condition, "Looking great today! 💫")

if __name__ == '__main__':
    print("🚀 Starting RESILIENT Gateway Service")
    print("🔗 Features: Circuit Breaker, Fallbacks, Health Checks")
    print("📍 Endpoints:")
    print("   http://localhost:8000/outfit-for-city/amizour")
    print("   http://localhost:8000/smart-outfit/amizour")  # 🆕 THIS IS THE NEW ONE!
    print("   http://localhost:8000/service-status")
    print("   http://localhost:8000/health")
    app.run(host='0.0.0.0', port=8000, debug=True)