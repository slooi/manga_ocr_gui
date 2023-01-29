from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene
from PySide6 import QtGui
from PySide6 import QtCore




class ScreenOverlay():
	# This is a GUI which overlays the screen. It renders the desktop's screen onto this GUI widget so you can click select text without highlighting the html
	def __init__(self) -> None:
		# Create Application
		app = QApplication([])
		

		# Create Main Window + Show
		view = QGraphicsView()
		# view.setWindowFlags(QtCore.Qt.Tool)

		# Setup scene
		scene = self.setup_scene()
		view.setScene(scene)
		view.showFullScreen()

		# Show Main Window
		view.show()

		# Execute Eventloop
		app.exec()

	def setup_scene(self):
		# ###################
		# Create Scene
		scene = QGraphicsScene()

		# Create QImage to create QPixmap
		image = QImage("captures/screenshot.png") # For QPixMap in the future
		pixmap = QPixmap.fromImage(image)

		graphicPixmap = scene.addPixmap(pixmap)

		return scene
		# ###################


# QtGui.QGuiApplication.desk	    w.showFullScreen()

a = ScreenOverlay()