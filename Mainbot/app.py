"""
singapore nutrition chatbot - flask backend
personalized nutrition assistant with singapore food database
"""

from flask import Flask, request, jsonify, send_from_directory, session
import requests
import json
import os
from datetime import datetime
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # session security

# cors headers for cross-origin requests
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# load config from json
def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

config = load_config()

# api settings
USDA_KEY = config['api']['usda_key']
USDA_URL = config['api']['usda_url']

# file paths
FILES = config['files']
HPB_GUIDELINES = config['hpb_guidelines']

# store user data in memory (in-memory for simplicity)
user_data = {}

# helper function to safely update user count
def update_user_count(user_id, count):
    """safely update conversation count"""
    if user_id not in user_data:
        user_data[user_id] = {'name': '', 'count': 0, 'awaiting_name': False}
    user_data[user_id]['count'] = count

# save to file
def save_to_file(data, filename):
    """save data as json line to text file"""
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False) + '\n')

# read from file
def read_from_file(filename):
    """read json lines from text file, skip comments and handle errors"""
    try:
        # make file if not there
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

# check if asking for name
def is_asking_name(message):
    """check if user is providing their name"""
    greetings = ['hi', 'hello', 'hey', 'yo', 'sup', 'greetings', 'good morning', 'good afternoon', 'good evening']
    msg = message.lower().strip()
    
    # check for direct greetings
    for greeting in greetings:
        if msg == greeting or msg.startswith(greeting + ' '):
            return 'greeting'
    
    # check if looks like a name (short, no special keywords)
    food_keywords = ['nutrition', 'calories', 'healthy', 'food', 'eat', 'diet', 'diabetes', 'pressure', 'cholesterol']
    if len(msg.split()) <= 3 and not any(kw in msg for kw in food_keywords):
        return 'possible_name'
    
    return None

