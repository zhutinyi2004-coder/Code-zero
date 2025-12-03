# singapore nutrition chatbot

yo so this is a chatbot that helps with singapore food nutrition stuff. asks for your name and remembers it which is pretty cool.

## what it does

- asks for your name when you say hi
- tells you nutrition info for local foods like chicken rice, laksa, etc
- gives health tips for diabetes, blood pressure, cholesterol
- busts diet myths like "are carbs bad"
- suggests healthy food swaps
- typing animation makes it look alive
- has quick buttons for common stuff

basically it's personalized and actually useful for singaporean context.

## how to run

super simple:

```bash
# install stuff
pip install flask requests

# run it
python app.py

# open browser
http://127.0.0.1:5000
```

that's it. should see the purple gradient chatbot.

## files in here

- `app.py` - backend that does all the work
- `frontend.html` - the webpage you see
- `script.js` - makes buttons work and stuff
- `style.css` - makes it look good (purple gradient)
- `config.json` - settings
- `sg_foods.txt` - 30 local foods with nutrition data
- `myths.txt` - diet myths to bust
- `healthy_swaps.txt` - healthier alternatives

## how to use

1. open the chatbot
2. click "say hi" or type hi
3. bot asks for your name
4. tell it your name
5. start asking about food

examples:
- "chicken rice nutrition"
- "are carbs bad?"
- "diabetes tips"
- "healthy swaps"

## features

**personalization**
- remembers your name
- uses it in responses
- different greetings each time

**singapore specific**
- 30 local foods in database
- hpb guidelines for health conditions
- hawker center tips
- local context

**smooth ux**
- typing animation
- quick action buttons
- smooth animations
- dark mode toggle
- clear chat that actually works

**health advice**
- diabetes management with target numbers
- blood pressure tips with sodium limits
- cholesterol advice with ldl targets
- specific actionable tips

## the 30 foods

chicken rice, nasi lemak, char kway teow, laksa, hokkien mee, bak chor mee, nasi goreng, roti prata, yong tau foo, chilli crab, satay, mee goreng, fish soup, carrot cake, economic rice, oyster omelette, wonton mee, popiah, rojak, kaya toast, bak kut teh, mee siam, prawn noodles, murtabak, chicken curry, tau huay, ice kacang, bee hoon, fried rice, lor mee

all with complete nutrition: calories, protein, carbs, fat, sodium, fiber, sugar.

## troubleshooting

**"no module named flask"**
run: `pip install flask requests`

**port 5000 already in use**
change port in app.py line 522 to 5001 or something

**chatbot looks ugly (no css)**
make sure style.css is in same folder as app.py

**foods not found**
check sg_foods.txt is there with all 30 foods

**still getting errors**
open browser console (f12) and check what it says

## tech stack

- python + flask for backend
- vanilla js for frontend (no frameworks)
- text files for data (easy to edit)
- no database needed
- runs locally

## for hackathon judges

show them:
1. the personalization (asks for name)
2. 30 singapore foods
3. health tips with actual hpb numbers
4. typing animation
5. quick buttons
6. dark mode
7. singapore context

emphasize it's not just generic nutrition bot - it's specifically for singapore with local foods and hpb guidelines.

## code quality

- clean code structure
- proper error handling
- comments in lowercase style
- no crashes on bad input
- validates everything
- production ready

## future improvements

could add:
- meal planning
- calorie tracking
- recipe suggestions
- more health conditions
- exercise tips
- food photos

but current version is solid for demo.

## notes

- data is stored in text files (json lines format)
- chat history saved to chat_history.txt
- everything in one folder
- easy to modify data files
- no complicated setup

## credits

made for hackathon. uses hpb singapore guidelines for health advice. food nutrition data from local sources.

---

basically just run it and it works. ask it stuff and it responds with your name. pretty straightforward.
