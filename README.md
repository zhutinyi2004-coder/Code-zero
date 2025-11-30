#  Singapore Nutrition Chatbot - Web Version

clean web interface with singapore food nutrition info based on hpb guidelines. all data stored in text files for easy editing.

#features

-  local singapore food database (10 popular dishes)
-  health management tips (diabetes, blood pressure, cholesterol)
-  diet myth busting (6 common myths)
-  healthy food swaps (12 alternatives)
-  usda api integration for international foods
-  all data in text files (easy to edit)
-  chat history saved in readable text format
-  material-ui styled interface

## quick start

### 1. install dependencies
```bash
pip install -r requirements.txt
```

### 2. get api key (optional)
1. visit: https://api.data.gov/signup/
2. enter your email
3. copy the api key
4. open `config.json`
5. replace `"DEMO_KEY"` with your actual key

### 3. start the server
```bash
python app.py
```

### 4. open browser
go to: http://127.0.0.1:5000

## 📁 file structure

```
sg-nutrition-chatbot/
├── app.py                  # flask backend (run this!)
├── index.html              # web frontend
├── chatbot_improved.py     # cli version (optional)
├── config.json             # settings & api key
├── requirements.txt        # python dependencies
├── data/
│   ├── sg_foods.txt       # singapore food database
│   ├── myths.txt          # diet myths
│   ├── healthy_swaps.txt  # food alternatives
│   └── chat_history.txt   # auto-saved conversations
└── README.md              # this file
```

## 💬 how to use

### web interface
1. start flask: `python app.py`
2. open browser: http://127.0.0.1:5000
3. type your questions
4. press enter or click send

### command line (optional)
```bash
python chatbot_improved.py
```

## editing data files

all data in `data/` folder. each line = one json object. lines starting with `#` = comments.

### add food (data/sg_foods.txt)
```json
{"name": "hokkien mee", "calories": 680, "protein": 22, "carbs": 70, "fat": 35, "sodium": 1400, "fiber": 3, "sugar": 4}
```

### add myth (data/myths.txt)
```json
{"keywords": ["keto", "ketogenic"], "myth": "keto is for everyone", "truth": "works for some, not all", "tip": "consult a doctor first"}
```

### add swap (data/healthy_swaps.txt)
```json
{"category": "general", "unhealthy": "fried rice", "healthy": "brown rice with stir-fry", "benefit": "more fiber, less oil"}
```

##  chat history format

saved in `data/chat_history.txt` in readable format:

```
============================================================
[2024-11-30 14:30:15]
User: nutrition for chicken rice
Bot:  CHICKEN RICE
──────────────────────────────
Calories: 607 kcal
Protein: 25g
...
```

## key improvements

**better comment handling** - lines starting with `#` properly skipped
**utf-8 encoding** - supports special characters
**readable history** - chat logs in human-readable format
**error handling** - graceful handling of invalid json
**web interface** - material-ui styled chat
 **dual mode** - both web and cli versions

##  configuration

edit `config.json` to change settings:

```json
{
  "api": {
    "usda_key": "YOUR_KEY_HERE",
    "usda_url": "https://api.nal.usda.gov/fdc/v1/foods/search"
  },
  "files": {
    "sg_foods": "data/sg_foods.txt",
    "myths": "data/myths.txt",
    "chat_history": "data/chat_history.txt",
    "swaps": "data/healthy_swaps.txt"
  },
  "hpb_guidelines": {
    "diabetes": {
      "fasting_glucose_normal": "≤ 6.0 mmol/L",
      "sugar_limit": "< 10% of daily calories",
      "fiber_recommendation": "25-30g per day"
    }
  }
}
```

## 🐛 troubleshooting

**"modulenotfounderror: no module named 'flask'"**
```bash
pip install -r requirements.txt
```

**"address already in use"**
- another app using port 5000
- change port in app.py: `app.run(port=5001)`

**"warning: line x has invalid json"**
- check that line for syntax errors
- each line must be valid json
- no trailing commas

**frontend shows error**
- make sure flask is running (python app.py)
- check browser console for errors
- verify backend url is http://127.0.0.1:5000

## 🎓 for hackathon

### demo points
1. show the web interface
2. demo nutrition lookup with local food
3. bust a popular myth
4. show health management tips
5. display food swaps
6. open data files - show easy to edit
7. open chat history - show readable format

### key selling points
- **singapore context** - built for singaporeans
- **evidence-based** - hpb guidelines, not fads
- **easy to modify** - all data in text files
- **dual interface** - web and command-line
- **readable logs** - chat history in text format
- **production-ready** - proper error handling

##  data sources

- **singapore hpb**: https://www.hpb.gov.sg/
- **healthhub**: https://www.healthhub.sg/
- **usda fooddata**: https://fdc.nal.usda.gov/

---