# main chat processing function with personalization
def process_chat(message, user_id):
    """process user message and return response with personalization"""
    
    # get user data
    user_info = user_data.get(user_id, {})
    user_name = user_info.get('name', '')
    conversation_count = user_info.get('count', 0)
    
    # increment conversation count
    conversation_count += 1
    
    # check if greeting or name
    name_check = is_asking_name(message)
    
    if name_check == 'greeting' and not user_name:
        # first time greeting - ask for name
        response = "Hello there! Welcome to Singapore Nutrition Assistant!\n\n"
        response += "I'm here to help you with nutrition info about local Singaporean foods.\n\n"
        response += "What's your name? I'd love to know who I'm chatting with!"
        
        # store temporary state
        user_data[user_id] = {
            'name': '',
            'count': conversation_count,
            'awaiting_name': True
        }
        
        return response
    
    elif user_info.get('awaiting_name') and name_check == 'possible_name':
        # user provided their name
        name = message.strip().title()
        user_data[user_id] = {
            'name': name,
            'count': conversation_count,
            'awaiting_name': False
        }
        
        response = f"Nice to meet you, {name}!\n\n"
        response += "I can help you with:\n\n"
        response += "1. Nutrition info for local dishes (try: 'chicken rice nutrition')\n"
        response += "2. Bust diet myths (try: 'are carbs bad?')\n"
        response += "3. Health tips for diabetes, blood pressure, cholesterol\n"
        response += "4. Healthy food swaps\n\n"
        response += "What would you like to know?"
        
        return response
    
    elif name_check == 'greeting' and user_name:
        # returning user greeting
        greetings_list = [
            f"Hey {user_name}! Good to see you again!",
            f"Welcome back, {user_name}!",
            f"Hi {user_name}! Ready for some nutrition talk?",
            f"Hello {user_name}! What can I help you with today?"
        ]
        response = greetings_list[conversation_count % len(greetings_list)]
        response += "\n\nWhat would you like to know about today?"
        
        update_user_count(user_id, conversation_count)
        return response
    
    # add personalization prefix if we know the name
    name_prefix = f"{user_name}, " if user_name and conversation_count > 2 else ""
    
    # check for myths first
    myth = check_myth(message)
    if myth:
        response = f"{name_prefix}great question! Let me bust that myth for you:\n\n"
        response += f"MYTH: {myth['myth']}\n\n"
        response += f"TRUTH: {myth['truth']}\n\n"
        response += f"TIP: {myth['tip']}"
        
        if user_name:
            response += f"\n\nAnything else you'd like to know, {user_name}?"
        
        update_user_count(user_id, conversation_count)
        return response
    
    # check for food nutrition queries
    food_keywords = ['nutrition', 'calories', 'healthy', 'info', 'nutrient', 'nutritional', 'how many']
    if any(word in message.lower() for word in food_keywords):
        # search local first
        food = search_local_food(message)
        
        # try api if not found locally
        if not food:
            food = search_usda(message)
        
        if food:
            response = f"{name_prefix}here's the nutrition info for {food.get('name', 'this food')}:\n\n"
            response += f"Calories: {food.get('calories', 'N/A')} kcal\n"
            response += f"Protein: {food.get('protein', 'N/A')}g\n"
            response += f"Carbs: {food.get('carbs', 'N/A')}g\n"
            response += f"Fat: {food.get('fat', 'N/A')}g\n"
            response += f"Sodium: {food.get('sodium', 'N/A')}mg\n"
            response += f"Fiber: {food.get('fiber', 'N/A')}g\n"
            response += f"Sugar: {food.get('sugar', 'N/A')}g\n"
            
            # warnings based on hpb guidelines
            if food.get('sodium', 0) > 600:
                response += f"\n\nWARNING: This is quite high in sodium! HPB recommends less than {HPB_GUIDELINES['blood_pressure']['sodium_limit']}"
            if food.get('sugar', 0) > 10:
                response += "\n\nWARNING: High sugar content - consume in moderation!"
            
            if user_name:
                response += f"\n\nWant to know about any other foods, {user_name}?"
            
            update_user_count(user_id, conversation_count)
            return response
        else:
            response = f"{name_prefix}hmm, I couldn't find that food in my database.\n\n"
            response += "Try asking about popular Singapore dishes like:\n"
            response += "- Chicken rice\n- Nasi lemak\n- Laksa\n- Char kway teow\n- Yong tau foo"
            
            update_user_count(user_id, conversation_count)
            return response
    
    # diabetes management
    if 'diabetes' in message.lower():
        response = f"{name_prefix}here are some diabetes management tips based on HPB guidelines:\n\n"
        response += f"TARGETS:\n"
        response += f"- Fasting glucose: {HPB_GUIDELINES['diabetes']['fasting_glucose_normal']}\n"
        response += f"- Sugar limit: {HPB_GUIDELINES['diabetes']['sugar_limit']}\n"
        response += f"- Daily fiber: {HPB_GUIDELINES['diabetes']['fiber_recommendation']}\n\n"
        response += "GOOD CHOICES:\n"
        response += "- Fish soup, yong tau foo (more veggies), economic rice\n\n"
        response += "AVOID:\n"
        response += "- Sugary drinks, fried noodles, white rice in large portions\n"
        
        # show relevant swaps
        swaps = get_swaps('diabetes', limit=3)
        if swaps:
            response += "\n\nHEALTHY SWAPS:\n"
            for swap in swaps:
                response += f"- {swap['unhealthy']} → {swap['healthy']}\n"
        
        if user_name:
            response += f"\n\nNeed more specific advice, {user_name}?"
        
        update_user_count(user_id, conversation_count)
        return response
    
    # blood pressure management
    if 'blood pressure' in message.lower() or 'hypertension' in message.lower() or 'bp' in message.lower():
        response = f"{name_prefix}here's how to manage blood pressure with food:\n\n"
        response += f"TARGET: {HPB_GUIDELINES['blood_pressure']['normal']}\n"
        response += f"SODIUM LIMIT: {HPB_GUIDELINES['blood_pressure']['sodium_limit']}\n\n"
        response += "TIPS:\n"
        response += "- Ask for 'less salt' or 'no MSG' at hawker centers\n"
        response += "- Avoid instant noodles and processed meats\n"
        response += "- Choose steamed over fried options\n"
        
        # show relevant swaps
        swaps = get_swaps('blood_pressure', limit=3)
        if swaps:
            response += "\n\nHEALTHY SWAPS:\n"
            for swap in swaps:
                response += f"- {swap['unhealthy']} → {swap['healthy']}\n"
        
        if user_name:
            response += f"\n\nWant more BP-friendly food tips, {user_name}?"
        
        update_user_count(user_id, conversation_count)
        return response
    
    # cholesterol management
    if 'cholesterol' in message.lower():
        response = f"{name_prefix}let's talk about managing cholesterol:\n\n"
        response += f"LDL TARGET: {HPB_GUIDELINES['cholesterol']['ldl_target']}\n\n"
        response += "TIPS:\n"
        response += "- Choose grilled/steamed over fried foods\n"
        response += "- Use olive oil or canola oil for cooking\n"
        response += "- Eat fatty fish (salmon, mackerel) 2x per week\n"
        response += "- Limit coconut milk curries\n"
        
        # show relevant swaps
        swaps = get_swaps('cholesterol', limit=3)
        if swaps:
            response += "\n\nHEALTHY SWAPS:\n"
            for swap in swaps:
                response += f"- {swap['unhealthy']} → {swap['healthy']}\n"
        
        if user_name:
            response += f"\n\nAny other questions about cholesterol, {user_name}?"
        
        update_user_count(user_id, conversation_count)
        return response
    
    # show healthy swaps
    if 'swap' in message.lower() or 'alternative' in message.lower() or 'replace' in message.lower():
        swaps = load_swaps()
        response = f"{name_prefix}here are some healthy food swaps you can make:\n\n"
        for i, swap in enumerate(swaps[:8], 1):
            response += f"{i}. {swap['unhealthy']} → {swap['healthy']}\n"
            response += f"   Why? {swap['benefit']}\n\n"
        
        if user_name:
            response += f"Try these out, {user_name}! Your body will thank you."
        
        update_user_count(user_id, conversation_count)
        return response
    
    # thank you response
    if 'thank' in message.lower() or 'thanks' in message.lower():
        responses = [
            f"You're welcome{', ' + user_name if user_name else ''}! Happy to help!",
            f"No problem{', ' + user_name if user_name else ''}! Eat healthy!",
            f"Anytime{', ' + user_name if user_name else ''}! Stay healthy!"
        ]
        update_user_count(user_id, conversation_count)
        return responses[conversation_count % len(responses)]
    
    # default help message
    response = f"{'Hey ' + user_name + '! ' if user_name else 'Hi there! '}"
    response += "I can help you with:\n\n"
    response += "1. Nutrition info (try: 'nutrition for chicken rice')\n"
    response += "2. Diet myths (try: 'are carbs bad?')\n"
    response += "3. Health conditions (diabetes, blood pressure, cholesterol)\n"
    response += "4. Healthy food swaps\n\n"
    response += "What interests you?"
    
    update_user_count(user_id, conversation_count)
    return response

