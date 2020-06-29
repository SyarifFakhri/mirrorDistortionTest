import sys
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QGridLayout, QWidget, QPushButton, QVBoxLayout, \
		QHBoxLayout, QScrollArea, QSlider, QLineEdit, QFrame, QFileDialog
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QRect
from PyQt5.QtGui import QImage, QPixmap
from settingsSaver import SettingsSaver
from testRunner import TestRunner
import time
from datetime import datetime
import math

import os
import numpy as np
import csv

import qtmodern.styles
import qtmodern.windows

from mainWindow import MainWindow

import cv2

class MasterWindow(QMainWindow):
		def __init__(self, app):
			super(MasterWindow, self).__init__()
			self.setWindowTitle("Distortion Tester")
			self.mainWindow = MainWindow()

			self.processingThread = QThread()
			self.processingThread.start()

			self.settingsSaver = SettingsSaver()

			self.testRunner = TestRunner(self.settingsSaver)
			self.testRunner.moveToThread(self.processingThread)
			self.testRunner.startImageLoop.emit()

			app.aboutToQuit.connect(self.onClose)

			self.showMainWindow()

		@pyqtSlot()
		def onClose(self):
			print("Good bye")
			self.settingsSaver.saveAllSettings()
			self.processingThread.quit()

		###MAIN WINDOW FUNCTIONS START
		def updateCropArea(self):
			self.settingsSaver.cropArea['x'] = self.mainWindow.xSliderCrop.value()
			self.settingsSaver.cropArea['y'] = self.mainWindow.ySliderCrop.value()
			self.settingsSaver.cropArea['w'] = self.mainWindow.wSliderCrop.value()
			self.settingsSaver.cropArea['h'] = self.mainWindow.hSliderCrop.value()

		def updateNumberOfCircles(self):
			self.settingsSaver.numberOfCircles = self.mainWindow.completeCircleSlider.value()

		@pyqtSlot(QImage)
		def updateCameraImage(self, image):
			self.mainWindow.cameraImage.setPixmap(QPixmap.fromImage(image))

		@pyqtSlot(QImage)
		def setProccessedPixmap(self, image):
			self.mainWindow.cameraImage2.setPixmap(QPixmap.fromImage(image))

		@pyqtSlot(list)
		def updateDistortionStats(self, list):
			distortionStr = ''
			for index, stat in enumerate(list):
				maxVar = '{:.2f}'.format(stat[0])
				minVar = '{:.2f}'.format(stat[1])
				avgVar = '{:.2f}'.format(stat[2])
				distortionStr += 'Circle ' + str(index) + ': ' + avgVar + '%' +'\n'

			self.mainWindow.distortionsLabel.setText(distortionStr)

		def proceedPrevStep(self):
			# if self.testRunner.currentTestStep == 'starting_step':
			# 	self.mainWindow.nextButtonStep1.setText('Get result')
			# 	self.testRunner.currentTestStep = 'step_1'

			if self.testRunner.currentTestStep == 'step_1':
				self.mainWindow.nextButtonStep1.setText('Start Test')
				self.testRunner.currentTestStep = 'starting_step'

			elif self.testRunner.currentTestStep == 'result_step':
				self.mainWindow.nextButtonStep1.setText('Get Result')
				self.testRunner.currentTestStep = 'step_1'

			elif self.testRunner.currentTestStep == 'done_step':
				self.mainWindow.nextButtonStep1.setText('Get Result')
				self.testRunner.currentTestStep = 'step_1'


		def proceedToNextStep(self):
			if self.testRunner.currentTestStep == 'starting_step':
				self.mainWindow.nextButtonStep1.setText('Get result')
				self.testRunner.currentTestStep = 'step_1'

			elif self.testRunner.currentTestStep == 'step_1':
				self.mainWindow.nextButtonStep1.setText('Export Excel')
				self.testRunner.currentTestStep = 'result_step'

			elif self.testRunner.currentTestStep == 'result_step':
				self.testRunner.saveLocation = self.getFileLocation()[0]
				self.mainWindow.nextButtonStep1.setText('Start Test')
				self.testRunner.currentTestStep = 'done_step'

			# elif self.testRunner.currentTestStep == 'done_step':
			# 	self.mainWindow.nextButtonStep1.setText('Start Test')
			# 	self.testRunner.currentTestStep = 'starting_step'

			self.settingsSaver.saveAllSettings()

		def getFileLocation(self):
			dlg = QFileDialog()
			dlg.setFileMode(QFileDialog.Directory)
			dlg.setAcceptMode(QFileDialog.AcceptSave)
			currentTime = datetime.now()
			dateTimeStr = 'Report_Distortion_' + currentTime.strftime("%d_%m_%Y_%H_%M_%S")
			pathFileName = dlg.getSaveFileName(self, 'Save File Location', dateTimeStr + '.xlsx')
			return pathFileName

		def showMainWindow(self):
			mw = qtmodern.windows.ModernWindow(self)
			self.mainWindow.init_ui(self, self.settingsSaver)
			self.mainWindow.nextButtonStep1.clicked.connect(self.proceedToNextStep)

			self.mainWindow.xSliderCrop.valueChanged.connect(self.updateCropArea)
			self.mainWindow.ySliderCrop.valueChanged.connect(self.updateCropArea)
			self.mainWindow.wSliderCrop.valueChanged.connect(self.updateCropArea)
			self.mainWindow.hSliderCrop.valueChanged.connect(self.updateCropArea)
			self.mainWindow.completeCircleSlider.valueChanged.connect(self.updateNumberOfCircles)

			self.testRunner.retrievedImage.connect(self.updateCameraImage)
			self.testRunner.processedImageSig.connect(self.setProccessedPixmap)
			self.testRunner.distortionStats.connect(self.updateDistortionStats)
			mw.show()
			# self.show()

		###MAIN WINDOW FUNCTIONS END###

if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	masterWindow = MasterWindow(app)


	sys.exit(app.exec_())
	# app.exec()