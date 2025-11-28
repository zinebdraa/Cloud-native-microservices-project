from flask import Flask, jsonify, request
import os
import uuid
from datetime import datetime

app = Flask(__name__)

# In-memory "database" - in real app, use PostgreSQL/MongoDB
user_clothes = {
    "user123": [
        {
            "id": "1",
            "name": "Blue T-Shirt",
            "type": "top",
            "color": "blue", 
            "warmth": 1,  # 1=light, 2=medium, 3=warm
            "category": "casual",
            "image_url": "/images/blue-tshirt.jpg"
        },
        {
            "id": "2", 
            "name": "Black Jeans",
            "type": "bottom",
            "color": "black",
            "warmth": 2,
            "category": "casual",
            "image_url": "/images/black-jeans.jpg"
        },
        {
            "id": "3",
            "name": "Red Jacket", 
            "type": "layer",
            "color": "red",
            "warmth": 3,
            "category": "casual", 
            "image_url": "/images/red-jacket.jpg"
        },
        {
            "id": "4",
            "name": "Running Shoes",
            "type": "footwear", 
            "color": "white",
            "warmth": 2,
            "category": "sports",
            "image_url": "/images/running-shoes.jpg"
        },
        {
            "id": "5",
            "name": "Winter Boots",
            "type": "footwear",
            "color": "brown", 
            "warmth": 3,
            "category": "winter",
            "image_url": "/images/winter-boots.jpg"
        },
        {
            "id": "6",
            "name": "Summer Dress",
            "type": "dress",
            "color": "yellow",
            "warmth": 1,
            "category": "summer",
            "image_url": "/images/summer-dress.jpg"
        }
    ]
}

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": "wardrobe",
        "clothes_count": len(user_clothes["user123"]),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/clothes', methods=['GET'])
def get_all_clothes():
    """Get all clothes for a user"""
    user_id = request.args.get('user_id', 'user123')
    return jsonify({
        "user_id": user_id,
        "clothes": user_clothes.get(user_id, []),
        "total_items": len(user_clothes.get(user_id, []))
    })

@app.route('/clothes/add', methods=['POST'])
def add_clothing():
    """Add a new clothing item"""
    user_id = request.json.get('user_id', 'user123')
    new_item = {
        "id": str(uuid.uuid4())[:8],
        "name": request.json['name'],
        "type": request.json['type'],
        "color": request.json['color'],
        "warmth": request.json['warmth'],
        "category": request.json.get('category', 'casual'),
        "image_url": request.json.get('image_url', '/images/default.jpg'),
        "added_date": datetime.now().isoformat()
    }
    
    if user_id not in user_clothes:
        user_clothes[user_id] = []
    
    user_clothes[user_id].append(new_item)
    
    return jsonify({
        "message": "Clothing item added successfully",
        "item": new_item,
        "total_items": len(user_clothes[user_id])
    })

@app.route('/clothes/match', methods=['POST'])
def match_clothes_to_weather():
    """
    Match user's actual clothes to weather conditions
    This is where the magic happens!
    """
    user_id = request.json.get('user_id', 'user123')
    temperature = request.json['temperature']
    condition = request.json['condition']
    recommendation = request.json.get('recommendation', {})
    
    user_items = user_clothes.get(user_id, [])
    
    print(f"🎯 Matching clothes for {temperature}°C, {condition}")
    
    # Smart matching algorithm
    matched_outfit = find_best_outfit(user_items, temperature, condition, recommendation)
    
    return jsonify({
        "weather_conditions": {"temperature": temperature, "condition": condition},
        "recommendation": recommendation,
        "matched_outfit": matched_outfit,
        "match_confidence": matched_outfit["confidence"],
        "message": "Found the perfect outfit from your wardrobe! 👗"
    })

def find_best_outfit(clothes, temperature, condition, recommendation):
    """Smart algorithm to find best outfit combination"""
    
    # Determine warmth level needed
    if temperature < 5:
        needed_warmth = 3  # Very warm
    elif temperature < 15:
        needed_warmth = 2  # Medium warm
    else:
        needed_warmth = 1  # Light
    
    # Filter clothes by type and warmth
    tops = [item for item in clothes if item['type'] in ['top', 'dress'] and item['warmth'] <= needed_warmth]
    bottoms = [item for item in clothes if item['type'] == 'bottom' and item['warmth'] <= needed_warmth]
    layers = [item for item in clothes if item['type'] == 'layer' and item['warmth'] >= needed_warmth]
    footwear = [item for item in clothes if item['type'] == 'footwear']
    
    # Weather-specific adjustments
    if condition == "rainy":
        footwear = [item for item in footwear if item['category'] != 'summer']
    elif condition == "snow":
        footwear = [item for item in footwear if item['category'] == 'winter']
    elif condition == "sunny":
        tops = [item for item in tops if item['color'] not in ['black', 'navy']]  # Prefer lighter colors
    
    # Select best matches
    selected_top = tops[0] if tops else {"name": "No top found", "type": "top"}
    selected_bottom = bottoms[0] if bottoms else {"name": "No bottom found", "type": "bottom"}
    selected_layer = layers[0] if layers else None
    selected_footwear = footwear[0] if footwear else {"name": "No footwear found", "type": "footwear"}
    
    # Calculate confidence score
    confidence = min(len(tops), len(bottoms), len(footwear)) / 3.0
    
    return {
        "top": selected_top,
        "bottom": selected_bottom,
        "layer": selected_layer,
        "footwear": selected_footwear,
        "confidence": round(confidence, 2),
        "outfit_style": get_outfit_style(selected_top, selected_bottom),
        "fashion_advice": get_fashion_advice(temperature, condition)
    }

def get_outfit_style(top, bottom):
    colors = [top.get('color', ''), bottom.get('color', '')]
    if any(c in ['red', 'yellow', 'pink'] for c in colors):
        return "bold and colorful"
    elif all(c in ['black', 'white', 'gray'] for c in colors):
        return "minimalist and chic"
    else:
        return "casual and stylish"

def get_fashion_advice(temp, condition):
    advice = {
        "rainy": "💧 Perfect for that stylish raincoat!",
        "sunny": "😎 Rock those sunglasses with confidence!",
        "snow": "⛄ Cozy and warm never looked so good!",
        "cloudy": "☁️ Your outfit will brighten the day!"
    }
    return advice.get(condition, "✨ You're going to look amazing!")

if __name__ == '__main__':
    print("👕 Starting Wardrobe Service on port 5003")
    print("📁 Manages user's clothing inventory")
    print("🎯 Smart outfit matching from real clothes")
    print("📍 Endpoint: http://localhost:5003/clothes")
    app.run(host='0.0.0.0', port=5003, debug=True)