
from tinydb import TinyDB, Query

class SettingsSaver:
	def __init__(self):
		self.settingsDB = TinyDB('settings.json')
		allSettings = self.settingsDB.get(doc_id=1)

		# self.initDB()
		self.cameraInput = int(allSettings['camera'])
		self.cropArea = allSettings['crop_area']
		self.numberOfCircles = allSettings['num_circles']
		print(self.numberOfCircles)

	def saveAllSettings(self):
		self.saveCropArea()
		self.saveNumberOfCircles()

	def saveNumberOfCircles(self):
		self.settingsDB.update({'num_circles': self.numberOfCircles}, doc_ids=[1])

	def saveCropArea(self):
		# self.settingsDB.update({
		# 	'crop_area': {'x':x,'y':y, 'w':w, 'h':h},
		# }, doc_ids=[1])
		self.settingsDB.update({'crop_area': self.cropArea}, doc_ids=[1])

	def initDB(self):
		self.settingsDB.update({
			'num_circles': 5,
			'camera': '0', #actually camera index
			'crop_area': {'x':0,'y':0, 'w':100, 'h':100},
		},doc_ids=[1])