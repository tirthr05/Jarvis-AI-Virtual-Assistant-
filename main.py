import speech_recognition as sr      # for capturing audio from the microphone and converting speech to text
import webbrowser                   # to open URLs in the default web browser
import pyttsx3                      # offline text-to-speech engine as a fallback
import musicLibrary                 # custom module mapping song names to URLs for playback
import requests                     # to make HTTP requests (e.g., fetching news)
from openai import OpenAI           # OpenAI SDK to send prompts and receive AI responses
from gtts import gTTS               # Google Text-to-Speech to convert text to MP3
import pygame                       # for playing back the generated MP3 audio
import os                           # for file operations such as deleting temp files

# pip install pocketsphinx         # optional: install for offline speech recognition support

# Initialize the recognizer and text-to-speech engine
recognizer = sr.Recognizer()       # create a Recognizer() instance for speech recognition
engine = pyttsx3.init()            # initialize the pyttsx3 engine for offline TTS

# Your NewsAPI key (replace with your own key or use environment variables)
newsapi = "5b8573477b1c4a3e93c8a613f389f92e"

def speak_old(text):
    """
    Fallback text-to-speech using pyttsx3.
    :param text: The string to be spoken aloud.
    """
    engine.say(text)               # queue the text to be spoken
    engine.runAndWait()            # process and play the queued speech

def speak(text):
    """
    Primary text-to-speech using gTTS and pygame for playback.
    :param text: The string to convert to speech.
    """
    tts = gTTS(text)                       # create a gTTS object from the text
    tts.save('temp.mp3')                   # save the speech as a temporary MP3 file

    pygame.mixer.init()                    # initialize pygame mixer for audio playback
    pygame.mixer.music.load('temp.mp3')    # load the generated MP3 file
    pygame.mixer.music.play()              # start playing the MP3

    # wait until the playback has finished
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)       # sleep briefly to prevent busy-waiting

    pygame.mixer.music.unload()            # unload the MP3 from memory
    os.remove("temp.mp3")                  # delete the temporary file

def aiProcess(command):
    """
    Send the user’s command to the OpenAI API and return the AI’s response.
    :param command: The user’s spoken or typed command string.
    :return: The generated response text from the AI.
    """
    client = OpenAI(
        api_key="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"
    )
    completion = client.chat.completions.create(
        model="gpt-4.1",                                # specify the model to use
        messages=[
            {"role": "system", "content": (
                "You are a virtual assistant named Jarvis skilled in general tasks "
                "like Alexa and Google Cloud. Give short responses please"
            )},
            {"role": "user", "content": command}        # pass the user’s command to the model
        ]
    )
    # extract and return the assistant’s reply text
    return completion.choices[0].message.content

def processCommand(c):
    """
    Interpret the transcribed command and perform the corresponding action.
    :param c: The command string (expected lowercase for matching).
    """
    c = c.lower()                             # normalize to lowercase for easy comparisons

    # website shortcuts
    if "open google" in c:
        webbrowser.open("https://google.com")
    elif "open facebook" in c:
        webbrowser.open("https://facebook.com")
    elif "open youtube" in c:
        webbrowser.open("https://youtube.com")
    elif "open linkedin" in c:
        webbrowser.open("https://linkedin.com")

    # play a song from your custom library module
    elif c.startswith("play"):
        parts = c.split(" ", 1)                # split into ["play", "<song name>"]
        if len(parts) > 1:
            song = parts[1]                    # extract the song name
            link = musicLibrary.music.get(song)
            if link:
                webbrowser.open(link)
            else:
                speak(f"Sorry, I don't have a link for {song}.")
        else:
            speak("Please specify a song name after 'play'.")

    # fetch and read headlines using NewsAPI
    elif "news" in c:
        url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={newsapi}"
        r = requests.get(url)                 # send GET request to NewsAPI
        if r.status_code == 200:
            articles = r.json().get('articles', [])
            for article in articles:
                speak(article.get('title', 'No title available'))
        else:
            speak("Sorry, I couldn't fetch the news right now.")

    # fallback: send to GPT for general conversation or tasks
    else:
        output = aiProcess(c)
        speak(output)

if __name__ == "__main__":
    """
    Main loop:
    - Announce startup
    - Continuously listen for the wake word "Jarvis"
    - Upon hearing the wake word, listen for a follow-up command and process it
    """
    speak("Initializing Jarvis...")            # startup message

    while True:
        try:
            with sr.Microphone() as source:
                print("Listening for wake word...")
                # listen briefly for the wake word
                audio = recognizer.listen(source, timeout=2, phrase_time_limit=1)
            word = recognizer.recognize_google(audio)  # transcribe audio to text

            if word.lower() == "jarvis":       # check if user said the wake word
                speak("Yes?")                  # audio feedback that assistant is active
                with sr.Microphone() as source:
                    print("Awaiting command...")
                    audio = recognizer.listen(source)   # listen for the actual command
                    command = recognizer.recognize_google(audio)
                    processCommand(command)             # handle the command

        except Exception as e:
            # catch timeouts, recognition errors, network issues, etc.
            print(f"Error: {e}")
