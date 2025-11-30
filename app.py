"""
Singapore Nutrition Chatbot - Flask Backend
Integrated with frontend, all data in text files
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # enable cross-origin requests

# load config file
def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

config = load_config()

# get api settings from config
USDA_KEY = config['api']['usda_key']
USDA_URL = config['api']['usda_url']

# get file paths from config
FILES = config['files']
HPB_GUIDELINES = config['hpb_guidelines']

# make sure data directory exists
os.makedirs('data', exist_ok=True)

# save to text file with utf-8
def save_to_file(data, filename):
    """save data as json line to text file"""
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False) + '\n')

# read from text file with comment handling
def read_from_file(filename):
    """read json lines from text file, skip comments and handle errors"""
    try:
        # create file if doesnt exist
        if not os.path.exists(filename):
            return []
        
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            data = []
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                
                # skip empty lines and comment lines (starting with #)
                if not line or line.startswith('#'):
                    continue
                
                try:
                    # try to parse as json
                    item = json.loads(line)
                    data.append(item)
                except json.JSONDecodeError as e:
                    # print warning but continue
                    print(f"warning: line {line_num} in {filename} has invalid json - skipping")
                    continue
            
            return data
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"error reading file {filename}: {e}")
        return []

# load singapore foods from text file
def load_sg_foods():
    """load local food database"""
    foods = {}
    data = read_from_file(FILES['sg_foods'])
    for item in data:
        # store with lowercase key for case-insensitive matching
        foods[item['name'].lower()] = item
    return foods

# search local food database
def search_local_food(query):
    """search for food in local database"""
    foods = load_sg_foods()
    query = query.lower()
    
    # direct match first
    if query in foods:
        return foods[query]
    
    # partial match
    for name, info in foods.items():
        if query in name or name in query:
            return info
    
    return None

# call usda api with better error handling
def search_usda(query):
    """search usda fooddata central api"""
    try:
        params = {
            "api_key": USDA_KEY,
            "query": query,
            "pageSize": 1
        }
        
        response = requests.get(USDA_URL, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('foods') and len(data['foods']) > 0:
                food = data['foods'][0]
                
                # extract nutrients
                nutrients = {}
                for n in food.get('foodNutrients', []):
                    name = n.get('nutrientName', '').lower()
                    value = n.get('value', 0)
                    
                    if 'energy' in name or 'calorie' in name:
                        nutrients['calories'] = value
                    elif 'protein' in name:
                        nutrients['protein'] = value
                    elif 'carbohydrate' in name:
                        nutrients['carbs'] = value
                    elif 'total lipid' in name or ('fat' in name and 'fatty' not in name):
                        nutrients['fat'] = value
                    elif 'sodium' in name:
                        nutrients['sodium'] = value
                    elif 'fiber' in name:
                        nutrients['fiber'] = value
                    elif 'sugar' in name and 'added' not in name:
                        nutrients['sugar'] = value
                
                return {
                    'name': food.get('description'),
                    **nutrients,
                    'source': 'USDA'
                }
        
        return None
    except requests.RequestException as e:
        print(f"api request error: {e}")
        return None
    except Exception as e:
        print(f"unexpected api error: {e}")
        return None

# load myths from text file
def load_myths():
    """load diet myths database"""
    return read_from_file(FILES['myths'])

# check if message contains a myth
def check_myth(message):
    """check if user message relates to a diet myth"""
    myths = load_myths()
    msg = message.lower()
    
    for myth in myths:
        for keyword in myth.get('keywords', []):
            if keyword.lower() in msg:
                return myth
    return None

# load healthy swaps from text file
def load_swaps():
    """load healthy food swaps database"""
    return read_from_file(FILES['swaps'])

# get swaps based on condition
def get_swaps(condition=None, limit=None):
    """get food swaps, optionally filtered by health condition"""
    all_swaps = load_swaps()
    
    if condition:
        filtered = [s for s in all_swaps if s.get('category') == condition]
    else:
        filtered = all_swaps
    
    if limit:
        return filtered[:limit]
    return filtered

# save chat to history in readable text format
def save_chat_history(user_message, bot_response):
    """save conversation to history in readable text format"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(FILES['chat_history'], 'a', encoding='utf-8') as f:
        f.write(f"\n{'='*60}\n")
        f.write(f"[{timestamp}]\n")
        f.write(f"User: {user_message}\n")
        f.write(f"Bot: {bot_response}\n")

