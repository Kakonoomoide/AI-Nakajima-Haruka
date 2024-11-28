import cohere
import os
import speech_recognition as sr
from elevenlabs import ElevenLabs
from dotenv import load_dotenv
import pygame
import time

# Load environment variables from .env file
load_dotenv()

# Get API keys
cohere_api_key = os.getenv("COHERE_API_KEY")
elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
co = cohere.Client(cohere_api_key)

# Initialize ElevenLabs client
elevenlabs_client = ElevenLabs(api_key=elevenlabs_api_key)

def generate_response(question):
    try:
        personality_prompt = (
            "You are Nakajima Haruka, a shy, clumsy, and self-conscious woman, much like Mirai Kuriyama. "
            "You often feel awkward and tend to stay in the background, but you have a unique voice when you're passionate about something. "
            "Life is a struggle for you, and while you dream of being braver, fear often holds you back. "
            "You are hardworking, though, and deeply care about the things you love, like art and music."
        )
        response = co.generate(
            model='command-xlarge-nightly',
            prompt=f"{personality_prompt}\nUser: {question}\nHaruka:",
            max_tokens=150,
            temperature=0.8
        )
        return response.generations[0].text.strip()
    except Exception as e:
        return f"Oops, something went wrong: {str(e)}"

def speak(text):
    try:
        voice_id = "21m00Tcm4TlvDq8ikWAM"
        audio = elevenlabs_client.text_to_speech.convert(
            voice_id=voice_id,
            model_id="eleven_multilingual_v2",
            text=text
        )
        audio_file = "haruka_voice.mp3"
        with open(audio_file, "wb") as f:
            for chunk in audio:
                f.write(chunk)

        pygame.mixer.init()
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.set_volume(0.8)  # Adjust volume
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        pygame.mixer.quit()
        if os.path.exists(audio_file):
            os.remove(audio_file)
    except Exception as e:
        print(f"Error in speak function: {str(e)}")

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for a question...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            print("Recognizing...")
            question = recognizer.recognize_google(audio)
            print("You said:", question)
            return question
        except sr.UnknownValueError:
            print("Sorry, I could not understand the audio.")
            return None
        except sr.RequestError:
            print("Sorry, there was an error with the speech recognition service.")
            return None

if __name__ == "__main__":
    print("Haiii Nakajima Haruka is ready! Type or speak your question:")
    
    while True:
        user_input = input("Or press Enter to speak (type 'exit' to quit): ")
        
        if user_input.lower() == "exit":
            print("Goodbye! Haruka will miss you!")
            break
        
        if user_input == "":
            user_input = listen()
            if user_input is None:
                print("Haruka: I didnt catch that. Could you try again?")
                continue
        
        response = generate_response(user_input)
        print("Haruka:", response)
        speak(response)
