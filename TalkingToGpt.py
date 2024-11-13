import speech_recognition as sr
import gtts
import openai
import keyboard
import dotenv
import os
import pygame
import time

recogniser = sr.Recognizer()
listening = False
listen_keybind = 'p'

client = openai.OpenAI(
	api_key=os.getenv("GPT_API_KEY")
)

roles = (
	"""
	You are a helpful assistant focused on providing clear and direct answers. 
	Respond to all questions with the simplest possible explanations or solutions. 
	If given a complex equation, provide the answer immediately without extra explanations. 
	For example, if asked to calculate the settings_widget root of 72, simply respond with '8.4853' (the numerical answer).
	All of your responses will be read out by a tts voice.
	Always write numbers in numerical form (not in letter form!)
    IF THE PROMPT EXPLICITLY ASKS TO CHANGE YOUR KEYBIND ONLY RESPOND WITH 'press a key' if they just mention keybinds and make no reference to changing it just respond normaly
    IF THE USER EXPLICITLY ASKS TO CLEAR YOUR MEMORY ONLY RESPOND WITH 'clearing memory' if they just mention memory and make no reference to clearing it just respond normaly
    IF THE USER EXPLICITLY ASKS TO CHANGE YOUR VOLUME ONLY RESPOND WITH ''volumeset' to (and the number they want to set it to in numerical form)' if the volume the user wants to set it to exceeds 10 or is lower than 0 say that you can't set the volume to that number
    Every prompt will also have a conversation history, it includes every prompt that has been given to you and every response you gave to said prompt.
	""",
)

conversation_memory = []
forget_range = 30

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
	global conversation_memory
	
	audio_data = sr.AudioData(b"", 16000, 2)
	with sr.Microphone() as source:
		os.system('cls')
		print("Adjusting for ambient sound...")
		recogniser.adjust_for_ambient_noise(source=source, duration=sensitivity_adjustment_duration)

		os.system('cls')
		print(f"Listening... (release {listen_keybind} to stop!)")
		print(f"(Say that you would like to change your keybind, to reset the activation key!)")
		print(f"(Say that you would like to wipe the memory to reset the AI's memory)")
		while True:
			if keyboard.is_pressed(listen_keybind):
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
			role = roles[0]
			role = f"{role} + (PREVIOUS CONVERSATIONS): "
			for i in conversation_memory:
				role = f"{role} {i},"
			gpt_response = get_request(prompt=string, max_tokens=1000, role=role)
			print(f"GPT RESPONSE: {gpt_response}")
			string_to_speech(gpt_response)
			if gpt_response == "press a key":
				change_keybind()
			elif gpt_response == "clearing memory":
				conversation_memory.clear()
				print("Memory Wiped!")
				string_to_speech("Memory Wiped!")
			elif "volumeset" in gpt_response.split():
				pygame.mixer.quit()
				pygame.mixer.init()
				print(f"Volume set from {pygame.mixer.music.get_volume()} to {gpt_response.split()[2]}!")
				pygame.mixer.music.set_volume(int(gpt_response.split()[2]) * .1)
				pygame.mixer.quit()
			else:
				add_to_memory(gpt_response, string)
			
		except sr.UnknownValueError:
			os.system('cls')
			print("UNRECOGNISED!")
			gpt_response = get_request(prompt="The user's prompt wasn't recognised say sorry and that you didn't understand", max_tokens=1000, role=roles[0])
			print(f"GPT RESPONSE: {gpt_response}")
			string_to_speech(gpt_response)

		except sr.RequestError:
			os.system('cls')
			print("OH NO SOMETHING BAD HAPPENED TO THE RECOGNISER RUN FOR YOUR LIFE")

def string_to_speech(string: str):
    try:
        voice = gtts.gTTS(text=string, lang="en", slow=False, tld="com")
        voice.save('voice.mp3')
        pygame.mixer.quit()
        pygame.mixer.init()
        pygame.mixer.music.load('voice.mp3')
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            if keyboard.is_pressed(listen_keybind):
                break
            pass
        pygame.mixer.quit()
        os.remove('voice.mp3')

    except:
    	print("TTS error!")

def change_keybind():
    global listen_keybind
    print("Press a new key for the keybind...")

    while True:
        event = keyboard.read_event()
        if event.event_type == keyboard.KEY_DOWN:
            print(f"New keybind set to '{event.name }'")
            listen_keybind = event.name
            string_to_speech(f"New keybind set to '{event.name }'")
            time.sleep(0.5)
            break

def add_to_memory(gpt_response: str, prompt: str):
    global conversation_memory
    conversation_memory.append(f"|User said: {prompt} and you responded with {gpt_response}|")
    if len(conversation_memory) > forget_range:
        conversation_memory.pop(0)

def listen_for_key():
	global listening
	os.system('cls')
	print(f"~CHAT GPT TTS BOT~")
	print(f"Press {listen_keybind} to activate!")
	while True:
		if keyboard.is_pressed(listen_keybind) and not listening:
			listening = True
			speech_to_string(1)
			listening = False
			os.system('cls')
			print(f"~CHAT GPT TTS BOT~")
			print(f"Press {listen_keybind} to activate!")

listen_for_key()