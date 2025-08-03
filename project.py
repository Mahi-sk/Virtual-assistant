import openai
from dotenv import load_dotenv
import speech_recognition as sr
import os
import webbrowser
import tempfile
import pygame

# === LOAD ENVIRONMENT VARIABLES ===
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in .env")

client = openai.OpenAI(api_key=api_key)

# === OPENAI TEXT-TO-SPEECH ===
def speak(text):
    response = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=text
    )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
        temp_audio.write(response.content)
        temp_path = temp_audio.name

    pygame.mixer.init()
    pygame.mixer.music.load(temp_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        continue

# === LISTEN FUNCTION ===
def listen_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        speak("How can I help you?")
        audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio)
        print(f"You said: {command}")
        return command
    except:
        speak("Sorry, I didn't get that.")
        return ""

# === COMMAND PARSER ===
def parse_intent(command):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": """You are a helpful assistant that translates user commands into structured actions.

Return only one of the following formats:

1. To open a file or app:
   open_file: value: C:\\Windows\\System32\\notepad.exe

2. To search the web:
   search_web: value: search query here

3. To send email:
   send_email: value: email@example.com, message here

If the command does not match any of the above, respond with:
chat_response: value: actual message to say
"""},

                {"role": "user", "content": command}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"chat_response: value: Sorry, I couldn't understand that due to an error."

# === EXECUTE ACTION ===
def perform_action(reply):
    if reply.startswith("open_file:"):
        filename = reply.split("value:")[1].strip()
        speak("Opening file or application.")
        try:
            os.startfile(filename)
        except:
            speak("Sorry, I couldn't open the file.")
    elif reply.startswith("search_web:"):
        query = reply.split("value:")[1].strip()
        speak(f"Searching the web for {query}")
        webbrowser.open(f"https://www.google.com/search?q={query}")
    elif reply.startswith("send_email:"):
        speak("Sending emails is not yet implemented.")
    elif reply.startswith("chat_response:"):
        message = reply.split("value:")[1].strip()
        speak(message)
    else:
        speak("Sorry, I can't perform that task.")

# === MAIN LOOP ===
if __name__ == "__main__":
    while True:
        command = listen_command()
        if "exit" in command.lower():
            speak("Goodbye!")
            break
        if command:
            reply = parse_intent(command)
            print("Parsed Reply:", reply)
            perform_action(reply)
