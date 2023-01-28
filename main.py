# #################################
# IMPORTS
# #################################
from PIL import ImageGrab # ImageGrab only supported on Windows and macOS
from pynput import mouse
import os 
import time

# #################################
# CONSTANTS
# #################################
FOLDER_NAME = "captures"

# #################################
# CLASSES
# #################################
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

# #################################
# FUNCTIONS
# #################################
def testingA(selection_area_handler:SelectionAreaHandler):
	# Get selected area
	selection_area = selection_area_handler.get_selection_area()
	print("selection_area",selection_area)

	# Capture the selected area of the screen
	im = ImageGrab.grab(bbox=(selection_area["left"], selection_area["top"], selection_area["right"], selection_area["bottom"]))

	# Save the image to a file
	im.save("captures/screenshot.png")
	print("took screenshot")



# #################################
# MAIN CODE
# #################################
counter=0

def setup():
	global counter

	# Download manga_ocr model     !@#!@#!@#

	# Create captures folder if it doesn't already exist
	if not os.path.exists(FOLDER_NAME):
		os.mkdir(FOLDER_NAME)
	
	# capture handler setup
	selection_area_handler = SelectionAreaHandler(testingA)

	# Main Loop
	while True:
		time.sleep(1)
		counter = counter + 1
		if counter > 3:
			break


setup()
