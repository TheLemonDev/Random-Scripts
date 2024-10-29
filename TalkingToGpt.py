import speech_recognition as sr
import gtts
import openai
import keyboard
import dotenv
import os
import pygame

listen_keybind = 'p'

dotenv.load_dotenv()

client = openai.OpenAI(
    api_key=os.getenv("GPT_API_KEY")
)

roles = (
    "You are a helpful assistant"
)

recogniser = sr.Recognizer()

def get_request(prompt: str, max_tokens: int, role: str):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": role},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            model="gpt-3.5-turbo"
        )
        return(chat_completion.choices[0].message.content)
    
    except:
        os.system('cls')
        print("well obviously something went wrong but im too lazy to find out what errors I should check for so just check your internent or something :p")
    return None

def speech_to_string(sensitivity_adjustment_duration: int):
    audio_data = sr.AudioData(b"", 16000, 2)
    with sr.Microphone() as source:
        os.system('cls')
        print("Adjusting for ambient sound...")
        recogniser.adjust_for_ambient_noise(source=source, duration=sensitivity_adjustment_duration)
        os.system('cls')
        print(f"Listening... (release {listen_keybind} to stop!)")
        while True:
            if keyboard.is_pressed(listen_keybind):
                print(1)
                segment = recogniser.listen(source=source, phrase_time_limit=1)
                audio_data = sr.AudioData(audio_data.frame_data + segment.frame_data, segment.sample_rate, segment.sample_width)
            else:
                break
        
        os.system('cls')
        print("Recognising...")

        try:
            string = recogniser.recognize_google(audio_data)
            os.system('cls')
            print(f"RECOGNISED!: {string}")
            gpt_response = get_request(prompt=string, max_tokens=1000, role=roles[0])
            print(f"GPT RESPONSE: {gpt_response}")
            string_to_speech(gpt_response)
            
        except sr.UnknownValueError:
            os.system('cls')
            print("UNRECOGNISED!")

        except sr.RequestError:
            os.system('cls')
            print("OH NO SOMETHING BAD HAPPENED TO THE RECOGNISER RUN FOR YOUR LIFE")

def string_to_speech(string: str):
    try:
        voice = gtts.gTTS(text=string, lang="en", slow=False, tld="co.uk")
        voice.save('voice.mp3')
        pygame.mixer.init()
        pygame.mixer.music.load('voice.mp3')
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pass
        pygame.mixer.quit()
        os.remove('voice.mp3')
    
    except:
        print("TTS error!")


while True:
    if keyboard.is_pressed(listen_keybind):
        speech_to_string(1)
