# outfit-service/app.py
from flask import Flask, jsonify

app = Flask(__name__)

# Clothing rules engine
def get_outfit_recommendation(temperature, condition):
    recommendations = {
        "base": "",
        "layers": [],
        "accessories": [],
        "footwear": "",
        "style_tip": ""
    }
    
    # Temperature-based logic
    if temperature < 0:
        recommendations.update({
            "base": "thermal wear",
            "layers": ["warm sweater", "winter coat"],
            "accessories": ["scarf", "gloves", "beanie"],
            "footwear": "insulated boots",
            "style_tip": "Layer up! It's freezing out there ❄️"
        })
    elif temperature < 10:
        recommendations.update({
            "base": "long-sleeve shirt",
            "layers": ["jacket or hoodie"],
            "accessories": ["scarf"],
            "footwear": "closed shoes or boots", 
            "style_tip": "Perfect jacket weather! 🍂"
        })
    elif temperature < 20:
        recommendations.update({
            "base": "t-shirt or light sweater",
            "layers": ["light jacket (optional)"],
            "accessories": [],
            "footwear": "sneakers or casual shoes",
            "style_tip": "Comfortable and casual 🌤️"
        })
    else:
        recommendations.update({
            "base": "t-shirt or tank top",
            "layers": [],
            "accessories": ["sunglasses"],
            "footwear": "sandals or breathable shoes",
            "style_tip": "Stay cool and hydrated! ☀️"
        })
    
    # Weather condition adjustments
    if condition == "rainy":
        recommendations["accessories"].append("umbrella")
        recommendations["footwear"] = "waterproof shoes"
        recommendations["style_tip"] += " Don't forget rain protection! ☔"
    elif condition == "snow":
        recommendations["accessories"].extend(["warm gloves", "earmuffs"])
        recommendations["style_tip"] += " Winter wonderland ready! ⛄"
    elif condition == "sunny":
        recommendations["accessories"].append("sunglasses")
        recommendations["style_tip"] += " Perfect for sunglasses! 😎"
    
    return recommendations

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "outfit"})

@app.route('/recommend/<int:temperature>/<condition>', methods=['GET'])
def recommend_outfit(temperature, condition):
    try:
        recommendation = get_outfit_recommendation(temperature, condition)
        return jsonify({
            "temperature": temperature,
            "condition": condition,
            "recommendation": recommendation
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)