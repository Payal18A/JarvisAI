from flask import Flask, render_template, request, jsonify
import os
import webbrowser
import openai
import datetime
import pyttsx3
import requests
import wikipedia
import json
import random
import pyautogui 
import subprocess
import threading
from config import apikey
from rapidfuzz import fuzz

# Initialize Flask app
app = Flask(__name__)

# Initialize OpenAI API Key
openai.api_key = apikey

# Initialize Text-to-Speech Engine (server-side)
engine = pyttsx3.init()

def fuzzy_in(query, keyword, threshold=70):
    """
    Returns True if the token-set fuzzy similarity ratio between the query and the keyword
    is above the threshold.
    """
    return fuzz.token_set_ratio(query.lower(), keyword.lower()) >= threshold

def search_google(query):
    """Opens Google search in the browser."""
    try:
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(search_url)
        return "I've opened a Google search for you."
    except Exception as e:
        return "Error opening search results."

def basic_response(query):
    """Provides general conversation responses for non-command queries."""
    query = query.strip().lower()

    # Greetings and salutations
    greetings = ["hi", "hello", "hey", "hii", "greetings", "good morning", "good afternoon", "good evening"]
    if any(greet in query for greet in greetings):
        return random.choice([
            "Hello there! How can I assist you today?", 
            "Hey! What can I do for you?",
            "Hi! How can I help?"
        ])

    # Jarvis girlfriend inquiries
    gf_inquiries = ["have you any girlfriend", "jarvis have you girlfriend", "jarvis girlfriend"]
    if any(greet in query for greet in gf_inquiries):
        return random.choice([
            "No, I am single. Having a girlfriend causes many problems; loyalty is hard to come by.",
            "Sorry, I'm single. I have no girlfriend."
        ])
    
    # MMDU UNIVERSITY
    mmdu_inquiries = ["mmdu university", "mmu", "mmec"]
    if any(greet in query for greet in mmdu_inquiries):
        return random.choice([
            "This university is situated at Mullana, Ambala, Haryana.", 
            "This is an open deemed-to-be university."
        ])

    # Inquiries about well-being
    if "how are you" in query or "how's it going" in query:
        return random.choice([
            "I'm doing great! How about you?", 
            "I'm fine, thanks for asking! How are you?", 
            "Feeling smart and ready to help!"
        ])

    # Casual conversation starters
    if "what's up" in query or "what are you doing" in query:
        return random.choice([
            "Not much, just here to assist you!", 
            "Just thinking about artificial intelligence! What about you?",
            "Helping people like you. What can I do for you today?"
        ])

    # Questions about identity
    if "what is your name" in query or "who are you" in query:
        return "I'm Jarvis, your AI assistant. Here to make your life easier!"

    # Gratitude responses
    if "thank you" in query or "thanks" in query:
        return random.choice([
            "You're welcome! Anything else I can do for you?", 
            "Glad to help!", 
            "Always here to assist you!"
        ])

    # Farewell responses
    if "bye" in query or "goodbye" in query or "see you" in query:
        return random.choice([
            "Goodbye! Have a great day!", 
            "See you later! Take care!", 
            "Bye! Let me know if you need anything else."
        ])

    # LOVE responses
    if "love you" in query or "love" in query or "heyy babe" in query:
        return random.choice([
            "Love you too! How can I help you?", 
            "Heyy, I love you too!", 
            "Do you really love me? I'm just an AI, not human!"
        ])

    # Questions about abilities
    if "what can you do" in query or "how can you help" in query:
        return ("I can help you with a variety of tasks such as web searches, "
                "providing weather updates, setting reminders, answering questions, "
                "telling jokes, opening applications like ChatGPT, MS Word, Notepad, "
                "system settings, file manager, taking screenshots, and more! Just ask me anything.")

    # Requests for jokes or fun facts
    if "tell me a joke" in query or "make me laugh" in query:
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "What do you get when you cross a snowman and a vampire? Frostbite!",
            "Parallel lines have so much in common. It's a shame they'll never meet!"
        ]
        return random.choice(jokes)

    if "tell me a fun fact" in query or "give me a random fact" in query:
        facts = [
            "Did you know that honey never spoils? Archaeologists found pots of honey in ancient Egyptian tombs that were over 3000 years old and still edible!",
            "The Eiffel Tower can grow more than six inches in hot weather!",
            "Bananas are berries, but strawberries aren't!"
        ]
        return random.choice(facts)

    # Inquiries about creation or origin
    if "who made you" in query or "created you" in query:
        return "I was created by my developer, Mr. Ankit Raj, to assist you with daily tasks and information!"

    # Questions about weather (non-command version)
    if "what's the weather" in query or "how's the weather" in query:
        return "I can check the weather for you! Just ask me 'what's the weather in [city]' and I'll provide the details."

    # Directions
    if "how do i get to" in query or "directions to" in query:
        return "You can use Google Maps to find directions. Try saying 'open Google Maps and search for [destination]'."

    # Questions about news
    if "what's the latest news" in query or "tell me the news" in query:
        return "I can fetch news updates for you. Just say 'search Google for latest news'."

    # Math calculations
    if any(x in query for x in ["calculate", "solve", "math"]):
        return "I can help with basic math! Try asking me something like 'what is 25 plus 7?'"

    # If nothing matches, return None so we can fallback to AI chat.
    return None

