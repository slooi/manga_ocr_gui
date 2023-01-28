# #################################
# IMPORTS
# #################################
from PIL import ImageGrab # ImageGrab only supported on Windows and macOS
from pynput import mouse, keyboard
import os 
import time
from manga_ocr import MangaOcr

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
		self.possible_str_keys = ['i', '}', 'd', 'c', 'R', '|', 'O', 'U', 'Key.alt_l', 't', ',', 'Key.f8', 'Key.right', 'T', 'b', 'm', 'Key.shift_r', 'Key.page_down', 'Key.backspace', 'l', 'Key.alt_gr', 'X', '<96>', '~', 'Key.f7', 'Key.cmd', 'W', '<255>', '^', '2', '.', 'Q', ']', '-', '6', 'H', 'Key.f1', 'y', 'D', '<105>', 'J', '`', 'P', '""', 'Key.f10', '<97>', ':', '\\x01', '1', 'K', '0', 'Key.media_play_pause', 'Key.media_volume_down', '=', 'p', 'Key.f11', 'r', 'Key.media_volume_up', 'a', '4', 'Key.tab', 'Key.page_up', '{', 'B', 'Key.media_next', 'Key.caps_lock', 'w', '/', 'Key.down', '3', 'Key.f4', 'Key.num_lock', '8', '5', '[', 'Key.f9', '9', 'Key.f6', 'N', '%', 'E', 'z', 'Key.enter', 'Key.ctrl_r', '7', 'u', 'G', '(', '*', 'Key.f3', '<12>', 'n', 'Key.space', 'g', 'q', 'Key.ctrl_l', 'h', '?', '!', '<102>', 'o', 'I', 'e', 'C', '<', '$', '<98>', 'Key.esc', ')', 'f', 'L', 'Key.home', '>', '#', '<110>', '\\x03', '<99>', 'v', 'Key.left', '@', 'M', 'Key.print_screen', ';', 'Key.insert', 'x', '+', 'Key.delete', 'Key.media_volume_mute', 'Key.shift', 'F', 'j', '<103>', '_', 'S', 's', '"', 'Key.media_previous', 'Z', 'Key.up', 'A', '<104>', 'V', '&', '<101>', '\\\\', 'Key.end', 'Key.f12', 'k', '<100>', 'Key.f2', 'Y', 'Key.f5']
		self.callback = callback
		self.setup_listener()

	def setup_listener(self):
		listener = keyboard.Listener(on_press=self._on_press,on_release=self._on_release)
		listener.start()
	
	def _on_press(self,key):
		self._on_event(str(key).replace("'",""),True)

	def _on_release(self,key):
		self._on_event(str(key).replace("'",""),False)

	def _on_event(self,str_key:str,is_press:bool):
		self.keys_down[str_key] = is_press
		# print("self.keys_down",self.keys_down)
		self.update()

	# This function runs whenever a keyboard input had been updated
	def update(self):
		self.callback(self)

	def get_key(self,key):
		if key not in self.possible_str_keys:
			raise Exception("ERROR: KeyboardHandler does not support such key `{key}`")
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
		key_grave_accent_down = keyboard_handler.get_key("`")
		key_alt_l_down = keyboard_handler.get_key("Key.alt_l")
		if key_alt_l_down and key_grave_accent_down:
			self.set_capture_mode(not self.capture_mode_on)
			print("self.capture_mode_on",self.capture_mode_on)
			

	def set_capture_mode(self,is_on):
		self.capture_mode_on = is_on


class SaveImageStrategy():
	def strategy(self,im):
		# Save the image to a file
		im.save("captures/screenshot.png")
		print("took screenshot")
# #################################
# FUNCTIONS
# #################################




# #################################
# MAIN CODE
# #################################
counter=0

def setup():
	global counter

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
	# mocr = MangaOcr()
	# Screen Capturer
	screen_capturer = ScreenCapturer(SaveImageStrategy())

	# Main Loop
	while True:
		time.sleep(1)
		# counter = counter + 1
		if counter > 3:
			break


setup()
