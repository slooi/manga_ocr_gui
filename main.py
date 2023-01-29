# #################################
# IMPORTS
# #################################
from PIL import ImageGrab # ImageGrab only supported on Windows and macOS
from pynput import mouse, keyboard
import os 
import time
from manga_ocr import MangaOcr
import pyperclip

# #################################
# CONSTANTS
# #################################
FOLDER_NAME = "captures"

# #################################
# CLASSES
# #################################
class KeyboardHandler():
	# Handles the storage, updating and listening of keyboard inputs
	def __init__(self,callback) -> None:
		super().__init__()
		self.keys_down = {}
		self.possible_str_keys = ['<100>', '1', '\\\\', 'key.cmd', '^', 'key.media_volume_mute', 't', 'key.media_previous', 'key.media_volume_down', 'key.f1', '7', '+', '{', '[', 'key.print_screen', 'd', '(', '"', '<110>', 'key.right', 'key.f10', '<96>', 'z', 'key.f11', 'key.f5', '>', '.', 'key.ctrl_r', '<102>', '3', 'key.f6', 'key.left', '<97>', 'j', '<101>', '|', '`', '""', 'v', '<98>', 'key.alt_gr', 'key.esc', 'key.f8', '_', '&', 'a', 'c', '4', 'h', '\\x03', 'key.caps_lock', 'key.ctrl_l', '$', '<104>', 'key.page_up', 'key.alt_l', 'q', 'key.f4', '2', 'key.media_volume_up', 'g', 's', '<12>', 'e', 'key.delete', 'key.media_next', 'i', '?', '}', '<105>', 'key.shift', 'key.page_down', ',', ')', '!', 'key.f2', 'x', 'key.tab', '<255>', '5', '-', 'b', 'key.media_play_pause', '9', '6', 'l', 'key.shift_r', ':', 'key.down', 'key.home', '=', '~', 'y', '0', '\\x01', 'key.f9', 'key.f3', '%', 'f', 'key.up', 'k', 'key.space', 'p', 'w', '<103>', 'key.f7', '*', '<99>', 'o', '#', 'key.backspace', 'key.f12', '@', 
'key.end', '/', '8', '<', 'key.enter', ']', 'n', 'key.insert', 'key.num_lock', 'u', 'r', 'm', ';']
		self.callback = callback
		self.setup_listener()

	def setup_listener(self):
		listener = keyboard.Listener(on_press=self._on_press,on_release=self._on_release)
		listener.start()
	
	def _on_press(self,key):
		self._on_event(str(key).replace("'","").lower(),True)

	def _on_release(self,key):
		self._on_event(str(key).replace("'","").lower(),False)

	def _on_event(self,str_key:str,is_press:bool):
		self.keys_down[str_key] = is_press
		# print("self.keys_down",self.keys_down)
		self.update()

	# This function runs whenever a keyboard input had been updated
	def update(self):
		self.callback(self)

	def get_key(self,key):
		if key not in self.possible_str_keys:
			raise Exception(f"ERROR: KeyboardHandler does not support such key `{key}`")
		return self.keys_down[key] if key in self.keys_down else False

