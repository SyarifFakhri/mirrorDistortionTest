from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QRect
from PyQt5.QtWidgets import QApplication
from settingsSaver import SettingsSaver
from PyQt5.QtGui import QImage, QPixmap
import cv2
import numpy as np
import xlsxwriter
import time
import math
import datetime
import os

class TestRunner(QtCore.QObject):
	retrievedImage = pyqtSignal(QImage)
	processedImageSig= pyqtSignal(QImage)

	distortionStats = pyqtSignal(list)

	startImageLoop = pyqtSignal()

	def __init__(self, settingsSaver):
		super(TestRunner, self).__init__()
		self.settingsSaver = settingsSaver
		self.cap = cv2.VideoCapture(self.settingsSaver.cameraInput)
		self.cap.set(3, 1280)  # width
		self.cap.set(4, 720)  # height
		self.saveLocation = 'report.xslx'

		#call show image loop

		self.startImageLoop.connect(self.mainTestLoop)
		self.currentTestStep = 'starting_step'
		self.testSteps = {
			'starting_step': 'starting_step',
			'step_1': 'step_1',
			'result_step': 'result_step',
			'done_step': 'done_step'
		}

	@pyqtSlot()
	def convertToQTFormat(self, image):
		rgbImage = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
		h, w, ch = rgbImage.shape
		bytesPerLine = ch * w
		convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
		rawImg = convertToQtFormat.scaled(h, w, Qt.KeepAspectRatio)
		return rawImg

	@pyqtSlot()
	def mainTestLoop(self):
		self.currentTestStep = 'starting_step'
		prevImg = None

		while True:
			if self.currentTestStep == self.testSteps['starting_step']:
				ret, img = self.cap.read()
				h,w,c = img.shape
				# print("HEIGHT: " + str(h) + "WIDTH:" + str(w))

				self.retrievedImage.emit(self.convertToQTFormat(img))

			elif self.currentTestStep == self.testSteps['step_1']:
				ret, img = self.cap.read()
				prevImg = img.copy()
				self.processImageAndGetPoints(img)

			elif self.currentTestStep == self.testSteps['result_step']:
				# ret, img = self.cap.read()
				if prevImg is None:
					continue
				# rawImg = prevImg.copy()
				newImage = prevImg.copy()
				groupedPoints, percentDistortion = self.processImageAndGetPoints(newImage, emitDistortion=True)


			elif self.currentTestStep == self.testSteps['done_step']:
				if prevImg is None:
					continue

				newImage = prevImg.copy()
				groupedPoints, percentDistortion = self.processImageAndGetPoints(newImage)

				self.exportToExcel(groupedPoints, percentDistortion, prevImg, newImage)

				self.currentTestStep = self.testSteps['starting_step']

			else:
				print("Current Step is: ", self.currentTestStep)
				# raise Exception("Current step is not included in the possible test steps")

	def processImageAndGetPoints(self, img, emitDistortion=False):
		x = self.settingsSaver.cropArea['x']
		y = self.settingsSaver.cropArea['y']
		w = self.settingsSaver.cropArea['w']
		h = self.settingsSaver.cropArea['h']

		# overLay = self.createOverlay(x, y, w, h, img.shape[1], img.shape[0])
		overlay = self.createOverlayCircles(x,y,w,h, img.shape[1], img.shape[0])
		corners, processedImage = self.detectCornersInImage(img, mask=overlay)

		if corners is None:
			return

		centroid = self.getCenterOfMassOfPoints(corners)[0]
		sortedPoints = self.sortCornersFromDistanceToCenter(corners, centroid)
		groupedPoints = self.groupPointsAccordingToDist(sortedPoints, groupSize=8)
		groupedPoints = self.takeNCirclesFromSettings(groupedPoints)

		self.showGroupedPoints(img, groupedPoints)
		self.connectGroupedPoints(img, groupedPoints)

		percentDistortion = self.getDistortion(groupedPoints)
		if emitDistortion:
			self.distortionStats.emit(percentDistortion)

		cv2.circle(img, (int(centroid[0]), int(centroid[1])), 5, (0, 0, 255), -1)
		cv2.putText(img, "Detected Points", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255))

		img = self.overlay2Images(img, overlay)

		self.retrievedImage.emit(self.convertToQTFormat(img.copy()))
		return groupedPoints, percentDistortion

	def takeNCirclesFromSettings(self, groupedPoints):
		return groupedPoints[0:int(self.settingsSaver.numberOfCircles)]

	def connectGroupedPoints(self, image, groupedPoints):
		for group in groupedPoints:
			xyPoints = np.delete(group, -1, 1).astype(np.float32) #delete distance calculation
			xyPoints = cv2.convexHull(xyPoints)
			if xyPoints is None:
				continue

			xyPoints = xyPoints.astype(np.int32)
			# pts = np.array([[10, 5], [20, 30], [70, 20], [50, 10]], np.int32)
			xyPoints = xyPoints.reshape((-1, 1, 2))
			cv2.polylines(image, [xyPoints], True, (0,0,255), thickness=1)


	def getDistortion(self, groupedPoints):
		distortionList = []

		for group in groupedPoints:
			if len(group) == 0:
				continue
			maxDistInGroup = max([p[2] for p in group]) #get the max distance of the 3rd column (the distance column)
			minDistInGroup = min([p[2] for p in group]) #get the min distance of the 3rd column (the distance column)
			average = np.mean([p[2] for p in group])
			maxVariancePercent = abs(((maxDistInGroup - average) / average) * 100)
			minVariancePercent = abs(((minDistInGroup - average) / average) * 100)
			averageMaxAndMin = (maxVariancePercent + minVariancePercent) / 2

			distortionList.append([maxVariancePercent, minVariancePercent, averageMaxAndMin])

		return distortionList

	def overlay2Images(self, image1, image2, opacity=0.5):
		added_image = cv2.addWeighted(image1, opacity, image2, 0.1, 0)
		return added_image

	def createOverlayRectangle(self,x,y,w,h, imageWidth, imageHeight):
		blank_image = np.zeros((imageHeight, imageWidth,3), np.uint8)
		cv2.rectangle(blank_image, (x,y), (x+w,y+h),(255,255,255), -1)
		return blank_image

	def createOverlayCircles(self, cx, cy, rInner, rOuter, imageWidth, imageHeight):
		blank_image = np.zeros((imageHeight, imageWidth, 3), np.uint8)
		cv2.circle(blank_image, (cx, cy), rOuter, (255, 255, 255), -1)
		cv2.circle(blank_image, (cx, cy), rInner, (0, 0, 0), -1)
		return blank_image

	def exportToExcel(self, groupedPoints,distortionList, rawImage,processedImage):
		workbook = xlsxwriter.Workbook(self.saveLocation)
		worksheet = workbook.add_worksheet()

		worksheet.set_column(0,1,3)

		titleFormat = workbook.add_format({
			'bold': 1,
			# 'border': 1,
			'align': 'center',
			'valign': 'vcenter'})
			# 'fg_color': 'yellow'})

		worksheet.merge_range('A1:N1', 'MIRROR DISTORTION MEASUREMENT', titleFormat)

		boldFormat = workbook.add_format({
			'bold': 1,
			'align': 'left',
			'valign': 'vcenter'})

		worksheet.merge_range('A3:G3', 'Concentric Circle Image Measurement', boldFormat)
		worksheet.merge_range('A4:D4', 'Complete Circle: ', boldFormat)
		worksheet.write('E4', str(len(groupedPoints)))

		worksheet.write('F3', "Date: ")
		worksheet.write('G3', str(datetime.datetime.now()))

		tableFormat = workbook.add_format({
			'bold': 1,
			'border': 1,
			'align': 'center',
			'valign': 'vcenter'})

		worksheet.merge_range('C6:J6', 'Radius (pixel)', tableFormat)
		worksheet.write('C7', 'a', tableFormat)
		worksheet.write('D7', 'b', tableFormat)
		worksheet.write('E7', 'c', tableFormat)
		worksheet.write('F7', 'd', tableFormat)
		worksheet.write('G7', 'e', tableFormat)
		worksheet.write('H7', 'f', tableFormat)
		worksheet.write('I7', 'g', tableFormat)
		worksheet.write('J7', 'h', tableFormat)
		worksheet.merge_range('K7:L7', 'Average', tableFormat)
		worksheet.write('M7', 'Min', tableFormat)
		worksheet.write('N7', 'Max', tableFormat)

		cellFormat = workbook.add_format({
			# 'bold': 1,
			'border': 1,
			'align': 'center',
			'valign': 'vcenter'})

		cellCyanFormat = workbook.add_format({
			# 'bold': 1,
			'fg_color':'#BCFFFF',
			'border': 1,
			'align': 'center',
			'valign': 'vcenter'})

		row = 7
		index = 1
		for group in groupedPoints:
			if group == []:
				continue
			column = 1
			worksheet.write(row, column, str(index), cellFormat)
			for point in group:
				column += 1
				worksheet.write(row, column, '{:.2f}'.format(point[2]), cellFormat)

			maxDistInGroup = max([p[2] for p in group])  # get the max distance of the 3rd column (the distance column)
			minDistInGroup = min([p[2] for p in group])  # get the min distance of the 3rd column (the distance column)
			average = np.mean([p[2] for p in group])

			column += 1
			worksheet.merge_range(row, column, row, column+1, '{:.2f}'.format(average), cellCyanFormat)
			column += 2
			worksheet.write(row, column, '{:.2f}'.format(minDistInGroup), cellCyanFormat)
			column += 1
			worksheet.write(row, column, '{:.2f}'.format(maxDistInGroup), cellCyanFormat)

			row += 1
			index += 1

		rotatedFormat = workbook.add_format({
			'bold': 1,
			'border': 1,
			'align': 'center',
			'valign': 'vcenter',
			'rotation': 90})

		# worksheet.merge_range(7, 0, row-1, 0, 'Circle', rotatedFormat)
		self.attemptToWriteMerged(worksheet, 7,0,row-1, 0, 'Circle', rotatedFormat, boldFormat)


		row += 1
		#Write results
		worksheet.merge_range(row, 0, row, 4, 'Distortion Result', boldFormat)
		# worksheet.write('A15', 'Circle')
		row += 2
		worksheet.merge_range(row, 2,row, 5, 'Variance, % (Max)', tableFormat)
		worksheet.merge_range(row, 6, row, 9, 'Variance, % (Min)', tableFormat)
		worksheet.merge_range(row, 10, row, 13, 'Variance Average, %', tableFormat)

		row += 1
		index = 1

		# worksheet.merge_range(row, 0, row + len(distortionList) - 1, 0, 'Circle', rotatedFormat)
		self.attemptToWriteMerged(worksheet, row,0, row + len(distortionList) - 1, 0, 'Circle', rotatedFormat, boldFormat)
		for results in distortionList:
			column = 1
			worksheet.write(row, column, str(index), cellFormat)
			column += 1
			for res in results:
				worksheet.merge_range(row, column, row, column + 3,'{:.2f}'.format(res), cellCyanFormat)
				column += 4

			row += 1
			index += 1

		row += 2

		boldCenteredFormat = workbook.add_format({
			'bold': 1,
			'border': 1,
			'align': 'center',
			'valign': 'vcenter'})

		boldCenteredYellowFormat = workbook.add_format({
			'bold': 1,
			'border': 1,
			'align': 'center',
			'valign': 'vcenter',
			'fg_color': 'yellow'})

		averageDistortion =  [v[2] for v in distortionList]
		worksheet.merge_range(row, 0, row, 5,"AVERAGE DISTORTION, %", boldCenteredFormat)
		worksheet.merge_range(row, 6, row, 13, str(np.mean(averageDistortion)), boldCenteredYellowFormat)


		# processedImage = cv2.resize(processedImage, (int(1280/2),int(720/2))
		baseName = self.getSaveLocationBaseName()

		processedImgStr = baseName + "_Processed_Image.png"
		rawImgStr = baseName + "_Raw_Image.png"

		cv2.imwrite(processedImgStr, processedImage)
		cv2.imwrite(rawImgStr, rawImage)

		worksheet.insert_image('P7', processedImgStr, {'x_scale': 0.5, 'y_scale': 0.5})
		worksheet.insert_image('P25', rawImgStr, {'x_scale': 0.5, 'y_scale': 0.5})

		workbook.close()

	def getSaveLocationBaseName(self):
		return os.path.splitext(self.saveLocation)[0]

	def attemptToWriteMerged(self, worksheet,firstRow, firstCol, lastRow, lastCol, text, rotatedFormat, boldFormat):
		if firstRow == lastRow:
			worksheet.write(firstRow, firstCol, text, boldFormat)
		else:
			worksheet.merge_range(firstRow, firstCol, lastRow, lastCol, text, rotatedFormat)


	def cropImageFromSettings(self, image):
		x = self.settingsSaver.cropArea['x']
		y = self.settingsSaver.cropArea['y']
		w = self.settingsSaver.cropArea['w']
		h = self.settingsSaver.cropArea['h']

		cropped = image[y:y+h, x:x+w]

		return cropped

	def getCenterOfMassOfPoints(self, corners):
		return corners.mean(axis=0)

	def showGroupedPoints(self,image, groupedCornerPoints):
		colorArray = [
			# (255,0,0), #b
			# (0,255,0), #g
			# (0,0,255), #r
			(0,255,0),
			(255,255,0),
			(255,0,255),
			(0,255,255),
			(255,127,0),
			(127,255,0),
			(255,0,127),
			(127,0,255),
			(127,0,0),
			(0,127,0),
			(0,0,127),
		]
		for i, group in enumerate(groupedCornerPoints):
			for coordinate in group:
				color = colorArray[i] if len(colorArray) > i else (255,255,127) #getting the color while avoiding an out of index error
				cv2.circle(image, (int(coordinate[0]), int(coordinate[1])), 4, color, -1)

	def groupPointsAccordingToDist(self, sortedCornerPoints,groupSize):
		"""
		The idea is really simple, take the n closest points to the center, then the next n, then the next n etc

		In that way you should have a group of n points
		"""
		groupedPoints = []
		length = len(sortedCornerPoints)
		divisory = length // groupSize
		for i in range((len(sortedCornerPoints) // groupSize) + 1):
			startingGroupIndex = i*groupSize
			endingGroupIndex = startingGroupIndex + groupSize
			groupedPoints.append(sortedCornerPoints[startingGroupIndex:endingGroupIndex])

		return groupedPoints



	def sortCornersFromDistanceToCenter(self, corners, center):
		# print(corners)
		# print(center)
		pointsWithDist = []
		for corner in corners:
			res = np.sqrt(np.sum((corner - center) ** 2))
			cornerPointWithDist = np.append(corner,res) #array will look like [x,y,dist]
			pointsWithDist.append(cornerPointWithDist)

		pointsWithDist = np.array(pointsWithDist)
		sortedPoints = pointsWithDist[pointsWithDist[:,2].argsort()] # sort according to last axis aka distance
		return sortedPoints

	def detectCornersInImage(self, img, mask=None):
		gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
		# gray_blur = cv2.medianBlur(gray, 3)
		# eqHist = cv2.equalizeHist(gray)
		# ret, grayThresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

		# kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
		# gray_sharp = cv2.filter2D(gray_blur, -1, kernel)

		gray = np.float32(gray)

		gray_mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
		ret, binaryMask = cv2.threshold(gray_mask, 0,255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

		corners = cv2.goodFeaturesToTrack(gray, 48, 0.01, 10, blockSize=5, mask=binaryMask, useHarrisDetector=True)#, gradientSize=3)

		if corners is None:
			return corners, gray

		criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.001)

		# print(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER)
		corners = cv2.cornerSubPix(gray, np.float32(corners), (5, 5), (-1, -1), criteria)

		corners = np.int0(corners)

		# for i in corners:
		# 	x,y = i.ravel()
		# 	cv2.circle(img,(x,y),3,255,-1)

		return corners, np.uint8(gray)