def process_command(query):
    """Process user commands."""
    if query == "":
        return "I didn't hear anything. Could you please repeat?"

    # Exit Command (not relevant for web interface)
    if query in ["quit", "exit"]:
        return "To close this window, just close your browser tab."

    # ----- Process specific commands first -----

    # "Open ChatGPT" Command.
    if fuzzy_in(query, "open chatgpt"):
        webbrowser.open("https://chat.openai.com")
        return "Opening ChatGPT in a new tab."

    # "Open Wikipedia" Command.
    if fuzzy_in(query, "wikipedia"):
        webbrowser.open("https://www.wikipedia.org/")
        return "Opening Wikipedia in a new tab."

    # "Open YouTube" Command.
    if fuzzy_in(query, "open youtube"):
        if "search" in query:
            search_query = query.split("search", 1)[1].strip()
            youtube_search_url = "https://www.youtube.com/results?search_query=" + search_query.replace(" ", "+")
            webbrowser.open(youtube_search_url)
            return f"Opening YouTube and searching for {search_query}"
        else:
            webbrowser.open("https://www.youtube.com")
            return "Opening YouTube in a new tab."

    # "Open Google" Command.
    if "google" in query and "open" in query and "search" in query:
        search_query = query.split("search", 1)[1].strip()
        google_search_url = "https://www.google.com/search?q=" + search_query.replace(" ", "+")
        webbrowser.open(google_search_url)
        return f"Opening Google and searching for {search_query}"

    # "Search Google for ..." Command.
    if fuzzy_in(query, "search google for"):
        search_query = query.lower().replace("search google for", "").strip()
        result = search_google(search_query)
        return result

    # "Time" Command.
    if "time" in query:
        current_time = datetime.datetime.now().strftime("%H:%M")
        return f"The time is {current_time}"

    # "Date" Command.
    if "date" in query or "today's date" in query:
        current_date = datetime.datetime.now().strftime("%B %d, %Y")
        return f"Today's date is {current_date}"

    # --- Additional Commands ---

    # "Open MS Word" Command.
    if fuzzy_in(query, "open ms word") or fuzzy_in(query, "open word"):
        try:
            # Adjust the path as needed for your system.
            ms_word_path = r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE"
            os.startfile(ms_word_path)
            return "Opening Microsoft Word."
        except Exception as e:
            return "I could not open MS Word. Please check if the path is correct."

    # "Open Notepad" Command.
    if fuzzy_in(query, "open notepad"):
        try:
            os.startfile("notepad.exe")
            return "Opening Notepad."
        except Exception as e:
            return "I could not open Notepad."

    # "Open System Settings" Command.
    if fuzzy_in(query, "open system settings") or fuzzy_in(query, "open settings"):
        try:
            subprocess.Popen("start ms-settings:", shell=True)
            return "Opening System Settings."
        except Exception as e:
            return "I could not open System Settings."

    # "Open File Manager" Command.
    if fuzzy_in(query, "open file manager") or fuzzy_in(query, "open explorer"):
        try:
            os.startfile("explorer")
            return "Opening File Manager."
        except Exception as e:
            return "I could not open the File Manager."

    # "Take Screenshot" Command.
    if fuzzy_in(query, "take screenshot") or fuzzy_in(query, "screenshot"):
        try:
            screenshot = pyautogui.screenshot()
            # Save screenshot with a timestamp.
            filename = f"static/screenshots/screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            
            # Ensure directory exists
            os.makedirs("static/screenshots", exist_ok=True)
            
            screenshot.save(filename)
            return f"Screenshot taken and saved. <a href='/{filename}' target='_blank'>View screenshot</a>"
        except Exception as e:
            return f"I could not take a screenshot. Error: {e}"

    # ----- Fallback to basic_response -----
    response = basic_response(query)
    if response is not None:
        return response
    else:
        return "I'm not sure how to respond to that. Can you ask something else?"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/query', methods=['POST'])
def query():
    data = request.get_json()
    user_query = data.get('query', '')
    
    if not user_query:
        return jsonify({'response': 'I didn\'t receive any input. Please try again.'})
    
    # Process the command and get response
    response = process_command(user_query.lower())
    
    # If this is a browser-based request, we'll let the browser handle TTS
    return jsonify({'response': response})

# Optional function to speak text on the server-side (if needed)
def speak(text):
    """Converts text to speech on the server."""
    engine.say(text)
    engine.runAndWait()

if __name__ == '__main__':
    # Create a directory for screenshots if it doesn't exist
    os.makedirs('static/screenshots', exist_ok=True)
    
    # Open browser automatically (optional)
    def open_browser():
        webbrowser.open('http://127.0.0.1:5000/')
    
    threading.Timer(1.0, open_browser).start()
    
    # Run the Flask app
    app.run(debug=True) 