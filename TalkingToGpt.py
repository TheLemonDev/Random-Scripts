import speech_recognition as sr
import gtts
import openai
import keyboard
import dotenv
import os
import pygame
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import sys
import threading

dotenv.load_dotenv()
recogniser = sr.Recognizer()

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
	""",
)

listen_keybind = 'p'

class Main_window(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle('GPT Home')
		self.setGeometry(100, 100, 600, 400)
		self.setStyleSheet("background-color: black;")
		self.settings_active = False

		self.central_widget = QWidget()
		self.setCentralWidget(self.central_widget)

		self.settings_widget = QWidget(self)
		self.settings_widget.setFixedSize(200, 400)
		self.settings_widget.setStyleSheet("background-color: rgba(30, 30, 30, .9);")
		self.settings_widget.move(600, 0)

		self.text = QLabel("HELLO WORLD TEST")
		self.text.setStyleSheet("text-aligne: center;")

		self.button = QPushButton(self)
		self.button.setIcon(QIcon('settings_icon.png'))
		self.button.setFixedSize(QSize(35, 35))
		self.button.setIconSize(QSize(30, 30))

		button_style = """
					QPushButton {
						border: none;
						background-color: transparent;
					}
					QPushButton:hover {
						background-color: rgba(255, 255, 255, .2);
						border-radius: 10px;
					}
					QPushButton:pressed {
						background-color: rgba(255, 255, 255, .3);
						border-radius: 10px;
					}
					"""

		self.button.setStyleSheet(button_style)
		self.button.move(550, 10)
		self.button.clicked.connect(self.move_settings)
		self.button.raise_()

	def change_colour(self, color):
		self.setStyleSheet(f"background-color: {color};")

	def move_settings(self):
		self.settings_active = not self.settings_active
		if self.settings_active:
			self.settings_widget.move(600, 0)
		else:
			self.settings_widget.move(400, 0)
		self.button.raise_()

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
		window.change_colour("crimson")
		os.system('cls')
		print("Adjusting for ambient sound...")
		recogniser.adjust_for_ambient_noise(source=source, duration=sensitivity_adjustment_duration)
		window.change_colour("lawngreen")
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
			gpt_response = get_request(prompt="The user's prompt wasn't recognised say sorry and that you didn't understand", max_tokens=1000, role=roles[0])
			print(f"GPT RESPONSE: {gpt_response}")
			string_to_speech(gpt_response)

		except sr.RequestError:
			os.system('cls')
			print("OH NO SOMETHING BAD HAPPENED TO THE RECOGNISER RUN FOR YOUR LIFE")

def string_to_speech(string: str):
	try:
		window.change_colour("cyan")
		voice = gtts.gTTS(text=string, lang="en", slow=False, tld="com")
		voice.save('voice.mp3')
		pygame.mixer.init()
		pygame.mixer.music.load('voice.mp3')
		pygame.mixer.music.play()
		while pygame.mixer.music.get_busy():
			if keyboard.is_pressed(listen_keybind):
				break
			pass
		pygame.mixer.quit()
		os.remove('voice.mp3')
		window.change_colour("black")
	
	except:
		print("TTS error!")

def listen_for_key():
	while True:
		if keyboard.is_pressed(listen_keybind):
			speech_to_string(1)

app = QApplication(sys.argv)

window = Main_window()
window.show()

listener_thread = threading.Thread(target=listen_for_key, daemon=True)
listener_thread.start()

sys.exit(app.exec())