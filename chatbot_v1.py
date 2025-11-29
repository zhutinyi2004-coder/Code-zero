"""
Singapore Nutrition Chatbot - First Draft
Quick hackathon build - will improve later
"""



from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
from datetime import datetime

# USDA API setup - free API, just need to register
USDA_KEY = "2dPV0Hytk8xBTGn88XumjCxgp7tN8yrUC6KiQxAX"  # replace this with your actual key later
USDA_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"


app = Flask(__name__)
CORS(app)


# gonna store user data in a text file for now
# yeah i know this isnt the best way but its quick for hackathon
def save_to_file(data, filename):
    with open(filename, 'a') as f:
        f.write(json.dumps(data) + '\n')

def read_from_file(filename):
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
            return [json.loads(line.strip()) for line in lines if line.strip()]
    except:
        return []

# load singapore food data from text file
def load_sg_foods():
    foods = {}
    try:
        with open('sg_foods.txt', 'r') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line.strip())
                    foods[data['name']] = data
    except:
        # if file doesnt exist, create it with some basic foods
        create_default_foods()
        return load_sg_foods()
    return foods

# creating default food database if it doesnt exist
def create_default_foods():
    default_foods = [
        {
            "name": "chicken rice",
            "calories": 607,
            "protein": 25,
            "carbs": 78,
            "fat": 20,
            "sodium": 900
        },
        {
            "name": "nasi lemak",
            "calories": 644,
            "protein": 18,
            "carbs": 70,
            "fat": 32,
            "sodium": 1100
        },
        {
            "name": "laksa",
            "calories": 569,
            "protein": 22,
            "carbs": 56,
            "fat": 28,
            "sodium": 1800
        }
    ]
    
    with open('sg_foods.txt', 'w') as f:
        for food in default_foods:
            f.write(json.dumps(food) + '\n')

# search singapore foods first
def search_local_food(query):
    foods = load_sg_foods()
    query = query.lower()
    
    for name, info in foods.items():
        if query in name or name in query:
            return info
    return None

