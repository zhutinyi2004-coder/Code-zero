"""
Quick test for the chatbot
Just run this to see if it works
"""

import requests

url = "http://localhost:5000/chat"

# test 1: basic greeting
print("Test 1: Greeting")
r = requests.post(url, json={"message": "hello"})
print(r.json()['response'])
print("\n" + "="*50 + "\n")

# test 2: singapore food
print("Test 2: Chicken Rice")
r = requests.post(url, json={"message": "whats the nutrition for chicken rice"})
print(r.json()['response'])
print("\n" + "="*50 + "\n")

# test 3: diet myth
print("Test 3: Carbs Myth")
r = requests.post(url, json={"message": "are carbs bad for me"})
print(r.json()['response'])
print("\n" + "="*50 + "\n")

# test 4: diabetes advice
print("Test 4: Diabetes")
r = requests.post(url, json={"message": "how to manage diabetes"})
print(r.json()['response'])
print("\n" + "="*50 + "\n")

print("All tests done!")
