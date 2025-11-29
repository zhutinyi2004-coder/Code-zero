# Singapore Nutrition Chatbot - Simple Version

Quick first draft for hackathon. Stores data in text files.

## Setup

1. Install stuff:
```bash
pip install flask flask-cors requests --break-system-packages
```

2. Get API key:
- Go to https://api.data.gov/signup/
- Copy your key
- key:2dPV0Hytk8xBTGn88XumjCxgp7tN8yrUC6KiQxAX
- Replace DEMO_KEY in chatbot_v1.py

3. Run it:
```bash
python3 chatbot_v1.py
```

4. Test it:
```bash
python3 test_simple.py
```

## How it works

- Stores Singapore food data in `sg_foods.txt`
- Stores diet myths in `myths.txt`
- Saves chat history to `chat_history.txt`
- Calls USDA API if local food not found
- Returns nutrition info based on HPB guidelines

## Files created automatically

- `sg_foods.txt` - local food database (chicken rice, nasi lemak, laksa)
- `myths.txt` - diet myths database
- `chat_history.txt` - all chat messages

## API Usage

```bash
# Chat
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "nutrition for chicken rice", "user_id": "user123"}'

# Get history
curl http://localhost:5000/history
```

## Adding more foods

Just edit `sg_foods.txt` and add a new line:
```json
{"name": "mee goreng", "calories": 663, "protein": 18, "carbs": 75, "fat": 32, "sodium": 1200}
```

## Adding more myths

Edit `myths.txt` and add:
```json
{"keywords": ["eggs bad", "eggs cholesterol"], "myth": "Eggs are bad", "truth": "Eggs are fine in moderation", "tip": "1 egg per day is ok"}
```

## TODO for later
- Add proper database instead of text files
- Add user profiles
- More singapore foods
- Better error handling
- Frontend UI

## Singapore HPB Guidelines Used

Diabetes:
- Fasting glucose < 6.0 mmol/L
- Limit sugar intake
- More fiber

Blood Pressure:
- Sodium < 2000mg/day
- Ask for less salt
- Avoid processed foods

Cholesterol:
- Choose grilled over fried
- Use olive oil
- Eat fatty fish

Source: HPB.gov.sg