# call USDA API if local food not found
def search_usda(query):
    try:
        params = {
            "api_key": USDA_KEY,
            "query": query,
            "pageSize": 1
        }
        
        response = requests.get(USDA_URL, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('foods'):
                food = data['foods'][0]
                
                # extract nutrients from API response
                nutrients = {}
                for n in food.get('foodNutrients', []):
                    name = n.get('nutrientName', '').lower()
                    value = n.get('value', 0)
                    
                    if 'energy' in name:
                        nutrients['calories'] = value
                    elif 'protein' in name:
                        nutrients['protein'] = value
                    elif 'carbohydrate' in name:
                        nutrients['carbs'] = value
                    elif 'fat' in name:
                        nutrients['fat'] = value
                    elif 'sodium' in name:
                        nutrients['sodium'] = value
                
                return {
                    'name': food.get('description'),
                    **nutrients,
                    'source': 'USDA'
                }
        return None
    except Exception as e:
        print(f"API error: {e}")
        return None

# load diet myths from text file
def load_myths():
    myths = []
    try:
        with open('myths.txt', 'r') as f:
            for line in f:
                if line.strip():
                    myths.append(json.loads(line.strip()))
    except:
        # create default myths file
        create_default_myths()
        return load_myths()
    return myths

def create_default_myths():
    default_myths = [
        {
            "keywords": ["carbs bad", "carbohydrates bad"],
            "myth": "All carbs are bad",
            "truth": "Complex carbs from whole grains are actually good for you",
            "tip": "Choose brown rice over white rice"
        },
        {
            "keywords": ["fruit sugar", "fruit bad diabetes"],
            "myth": "Fruit sugar is as bad as table sugar",
            "truth": "Whole fruits have fiber which slows sugar absorption",
            "tip": "Eat whole fruits in moderation, avoid fruit juice"
        }
    ]
    
    with open('myths.txt', 'w') as f:
        for myth in default_myths:
            f.write(json.dumps(myth) + '\n')

# check if user asking about a myth
def check_for_myth(message):
    myths = load_myths()
    msg_lower = message.lower()
    
    for myth in myths:
        for keyword in myth['keywords']:
            if keyword in msg_lower:
                return myth
    return None

# Test endpoints  Demo endpoints using JSONPlaceholder API

#Health check (/, /health) - Basic server status monitoring

#Food search (/api/food/<food_name>) - Searches USDA database for nutrition data

#Error handling - All endpoints include try-catch with proper error responses

@app.route('/api/data')
def get_data():
    try:
        response = requests.get('https://jsonplaceholder.typicode.com/posts/1')
        response.raise_for_status()
        return jsonify({
            "status": "success",
            "data": response.json()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return "Flask server is running! Visit /api/data to view test data"

@app.route('/health')
def health_check():
    return jsonify({"service_status": "running", "message": "Server is working properly"})

@app.route('/api/users')
def get_users():
    try:
        response = requests.get('https://jsonplaceholder.typicode.com/users')
        response.raise_for_status()
        return jsonify({
            "status": "success",
            "count": len(response.json()),
            "users": response.json()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/api/food/<string:food_name>')
def search_food(food_name):
    try:
        params = {
            'api_key': USDA_KEY,
            'query': food_name,
            'pageSize': 5
        }
        
        response = requests.get(USDA_URL, params=params)
        response.raise_for_status()
        
        return jsonify({
            "status": "success",
            "search_term": food_name,
            "data": response.json()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# main chat endpoint
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    user_id = data.get('user_id', 'anonymous')
    
    # save chat to history file
    save_to_file({
        'user_id': user_id,
        'message': message,
        'timestamp': str(datetime.now())
    }, 'chat_history.txt')
    
    response = ""
    
    # check for diet myths first
    myth = check_for_myth(message)
    if myth:
        response = f"Myth: {myth['myth']}\n"
        response += f"Truth: {myth['truth']}\n"
        response += f"Tip: {myth['tip']}"
        return jsonify({'response': response})
    
    # check if asking about food nutrition
    if any(word in message.lower() for word in ['nutrition', 'calories', 'healthy']):
        # try local foods first
        food = search_local_food(message)
        
        if not food:
            # try API if not found locally
            food = search_usda(message)
        
        if food:
            response = f"{food.get('name', 'Food')}\n\n"
            response += f"Calories: {food.get('calories', 'N/A')}\n"
            response += f"Protein: {food.get('protein', 'N/A')}g\n"
            response += f"Carbs: {food.get('carbs', 'N/A')}g\n"
            response += f"Fat: {food.get('fat', 'N/A')}g\n"
            response += f"Sodium: {food.get('sodium', 'N/A')}mg\n"
            
            # add warnings based on singapore guidelines
            if food.get('sodium', 0) > 600:
                response += "\nWarning: High sodium! HPB recommends less than 2000mg per day"
            
            return jsonify({'response': response})
    
    # diabetes tips
    if 'diabetes' in message.lower():
        response = "Diabetes Tips (HPB Singapore):\n"
        response += "- Choose brown rice\n"
        response += "- Limit sugar intake\n"
        response += "- Eat more vegetables\n"
        response += "Good foods: Fish soup, yong tau foo"
        return jsonify({'response': response})
    
    # blood pressure tips
    if 'blood pressure' in message.lower():
        response = "Blood Pressure Tips (HPB Singapore):\n"
        response += "- Limit salt to less than 2000mg/day\n"
        response += "- Ask for less salt at hawker\n"
        response += "- Avoid instant noodles"
        return jsonify({'response': response})
    
    # default response
    response = "Hi! I can help with:\n"
    response += "- Food nutrition info\n"
    response += "- Diabetes tips\n"
    response += "- Blood pressure advice\n"
    response += "- Busting diet myths\n\n"
    response += "Try asking: 'What is the nutrition for chicken rice?'"
    
    return jsonify({'response': response})

# simple endpoint to get chat history
@app.route('/history', methods=['GET'])
def get_history():
    history = read_from_file('chat_history.txt')
    return jsonify({'history': history[-10:]})  # return last 10 chats

if __name__ == '__main__':
    from datetime import datetime
    print("Starting chatbot...")
    print("Get your free API key at: https://api.data.gov/signup/")
    app.run(debug=True, port=5000)
