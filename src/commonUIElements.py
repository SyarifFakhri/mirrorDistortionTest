from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QGridLayout, QWidget, QPushButton, QVBoxLayout, \
	QHBoxLayout, QScrollArea, QSlider, QLineEdit, QFrame, QGroupBox, QSpacerItem
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QRect
import windowStyling

class CommonUI():
	@staticmethod
	def menuGrid(highlightedMenu=0):
		menuGrid = QVBoxLayout()
		menuGrid.setContentsMargins(0,0,0,0)

		mainTitle = CommonUI.labelCell('Distortion Tester', size=18)
		menuGrid.addWidget(mainTitle)
		menuGrid.addWidget(CommonUI.horizontalSpacer())

		menuItems = ['Main Menu'] #, 'Settings Menu', 'Data Menu']

		for i in range(len(menuItems)):
			menuItem = CommonUI.labelCell(menuItems[i], size=13)

			if i == highlightedMenu:
				menuItem.setStyleSheet('background-color: #212431; color: white')
			menuGrid.addWidget(menuItem)

		menuGrid.addStretch()

		menuFrame = QFrame()
		menuFrame.setStyleSheet("background-color:" + windowStyling.darkBackgroundColor) # + "; border-radius: 5px")
		menuFrame.setLayout(menuGrid)

		return menuFrame

	@staticmethod
	def whiteQFrame():
		infoFrame = QFrame()
		infoFrame.setFrameStyle(QFrame.Box | QFrame.Raised)
		infoFrame.setStyleSheet('.QFrame {margin-right: 10px; margin-bottom: 10px;background-color: white; border-radius: 5px; border: 1px solid #E1E4E7;}')

		return infoFrame

	@staticmethod
	def labelCell(text, size=10, color='white'):
		label = QLabel(text)
		label.setContentsMargins(15,10,20,10)
		label.setFont(QtGui.QFont('Lato', pointSize=size))
		label.setStyleSheet('color: ' + color)
		return label


	@staticmethod
	def horizontalSpacer():
		spacer = QFrame()
		spacer.setFrameShape(QFrame.HLine)
		spacer.setMaximumHeight(1)
		spacer.setContentsMargins(0,0,0,0)
		# spacer.setLineWidth(0)
		# spacer.setFrameShadow(QFrame.Sunken)
		spacer.setStyleSheet('color: #434858')
		return spacer