# flask routes

@app.route('/')
def index():
    """serve the frontend html"""
    return send_from_directory('.', 'frontend.html')

@app.route('/style.css')
def serve_css():
    """serve the css file"""
    return send_from_directory('.', 'style.css')

@app.route('/script.js')
def serve_js():
    """serve the javascript file"""
    return send_from_directory('.', 'script.js')

@app.route('/chat', methods=['POST'])
def chat():
    """main chat endpoint with personalization"""
    try:
        # get request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'response': 'sorry, i didnt receive your message properly. please try again.',
                'status': 'error'
            }), 400
        
        user_message = data.get('message', '').strip()
        user_id = data.get('user_id', 'default_user')
        
        if not user_message:
            return jsonify({
                'response': 'please type a message first!',
                'status': 'error'
            }), 400
        
        # process the message with personalization
        bot_response = process_chat(user_message, user_id)
        
        # save to history
        try:
            save_chat_history(user_message, bot_response)
        except Exception as history_error:
            # dont fail if history save fails
            print(f"warning: could not save to history - {history_error}")
        
        return jsonify({
            'response': bot_response,
            'status': 'success'
        })
    
    except json.JSONDecodeError:
        return jsonify({
            'response': 'sorry, there was a problem understanding your message. please try again.',
            'status': 'error'
        }), 400
    
    except Exception as e:
        print(f"error in chat endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'response': 'oops! something went wrong on my end. please refresh and try again.',
            'status': 'error'
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
    print("SINGAPORE NUTRITION CHATBOT")
    print("="*60)
    # print(f"api key configured: {'yes' if USDA_KEY != 'DEMO_KEY' else 'no (using demo_key)'}")
    print(f"chat history: {os.path.abspath(FILES['chat_history'])}")
    print("\nstarting flask server...")
    print("open browser: http://127.0.0.1:5000")
    print("="*60)
    
    app.run(debug=True, host='127.0.0.1', port=5000)
