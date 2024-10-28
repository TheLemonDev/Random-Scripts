import speech_recognition as sr
import gtts
import openai
import keyboard
import dotenv
import os

listen_keybind = 'p'

dotenv.load_dotenv()

client = openai.OpenAI(
    api_key=os.getenv("GPT_API_KEY")
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
        while keyboard.is_pressed(listen_keybind):
            segment = recogniser.listen(source=source)
            audio_data = sr.AudioData(audio_data.frame_data + segment.frame_data, segment.sample_rate, segment.sample_width)
        
        os.system('cls')
        try:
            string = recogniser.recognize_google(audio_data)
            print(f"RECOGNISED!: {string}")
            
        except sr.UnknownValueError:
            print("UNRECOGNISED!")

        except sr.RequestError:
            print("OH NO SOMETHING BAD HAPPENED TO THE RECOGNISER RUN FOR YOUR LIFE")

while True:
    if keyboard.is_pressed(listen_keybind):
        speech_to_string(1)

