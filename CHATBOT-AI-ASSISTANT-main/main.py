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
from config import apikey  
from rapidfuzz import fuzz
import tkinter as tk
from tkinter import scrolledtext, ttk, PhotoImage
import threading
import time

# Initialize OpenAI API Key
openai.api_key = apikey

# Initialize Text-to-Speech Engine
engine = pyttsx3.init()

# Conversation history file path
HISTORY_FILE = os.path.join(os.path.dirname(__file__), 'conversation_history.json')

def load_conversation_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_conversation_history(history):
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=4)
    except Exception as e:
        print(f"Error saving conversation history: {e}")

# Initialize conversation history
conversation_history = load_conversation_history()

def speak(text):
    """Converts text to speech and prints it."""
    # Log assistant message
    conversation_history.append({"role": "assistant", "content": text})
    save_conversation_history(conversation_history)
    if gui_mode:
        display_assistant_message(text)
    else:
        print("Jarvis:", text)
    engine.say(text)
    engine.runAndWait()

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

def take_voice_command():
    """Takes voice input from the user and returns it as text."""
    import speech_recognition as sr
    r = sr.Recognizer()
    
    if gui_mode:
        status_label.config(text="Listening...")
        root.update()
    
    with sr.Microphone() as source:
        if not gui_mode:
            speak("Listening for your voice command...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
        try:
            if gui_mode:
                status_label.config(text="Recognizing...")
                root.update()
            else:
                speak("Recognizing your command...")
            query = r.recognize_google(audio, language="en-in")
            
            if gui_mode:
                display_user_message(query)
                status_label.config(text="Ready")
            else:
                print("User (voice):", query)
            # Log user message
            conversation_history.append({"role": "user", "content": query})
            save_conversation_history(conversation_history)
            return query.lower()
        except Exception as e:
            if gui_mode:
                status_label.config(text="Ready")
                speak("I didn't catch that. Please try again.")
            else:
                speak("I didn't catch that. Please try again.")
            return ""

def get_text_command():
    """Takes text input from the user."""
    query = input("Enter your message (or type 'exit' to quit): ")
    # Log user message
    conversation_history.append({"role": "user", "content": query})
    save_conversation_history(conversation_history)
    return query.lower()

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

def display_user_message(message):
    """Display user message in the chat window."""
    chat_display.config(state=tk.NORMAL)
    chat_display.insert(tk.END, "You: ", "user_tag")
    chat_display.insert(tk.END, message + "\n", "user_message")
    chat_display.config(state=tk.DISABLED)
    chat_display.see(tk.END)
    
def display_assistant_message(message):
    """Display assistant message in the chat window."""
    chat_display.config(state=tk.NORMAL)
    chat_display.insert(tk.END, "Jarvis: ", "jarvis_tag")
    chat_display.insert(tk.END, message + "\n", "jarvis_message")
    chat_display.config(state=tk.DISABLED)
    chat_display.see(tk.END)

def process_command(query):
    """Process user commands either from GUI or terminal."""
    if query == "":
        return

    # Exit Command.
    if query in ["quit", "exit"]:
        if gui_mode:
            speak("Goodbye Sir!")
            root.after(1000, root.destroy)
        else:
            speak("Goodbye Sir!")
        return False

    # ----- Process specific commands first -----

    # "Open ChatGPT" Command.
    if fuzzy_in(query, "open chatgpt"):
        speak("Opening ChatGPT in your browser.")
        webbrowser.open("https://chat.openai.com")
        return True

    # "Open WIKIPIDIA" Command.
    if fuzzy_in(query, "wikipedia"):
        speak("Opening Wikipedia.")
        webbrowser.open("https://www.wikipedia.org/")
        return True

    # "Open YouTube" Command.
    if fuzzy_in(query, "open youtube"):
        if "search" in query:
            search_query = query.split("search", 1)[1].strip()
            youtube_search_url = "https://www.youtube.com/results?search_query=" + search_query.replace(" ", "+")
            speak(f"Opening YouTube and searching for {search_query}")
            webbrowser.open(youtube_search_url)
        else:
            speak("Opening YouTube")
            webbrowser.open("https://www.youtube.com")
        return True

    # "Open Google" Command.
    if "google" in query and "open" in query and "search" in query:
        search_query = query.split("search", 1)[1].strip()
        google_search_url = "https://www.google.com/search?q=" + search_query.replace(" ", "+")
        speak(f"Opening Google and searching for {search_query}")
        webbrowser.open(google_search_url)
        return True

    # "Search Google for ..." Command.
    if fuzzy_in(query, "search google for"):
        search_query = query.lower().replace("search google for", "").strip()
        result = search_google(search_query)
        speak(result)
        return True

    # "Time" Command.
    if "time" in query:
        current_time = datetime.datetime.now().strftime("%H:%M")
        speak(f"The time is {current_time}")
        return True

    # "Date" Command.
    if "date" in query or "today's date" in query:
        current_date = datetime.datetime.now().strftime("%B %d, %Y")
        speak(f"Today's date is {current_date}")
        return True

    # --- Additional Commands ---

    # "Open MS Word" Command.
    if fuzzy_in(query, "open ms word") or fuzzy_in(query, "open word"):
        try:
            # Adjust the path as needed for your system.
            ms_word_path = r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE"
            os.startfile(ms_word_path)
            speak("Opening Microsoft Word.")
        except Exception as e:
            speak("I could not open MS Word. Please check if the path is correct.")
        return True

    # "Open Notepad" Command.
    if fuzzy_in(query, "open notepad"):
        try:
            os.startfile("notepad.exe")
            speak("Opening Notepad.")
        except Exception as e:
            speak("I could not open Notepad.")
        return True

    # "Open System Settings" Command.
    if fuzzy_in(query, "open system settings") or fuzzy_in(query, "open settings"):
        try:
            subprocess.Popen("start ms-settings:", shell=True)
            speak("Opening System Settings.")
        except Exception as e:
            speak("I could not open System Settings.")
        return True

    # "Open File Manager" Command.
    if fuzzy_in(query, "open file manager") or fuzzy_in(query, "open explorer"):
        try:
            os.startfile("explorer")
            speak("Opening File Manager.")
        except Exception as e:
            speak("I could not open the File Manager.")
        return True

    # "Take Screenshot" Command.
    if fuzzy_in(query, "take screenshot") or fuzzy_in(query, "screenshot"):
        try:
            screenshot = pyautogui.screenshot()
            # Save screenshot with a timestamp.
            filename = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            screenshot.save(filename)
            speak(f"Screenshot taken and saved as {filename}.")
            
            # Open the screenshot using the default image viewer.
            if os.name == "nt":  # Windows
                os.startfile(filename)
            elif os.name == "posix":  # macOS or Linux
                try:
                    subprocess.Popen(["open", filename])
                except Exception:
                    subprocess.Popen(["xdg-open", filename])
        except Exception as e:
            speak(f"I could not take a screenshot. Error: {e}")
        return True

    # ----- Fallback to basic_response or AI chat -----
    response = basic_response(query)
    if response is not None:
        speak(response)
    else:
        speak("I'm not sure how to respond to that. Can you ask something else?")
    
    return True

def submit_text():
    """Get text from entry field and process it."""
    query = user_input.get().strip()
    if query == "":
        return
    
    user_input.delete(0, tk.END)  # Clear the input field
    display_user_message(query)
    
    # Log user message
    conversation_history.append({"role": "user", "content": query})
    save_conversation_history(conversation_history)

    # Process command in a separate thread to prevent GUI freezing
    def process_in_thread():
        result = process_command(query.lower())
        if not result:  # Exit command was given
            root.after(1000, root.destroy)
    
    threading.Thread(target=process_in_thread).start()

def voice_command():
    """Trigger voice command input."""
    def listen_in_thread():
        query = take_voice_command()
        if query:
            process_command(query)
    
    threading.Thread(target=listen_in_thread).start()

def on_enter(event):
    """Handle Enter key press in the input field."""
    submit_text()

def start_gui():
    """Initialize and start the GUI."""
    global root, chat_display, user_input, status_label, gui_mode
    
    # Create the main window
    root = tk.Tk()
    root.title("Jarvis AI Assistant")
    root.geometry("800x600")
    root.configure(bg="#f0f0f0")
    
    # Set GUI mode
    gui_mode = True
    
    # Create a frame for the chat display
    chat_frame = tk.Frame(root, bg="#f0f0f0")
    chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Create a scrolled text widget for the chat display
    global chat_display
    chat_display = scrolledtext.ScrolledText(
        chat_frame, 
        wrap=tk.WORD, 
        width=80, 
        height=20,
        font=("Helvetica", 10),
        bg="#ffffff",
        relief=tk.FLAT
    )
    chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Configure text tags for styling
    chat_display.tag_configure("user_tag", foreground="#0066cc", font=("Helvetica", 10, "bold"))
    chat_display.tag_configure("user_message", foreground="#000000", font=("Helvetica", 10))
    chat_display.tag_configure("jarvis_tag", foreground="#009933", font=("Helvetica", 10, "bold"))
    chat_display.tag_configure("jarvis_message", foreground="#333333", font=("Helvetica", 10))
    
    # Create a frame for user input and buttons
    input_frame = tk.Frame(root, bg="#f0f0f0")
    input_frame.pack(fill=tk.X, padx=10, pady=5)
    
    # Create an entry widget for user input
    global user_input
    user_input = tk.Entry(
        input_frame, 
        width=70, 
        font=("Helvetica", 10),
        relief=tk.FLAT,
        bg="#ffffff"
    )
    user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
    user_input.bind("<Return>", on_enter)
    user_input.focus_set()
    
    # Create a submit button
    submit_button = ttk.Button(
        input_frame, 
        text="Send", 
        command=submit_text
    )
    submit_button.pack(side=tk.LEFT, padx=5, pady=5)
    
    # Create a voice button
    voice_button = ttk.Button(
        input_frame, 
        text="🎤", 
        command=voice_command
    )
    voice_button.pack(side=tk.LEFT, padx=5, pady=5)
    
    # Create a status label
    global status_label
    status_label = tk.Label(root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
    status_label.pack(side=tk.BOTTOM, fill=tk.X)
    
    # Display welcome message
    display_assistant_message("Welcome to Jarvis AI Assistant. How can I help you today?")
    
    # Start the mainloop
    root.mainloop()

# Main execution
if __name__ == '__main__':
    # Default to GUI mode
    gui_mode = True
    
    # Ask if user wants GUI or terminal mode
    try:
        mode_choice = input("Choose mode: (1) GUI, (2) Terminal [Default: GUI]: ").strip()
        if mode_choice == "2":
            gui_mode = False
    except:
        gui_mode = True
    
    if gui_mode:
        start_gui()
    else:
        # Terminal mode
        speak("Welcome to Jarvis A.I. How can I help you, Ankit?")
        
        # Ask for input mode only once at startup.
        mode = input("Choose input mode: (1) Voice, (2) Text: ").strip()
        input_mode = "voice" if mode == "1" else "text"
        
        # Initialize conversation history for chat fallback.
        # conversation_history = load_conversation_history() # This line is now redundant as it's global

        while True:
            # Get user query using the chosen input mode.
            query = take_voice_command() if input_mode == "voice" else get_text_command()
            
            # Process the command and check if we should continue or exit
            if not process_command(query):
                break 