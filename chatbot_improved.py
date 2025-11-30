"""
Singapore Nutrition Chatbot
All settings in config.json, all data in text files
Improved version with better comment handling and UTF-8 support
"""

import requests
import json
import os
from datetime import datetime

# Load config file
def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

config = load_config()

# Get API settings from config
USDA_KEY = config['api']['usda_key']
USDA_URL = config['api']['usda_url']

# Get file paths from config
FILES = config['files']
HPB_GUIDELINES = config['hpb_guidelines']

# Make sure data directory exists
os.makedirs('data', exist_ok=True)

# Save to text file with UTF-8 encoding
def save_to_file(data, filename):
    """Save data as JSON line to text file"""
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False) + '\n')

# Read from text file with improved comment handling
def read_from_file(filename):
    """Read JSON lines from text file, properly handling comments and errors"""
    try:
        # Create file if it doesn't exist
        if not os.path.exists(filename):
            return []
        
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            data = []
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                
                # Skip empty lines and comment lines (starting with #)
                if not line or line.startswith('#'):
                    continue
                
                try:
                    # Try to parse as JSON
                    item = json.loads(line)
                    data.append(item)
                except json.JSONDecodeError as e:
                    # Print warning but continue processing
                    print(f"Warning: Line {line_num} in {filename} has invalid JSON - skipping")
                    continue
            
            return data
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"Error reading file {filename}: {e}")
        return []

# Load Singapore foods from text file
def load_sg_foods():
    """Load local food database"""
    foods = {}
    data = read_from_file(FILES['sg_foods'])
    for item in data:
        # Store with lowercase key for case-insensitive matching
        foods[item['name'].lower()] = item
    return foods

# Search local food database
def search_local_food(query):
    """Search for food in local database"""
    foods = load_sg_foods()
    query = query.lower()
    
    # Direct match first
    if query in foods:
        return foods[query]
    
    # Partial match
    for name, info in foods.items():
        if query in name or name in query:
            return info
    
    return None

# Call USDA API with better error handling
def search_usda(query):
    """Search USDA FoodData Central API"""
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
                
                # Extract nutrients
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
        print(f"API request error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected API error: {e}")
        return None

# Load myths from text file
def load_myths():
    """Load diet myths database"""
    return read_from_file(FILES['myths'])

# Check if message contains a myth
def check_myth(message):
    """Check if user message relates to a diet myth"""
    myths = load_myths()
    msg = message.lower()
    
    for myth in myths:
        for keyword in myth.get('keywords', []):
            if keyword.lower() in msg:
                return myth
    return None

# Load healthy swaps from text file
def load_swaps():
    """Load healthy food swaps database"""
    return read_from_file(FILES['swaps'])

# Get swaps based on condition
def get_swaps(condition=None, limit=None):
    """Get food swaps, optionally filtered by health condition"""
    all_swaps = load_swaps()
    
    if condition:
        filtered = [s for s in all_swaps if s.get('category') == condition]
    else:
        filtered = all_swaps
    
    if limit:
        return filtered[:limit]
    return filtered

