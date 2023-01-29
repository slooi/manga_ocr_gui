from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QWidget
from PySide6 import QtGui
from PySide6 import QtCore
from PySide6.QtCore import QTimer, QByteArray, Qt
from PIL import ImageGrab # ImageGrab only supported on Windows and macOS
from PIL.ImageQt import ImageQt
import time

class ScreenOverlay(QWidget):
	# This is a GUI which handles the overlay of the screen. 
	# It renders the desktop's screen onto this GUI widget so you can click select text without highlighting the html
	def __init__(self) -> None:
		# Create Application
		self.app = QApplication([])

		# Create View & View Setup
		self.view = QGraphicsView()
		# self.view.setWindowFlags(QtCore.Qt.Tool)
		self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

		# Create Scene
		self.scene = QGraphicsScene()
		
		# View the scene
		self.view.setScene(self.scene)

		# TEMPORARY
		# QTimer.singleShot(2000,self.exit)

		
		self.render_scene()

		# Execute Eventloop
		self.app.exec()

	def render_scene(self):

		# Get image from screen
		im = ImageGrab.grab(bbox=get_geometry(app=self.app))
		# im.save("testings/aaaaaaa.png")				
		qim = ImageQt(im)
		pixmap = QtGui.QPixmap.fromImage(qim)

		# image = QImage("captures/screenshot.png") # For QPixMap in the future
		# pixmap = QPixmap.fromImage(image)

		self.scene.addPixmap(pixmap)

		self.show()
		# ###################

	def get_image(self):
		pass
		# im = ImageGrab.grab(bbox=(selection_area["left"], selection_area["top"], selection_area["right"], selection_area["bottom"]))

	def show(self):
		# Show Main Window
		# self.view.show()
		self.view.showFullScreen()


	def exit(self):
		print("EXITING")
		self.app.exit()

def get_geometry(app):
	screen_q_rect = app.primaryScreen().availableGeometry()
	left = screen_q_rect.left()
	top = screen_q_rect.top()
	right = screen_q_rect.right()
	bottom = screen_q_rect.bottom()

	return (left,top,right,bottom)
	


a = ScreenOverlay()


""" 
Separate for:
 - closing window
 - opening window
 - app should be running in the back and opens windows
 - how to display image?? no?
 - main gui vs screen overlay
 SINGULAR QAPPLICATION as have start up time. -> Actually they dont
"""