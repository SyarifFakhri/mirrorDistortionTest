from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QGridLayout, QWidget, QPushButton, QVBoxLayout, \
	QHBoxLayout, QScrollArea, QSlider, QLineEdit, QFrame, QGroupBox
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QRect
import windowStyling
from commonUIElements import CommonUI

class MainWindow():
	def init_ui(self, mainWindow, settingsSaver):
		self.settingsSaver = settingsSaver

		mainLayout = QHBoxLayout()
		mainLayout.setContentsMargins(0,0,0,0)

		menuGrid = CommonUI.menuGrid()

		mainInfoPanel = self.mainInfoPanel()
		sideSettingsPanel = self.sideSettingsPanel()

		mainLayout.addWidget(menuGrid)
		# mainLayout.addStretch(1)
		mainLayout.addWidget(mainInfoPanel)
		mainLayout.addStretch(1)
		mainLayout.addWidget(sideSettingsPanel)


		widget = QWidget()
		widget.setLayout(mainLayout)
		mainWindow.setCentralWidget(widget)


	def createSlider(self, minVal, maxVal, minWidth=300, initialVal=100):
		slider = QSlider(Qt.Horizontal)
		slider.setMaximum(maxVal)
		slider.setMinimum(minVal)
		slider.setValue(initialVal)
		slider.setMinimumWidth(minWidth)
		return slider

	def createSliderWithLabel(self,minVal, maxVal, label,minWidth=300, initialVal=100):
		hBox = QHBoxLayout()
		slider = self.createSlider(minVal, maxVal, minWidth, initialVal)
		lbl = QLabel(label)
		labelValue = QLabel(str(initialVal))
		slider.valueChanged.connect(lambda val=slider.value(), label=labelValue : self.updateSliderValue(val, label))

		hBox.addWidget(lbl)
		hBox.addWidget(slider)
		hBox.addWidget(labelValue)
		return hBox, slider

	def updateSliderValue(self,val, label):
		label.setText(str(val))


	def createSliderGroup(self, groupTitle,sliderList):
		groupBox = QGroupBox(groupTitle)
		vBox = QVBoxLayout()

		for index,slider in enumerate(sliderList):
			vBox.addLayout(slider)

		groupBox.setLayout(vBox)
		groupBox.setLayout(vBox)

		return groupBox


	def sideSettingsPanel(self):
		###Dynamically changing settings panel###
		settingsPanel = QVBoxLayout()

		settingsTitle = CommonUI.labelCell("Settings", color='black', size=15)

		resultsTitle = CommonUI.labelCell("Results", color='black', size=15)
		distortionList = CommonUI.labelCell("Distortion Factor", color='black', size=12)
		self.distortionsLabel = CommonUI.labelCell("Start Test To Get Results!", color='black', size=10)

		xSliderBox, self.xSliderCrop = self.createSliderWithLabel(0, 1000, 'Center Circle X',
		                                                          initialVal=self.settingsSaver.cropArea['x'])
		ySliderBox, self.ySliderCrop = self.createSliderWithLabel(0, 1000, 'Center Circle Y',
		                                                          initialVal=self.settingsSaver.cropArea['y'])
		wSliderBox, self.wSliderCrop = self.createSliderWithLabel(0, 1000, 'Radius Inner Circle',
		                                                          initialVal=self.settingsSaver.cropArea['w'])
		hSliderBox, self.hSliderCrop = self.createSliderWithLabel(0, 1000, 'Radius Outer Circle',
		                                                          initialVal=self.settingsSaver.cropArea['h'])

		cropGroup = self.createSliderGroup('Crop Image', [xSliderBox,ySliderBox, wSliderBox, hSliderBox])

		completeCircleBox, self.completeCircleSlider = self.createSliderWithLabel(1,6, 'n', initialVal=self.settingsSaver.numberOfCircles)

		circleGroup = self.createSliderGroup('Number of Circles', [completeCircleBox])

		settingsPanel.addWidget(settingsTitle)
		settingsPanel.addWidget(cropGroup)
		settingsPanel.addWidget(circleGroup)

		settingsPanel.addWidget(resultsTitle)
		settingsPanel.addWidget(distortionList)
		settingsPanel.addWidget(self.distortionsLabel)

		settingsPanel.addStretch()

		settingsFrame = CommonUI.whiteQFrame()
		settingsFrame.setLayout(settingsPanel)
		return settingsFrame


	def mainInfoPanel(self):

		infoPanel = QVBoxLayout()

		testLabel = CommonUI.labelCell("Detected Points", color='black', size=12)

		self.cameraImage = QLabel()
		self.cameraImage2 = QLabel()

		infoPanel.addWidget(testLabel)
		infoPanel.addWidget(self.cameraImage2)
		infoPanel.addWidget(self.cameraImage)
		infoPanel.addStretch()


		self.nextButtonStep1 = QPushButton("Start Test")
		infoPanel.addWidget(self.nextButtonStep1)

		infoFrame = CommonUI.whiteQFrame()
		infoFrame.setLayout(infoPanel)

		return infoFrame

	def step_1(self):
		#align the mirror so that the diagram is in full view

		#Settings menu
		pass

	def step_2(self):
		#snap a photo to snap a photo
		pass