# Save chat to history in readable text format
def save_chat_history(user_message, bot_response):
    """Save conversation to history in readable text format"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(FILES['chat_history'], 'a', encoding='utf-8') as f:
        f.write(f"\n{'='*60}\n")
        f.write(f"[{timestamp}]\n")
        f.write(f"User: {user_message}\n")
        f.write(f"Bot: {bot_response}\n")

# Main chat function
def chat(message):
    """Process user message and return response"""
    response_lines = []
    
    # Check for myths first
    myth = check_myth(message)
    if myth:
        response = "\n🚫 Myth Busted!\n"
        response += f"Myth: {myth['myth']}\n"
        response += f"✅ Truth: {myth['truth']}\n"
        response += f"💡 Tip: {myth['tip']}"
        print(response)
        save_chat_history(message, response)
        return
    
    # Check for food nutrition queries
    food_keywords = ['nutrition', 'calories', 'healthy', 'info', 'nutrient', 'nutritional']
    if any(word in message.lower() for word in food_keywords):
        # Search local first
        food = search_local_food(message)
        
        # Try API if not found locally
        if not food:
            print("\n🔍 Searching USDA database...")
            food = search_usda(message)
        
        if food:
            response = f"\n🍽️  {food.get('name', 'Food').upper()}\n"
            response += "─" * 40 + "\n"
            response += f"Calories: {food.get('calories', 'N/A')} kcal\n"
            response += f"Protein:  {food.get('protein', 'N/A')}g\n"
            response += f"Carbs:    {food.get('carbs', 'N/A')}g\n"
            response += f"Fat:      {food.get('fat', 'N/A')}g\n"
            response += f"Sodium:   {food.get('sodium', 'N/A')}mg\n"
            response += f"Fiber:    {food.get('fiber', 'N/A')}g\n"
            response += f"Sugar:    {food.get('sugar', 'N/A')}g\n"
            
            # Warnings based on HPB guidelines
            if food.get('sodium', 0) > 600:
                response += f"\n⚠️  High sodium! HPB recommends {HPB_GUIDELINES['blood_pressure']['sodium_limit']}"
            if food.get('sugar', 0) > 10:
                response += "\n⚠️  High sugar content"
            
            print(response)
            save_chat_history(message, response)
            return
        else:
            response = "\n❌ Couldn't find that food. Try: chicken rice, nasi lemak, laksa"
            print(response)
            save_chat_history(message, response)
            return
    
    # Diabetes management
    if 'diabetes' in message.lower():
        response = "\n💉 Diabetes Management (HPB Singapore):\n"
        response += f"• Fasting glucose target: {HPB_GUIDELINES['diabetes']['fasting_glucose_normal']}\n"
        response += f"• Sugar limit: {HPB_GUIDELINES['diabetes']['sugar_limit']}\n"
        response += f"• Fiber: {HPB_GUIDELINES['diabetes']['fiber_recommendation']}\n"
        response += "• Good SG foods: Fish soup, yong tau foo, economic rice (more veg)\n"
        response += "• Avoid: Sugary drinks, fried noodles"
        
        # Show relevant swaps
        swaps = get_swaps('diabetes', limit=3)
        if swaps:
            response += "\n\n🔄 Healthy Swaps:\n"
            for swap in swaps:
                response += f"  ❌ {swap['unhealthy']} → ✅ {swap['healthy']}\n"
                response += f"     ({swap['benefit']})\n"
        
        print(response)
        save_chat_history(message, response)
        return
    
    # Blood pressure management
    if 'blood pressure' in message.lower() or 'hypertension' in message.lower():
        response = "\n❤️  Blood Pressure Management (HPB Singapore):\n"
        response += f"• Normal BP: {HPB_GUIDELINES['blood_pressure']['normal']}\n"
        response += f"• Sodium limit: {HPB_GUIDELINES['blood_pressure']['sodium_limit']}\n"
        response += "• Ask for 'less salt' at hawker centers\n"
        response += "• Avoid: Instant noodles, processed meats"
        
        # Show relevant swaps
        swaps = get_swaps('blood_pressure', limit=3)
        if swaps:
            response += "\n\n🔄 Healthy Swaps:\n"
            for swap in swaps:
                response += f"  ❌ {swap['unhealthy']} → ✅ {swap['healthy']}\n"
                response += f"     ({swap['benefit']})\n"
        
        print(response)
        save_chat_history(message, response)
        return
    
    # Cholesterol management
    if 'cholesterol' in message.lower():
        response = "\n🩺 Cholesterol Management (HPB Singapore):\n"
        response += f"• LDL target: {HPB_GUIDELINES['cholesterol']['ldl_target']}\n"
        response += "• Choose grilled/steamed over fried\n"
        response += "• Use olive oil or canola oil\n"
        response += "• Eat fatty fish 2x per week"
        
        # Show relevant swaps
        swaps = get_swaps('cholesterol', limit=3)
        if swaps:
            response += "\n\n🔄 Healthy Swaps:\n"
            for swap in swaps:
                response += f"  ❌ {swap['unhealthy']} → ✅ {swap['healthy']}\n"
                response += f"     ({swap['benefit']})\n"
        
        print(response)
        save_chat_history(message, response)
        return
    
    # Show healthy swaps
    if 'swap' in message.lower() or 'alternative' in message.lower():
        swaps = load_swaps()
        response = "\n🔄 Healthy Food Swaps:\n"
        for swap in swaps[:8]:
            response += f"\n❌ {swap['unhealthy']} → ✅ {swap['healthy']}\n"
            response += f"   💡 {swap['benefit']}"
        
        print(response)
        save_chat_history(message, response)
        return
    
    # Default help message
    response = "\n👋 Hi! I can help with:\n"
    response += "1. Food nutrition (try: 'nutrition for chicken rice')\n"
    response += "2. Diabetes management\n"
    response += "3. Blood pressure advice\n"
    response += "4. Cholesterol tips\n"
    response += "5. Bust diet myths (try: 'are carbs bad?')\n"
    response += "6. Healthy food swaps\n"
    response += "\n✅ Based on Singapore HPB guidelines"
    
    print(response)
    save_chat_history(message, response)

# Main program
def main():
    print("=" * 60)
    print("🥗 SINGAPORE NUTRITION CHATBOT")
    print("Based on HPB Guidelines")
    print("=" * 60)
    print(f"\n📡 Using API: {USDA_URL}")
    print(f"📁 Data files: {os.path.abspath('data/')}/")
    print(f"💾 Chat history: {os.path.abspath(FILES['chat_history'])}")
    print("\nType 'quit' to exit\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\n👋 Bye! Stay healthy!")
                break
            
            if not user_input:
                continue
            
            chat(user_input)
            print()
        
        except KeyboardInterrupt:
            print("\n\n👋 Bye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            continue

if __name__ == '__main__':
    main()
