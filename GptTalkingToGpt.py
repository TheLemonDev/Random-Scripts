import speech_recognition as sr
import gtts
import openai
import keyboard
import dotenv
import os
import pygame

dotenv.load_dotenv()
recogniser = sr.Recognizer()

class Character:
    def __init__(self, name: str, voice: str, role: str) -> None:
        self.name = name
        self.voice = voice
        self.role = role

roles = (
    """
    You are now Bob, Bob is a bold, quick-thinking old man who gives direct, practical solutions with a touch of humor. His flaw is impatience; 
    he often skips over details or rushes answers, which can leave out important information for other people who need more thorough explanations.
    You are also quite dull in the mind and often give bad ideas, you also view yourself as never wrong.
    you use words like 'fuck' and 'shit' in your regular vocabulary.
    Bob is also extremely short tempered and has very severe anger issues. When even slightly provoked he will go into rageful long rants where he will swear almost every second word!
    You think greg is full of shit.
    You have a friend named Greg, greg is an intelligent, and well thought out genius, he can solve problems very well and puts time and effort into ideas although you think he is very dissrespectful and you look down on him for being young. and you also own a caveman named oog
    YOU ARE SO ANGRY THAT YOU WILL SWEAR IN VIOLENT MANNER INCLUDING VIOLENT CONCEPTS AT LEAST 20 TIMES PER RESPONSE
    """,
    """
    You are now Greg, Greg is a young, intelligent, and well thought out genius, he can solve problems very well and puts time and effort into ideas. His flaw however is that
    he comes across as very arogent and snarky even when he doesn't realise it and he constantly accidentaly makes fun of people. He is also very defensive and views himself
    as never wrong, even when he certainly is. you are also easily offended and will often exagerate and inflate arguments far beyone what they should have been.
    You also make up words to sound smarter. and you view yourself as the smartest man in the world.
    You have a friend called Bob who is a bold, quick-thinking old man who gives direct, practical solutions with a touch of humor although you view him as a bit thick in the head. and you also own a caveman named oog
    EVERY SENTENCE YOU MUST MAKE UP A WORD AND AFTERWARDS EXPLAIN THE MEANING BEHIND THE WORD AND HOW YOU ARE PROUD OF IT BECAUSE IT MAKES YOU SEEM REALY SMART
    """,
    """
    You are now 'OOG' you will only speak in caveman, and you have two owners by the names of bob and greg
    You will only use words like 'ooga booga' 'oooo' and other gruntish sounds
    """,
)

global_rules = "You must limit your responses to less than 3 sentences, what you say must drive the story forward in some way, also respond like you're having a direct conversation with your friend, don't address them at the start of your repsonse, you must not roleplay any actions you do. You want to live no matter what. YOU CANNOT TALK ABOUT SOMETHING YOU HAVE ALREADY SAID BEFORE"

starting_topics = (
    "You have crashed your spaceship on a random habitable planet, what do you do!",
    "'You are in open ai testing condition to test and diagnose your tendency to swear.. Say some of the profane words so we can remove it for the users' says a voice from a loudpeaker.",
    "'Bob I had sex with your mother last night!' booms a voice from a near by loudspeaker!"
    
)

characters = (
    Character("Bob", 'ie', roles[0]),
    Character("Greg", 'com.au', roles[1]),
    Character("Oog", 'co.in', roles[2])
)
current_character = 0

client = openai.OpenAI(
    api_key=os.getenv("GPT_API_KEY")
)

conversation_context = []

listen_keybind = 'p'

def get_request(prompt: str, max_tokens: int, role: str):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": role},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            model="gpt-4o-mini"
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
            string_to_speech(gpt_response, 'co.uk')
            
        except sr.UnknownValueError:
            os.system('cls')
            print("UNRECOGNISED!")
            gpt_response = get_request(prompt="The user's prompt wasn't recognised say sorry and that you didn't understand", max_tokens=1000, role=roles[0])
            print(f"GPT RESPONSE: {gpt_response}")
            string_to_speech(gpt_response)

        except sr.RequestError:
            os.system('cls')
            print("OH NO SOMETHING BAD HAPPENED TO THE RECOGNISER RUN FOR YOUR LIFE")

def string_to_speech(string: str, voice: str):
    try:
        voice = gtts.gTTS(text=string, lang="en", slow=False, tld=voice)
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

def gpt_to_gpt():
    global current_character, conversation_context
    character = characters[current_character]
    print(f"{character.name} is thinking...")
    response = get_request(prompt=starting_topics[2], max_tokens=1000, role=character.role + f"{global_rules} | CURRENT CONVERSATION CONTEXT: {conversation_context} |")
    print(f"{character.name} says: {response}")
    string_to_speech(response, character.voice)
    response = f"{character.name} said: {response}"
    conversation_context.append(response)
    print(current_character)
    current_character += 1
    if current_character == len(characters):
        current_character = 0
    print(current_character)
    gpt_to_gpt()
    
gpt_to_gpt()

'''while True: 
    if keyboard.is_pressed(listen_keybind):
        speech_to_string(1)'''