# main chat processing function
def process_chat(message):
    """process user message and return response"""
    
    # check for myths first
    myth = check_myth(message)
    if myth:
        response = f"🚫 Myth Busted!\n\n"
        response += f"Myth: {myth['myth']}\n\n"
        response += f"✅ Truth: {myth['truth']}\n\n"
        response += f"💡 Tip: {myth['tip']}"
        return response
    
    # check for food nutrition queries
    food_keywords = ['nutrition', 'calories', 'healthy', 'info', 'nutrient', 'nutritional']
    if any(word in message.lower() for word in food_keywords):
        # search local first
        food = search_local_food(message)
        
        # try api if not found locally
        if not food:
            food = search_usda(message)
        
        if food:
            response = f"🍽️ {food.get('name', 'Food').upper()}\n"
            response += "─" * 30 + "\n"
            response += f"Calories: {food.get('calories', 'N/A')} kcal\n"
            response += f"Protein: {food.get('protein', 'N/A')}g\n"
            response += f"Carbs: {food.get('carbs', 'N/A')}g\n"
            response += f"Fat: {food.get('fat', 'N/A')}g\n"
            response += f"Sodium: {food.get('sodium', 'N/A')}mg\n"
            response += f"Fiber: {food.get('fiber', 'N/A')}g\n"
            response += f"Sugar: {food.get('sugar', 'N/A')}g\n"
            
            # warnings based on hpb guidelines
            if food.get('sodium', 0) > 600:
                response += f"\n⚠️ High sodium! HPB recommends {HPB_GUIDELINES['blood_pressure']['sodium_limit']}"
            if food.get('sugar', 0) > 10:
                response += "\n⚠️ High sugar content"
            
            return response
        else:
            return "❌ Couldn't find that food. Try: chicken rice, nasi lemak, laksa"
    
    # diabetes management
    if 'diabetes' in message.lower():
        response = "💉 Diabetes Management (HPB Singapore):\n\n"
        response += f"• Fasting glucose target: {HPB_GUIDELINES['diabetes']['fasting_glucose_normal']}\n"
        response += f"• Sugar limit: {HPB_GUIDELINES['diabetes']['sugar_limit']}\n"
        response += f"• Fiber: {HPB_GUIDELINES['diabetes']['fiber_recommendation']}\n"
        response += "• Good SG foods: Fish soup, yong tau foo, economic rice (more veg)\n"
        response += "• Avoid: Sugary drinks, fried noodles\n"
        
        # show relevant swaps
        swaps = get_swaps('diabetes', limit=3)
        if swaps:
            response += "\n🔄 Healthy Swaps:\n"
            for swap in swaps:
                response += f"  ❌ {swap['unhealthy']} → ✅ {swap['healthy']}\n"
        
        return response
    
    # blood pressure management
    if 'blood pressure' in message.lower() or 'hypertension' in message.lower():
        response = "❤️ Blood Pressure Management (HPB Singapore):\n\n"
        response += f"• Normal BP: {HPB_GUIDELINES['blood_pressure']['normal']}\n"
        response += f"• Sodium limit: {HPB_GUIDELINES['blood_pressure']['sodium_limit']}\n"
        response += "• Ask for 'less salt' at hawker centers\n"
        response += "• Avoid: Instant noodles, processed meats\n"
        
        # show relevant swaps
        swaps = get_swaps('blood_pressure', limit=3)
        if swaps:
            response += "\n🔄 Healthy Swaps:\n"
            for swap in swaps:
                response += f"  ❌ {swap['unhealthy']} → ✅ {swap['healthy']}\n"
        
        return response
    
    # cholesterol management
    if 'cholesterol' in message.lower():
        response = "🩺 Cholesterol Management (HPB Singapore):\n\n"
        response += f"• LDL target: {HPB_GUIDELINES['cholesterol']['ldl_target']}\n"
        response += "• Choose grilled/steamed over fried\n"
        response += "• Use olive oil or canola oil\n"
        response += "• Eat fatty fish 2x per week\n"
        
        # show relevant swaps
        swaps = get_swaps('cholesterol', limit=3)
        if swaps:
            response += "\n🔄 Healthy Swaps:\n"
            for swap in swaps:
                response += f"  ❌ {swap['unhealthy']} → ✅ {swap['healthy']}\n"
        
        return response
    
    # show healthy swaps
    if 'swap' in message.lower() or 'alternative' in message.lower():
        swaps = load_swaps()
        response = "🔄 Healthy Food Swaps:\n\n"
        for swap in swaps[:8]:
            response += f"❌ {swap['unhealthy']} → ✅ {swap['healthy']}\n"
            response += f"   💡 {swap['benefit']}\n\n"
        
        return response
    
    # default help message
    response = "👋 Hi! I can help with:\n\n"
    response += "1. Food nutrition (try: 'nutrition for chicken rice')\n"
    response += "2. Diabetes management\n"
    response += "3. Blood pressure advice\n"
    response += "4. Cholesterol tips\n"
    response += "5. Bust diet myths (try: 'are carbs bad?')\n"
    response += "6. Healthy food swaps\n\n"
    response += "✅ Based on Singapore HPB guidelines"
    
    return response

# flask routes

@app.route('/')
def index():
    """serve the frontend html"""
    return send_from_directory('.', 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """main chat endpoint"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'no message provided'}), 400
        
        # process the message
        bot_response = process_chat(user_message)
        
        # save to history
        save_chat_history(user_message, bot_response)
        
        return jsonify({
            'response': bot_response,
            'status': 'success'
        })
    
    except Exception as e:
        print(f"error in chat endpoint: {e}")
        return jsonify({
            'error': str(e),
            'response': 'sorry, i encountered an error. please try again.'
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'api_configured': USDA_KEY != 'DEMO_KEY',
        'files_loaded': {
            'foods': len(load_sg_foods()),
            'myths': len(load_myths()),
            'swaps': len(load_swaps())
        }
    })

# main
if __name__ == '__main__':
    print("="*60)
    print("🥗 SINGAPORE NUTRITION CHATBOT - WEB VERSION")
    print("="*60)
    print(f"📡 api key configured: {'yes' if USDA_KEY != 'DEMO_KEY' else 'no (using demo_key)'}")
    print(f"📁 data directory: {os.path.abspath('data/')}")
    print(f"💾 chat history: {os.path.abspath(FILES['chat_history'])}")
    print("\nstarting flask server...")
    print("open browser: http://127.0.0.1:5000")
    print("="*60)
    
    app.run(debug=True, host='127.0.0.1', port=5000)