class SelectionAreaHandler():
	# This class handles the selection of an area
	def __init__(self,callback=None) -> None:
		super().__init__()
	
		# members
		self.mouse_down = {
			"x":0,
			"y":0
		}
		self.mouse_up = {
			"x":0,
			"y":0
		}
		self.selection_area = {
			"top":0,
			"bottom":0,
			"left":0,
			"right":0,
		}

		self.callback = callback

		# private methods
		self.setup_listener()

	def setup_listener(self):
		# Collect events until released
		listener = mouse.Listener(
			on_click=self.on_click)
		listener.start()
		
	def on_click(self,x, y, button, pressed):
		if(button is not mouse.Button.left): return

		
		if pressed:
			self.mouse_down = {
				"x":x,
				"y":y
			}
		else:
			self.mouse_up = {
				"x":x,
				"y":y
			}
			
			# Update selection area
			# horizontal
			left = self.mouse_down["x"] if self.mouse_down["x"] < self.mouse_up["x"] else self.mouse_up["x"]
			right = self.mouse_up["x"]  if self.mouse_down["x"] < self.mouse_up["x"] else self.mouse_down["x"]

			#  vertical
			top = self.mouse_down["y"] if self.mouse_down["y"] < self.mouse_up["y"] else self.mouse_up["y"]
			bottom = self.mouse_up["y"] if self.mouse_down["y"] < self.mouse_up["y"] else self.mouse_down["y"]

			# Actual update
			self.selection_area["left"] = left
			self.selection_area["right"] = right
			self.selection_area["top"] = top
			self.selection_area["bottom"] = bottom

			# Callback precursor
			self.callback_precursor()

	# Does validation/checks before running callback
	def callback_precursor(self):
		# Check if selection area meets minimum requirements
		width_is_less_than_required = self.selection_area["right"] - self.selection_area["left"] < 10
		height_is_less_than_required = self.selection_area["bottom"] - self.selection_area["top"] < 10

		if width_is_less_than_required: return
		if height_is_less_than_required: return

		# Callback
		self.callback(self)
		


	def get_selection_area(self):
		return self.selection_area


class ScreenCapturer():
	# This class handles the process of capturing the screen 
	def __init__(self,post_capture_selection_strategy) -> None:

		# Members
		self.capture_mode_on = False

		# Strategy/Callback
		self.post_capture_selection_strategy = post_capture_selection_strategy

		# Setup Handlers
		self.selection_area_handler = SelectionAreaHandler(self.capture_selection)
		self.keyboard_handler = KeyboardHandler(self.handleKeyboardChange)

	def capture_selection(self,selection_area_handler:SelectionAreaHandler):
		if self.capture_mode_on:
			# Get selected area
			selection_area = selection_area_handler.get_selection_area()
			# print("selection_area",selection_area)

			# Capture the selected area of the screen
			im = ImageGrab.grab(bbox=(selection_area["left"], selection_area["top"], selection_area["right"], selection_area["bottom"]))

			self.post_capture_selection(im)

	def post_capture_selection(self,im):
		# Use strategy
		self.post_capture_selection_strategy.strategy(im)

		# Turn off capture mode
		self.set_capture_mode(False)
				

	def handleKeyboardChange(self,keyboard_handler:KeyboardHandler):
		key_q_down = keyboard_handler.get_key("q")
		key_alt_l_down = keyboard_handler.get_key("key.alt_l")
		key_shift_down = keyboard_handler.get_key("key.shift")
		
		print("keyboard_handler.keys_down",keyboard_handler.keys_down)
		if key_alt_l_down and key_shift_down and key_q_down:
			self.set_capture_mode(not self.capture_mode_on)
			print("self.capture_mode_on",self.capture_mode_on)
			

	def set_capture_mode(self,is_on):
		self.capture_mode_on = is_on

	
	# #################################
	# STRATEGIES
	# #################################
	class SaveImageStrategy():
		def strategy(self,im):
			# Save the image to a file
			im.save("captures/screenshot.png")
			print("took screenshot")
			
	class MangaOCRStrategy():
		def __init__(self,mocr) -> None:
			self.mocr = mocr
			
		def strategy(self,im):
			old_time = time.time()
			# Pass image to ocr
			text = self.mocr(im)
			
			pyperclip.copy(text)
			pyperclip.paste()
			print(f"OCR compute time: {time.time()-old_time}")
			print(f"Text: {text}")

			
			
# #################################
# FUNCTIONS
# #################################




# #################################
# MAIN CODE
# #################################
def setup():

	# #################################
	# DEPENDENCIES
	# #################################
	# Download manga_ocr model     !@#!@#!@#

	# Create captures folder if it doesn't already exist
	if not os.path.exists(FOLDER_NAME):
		os.mkdir(FOLDER_NAME)
		
		
	# #################################
	# MAIN VARIABLES
	# #################################
	# mocr
	mocr = MangaOcr()
	# Screen Capturer
	screen_capturer = ScreenCapturer(ScreenCapturer.MangaOCRStrategy(mocr))

	counter = 0

	# Main Loop
	while True:
		# time.sleep(1)
		# counter = counter + 1
		if counter > 3:
			break

setup()
