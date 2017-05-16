import sublime
import sublime_plugin
import os.path
import subprocess
import functools
import datetime

class ftFile():
	def addFile(self, project, fileName, filePath):
		fileFound = 0

		fileList = project["fileList"]

		if fileList == None:
			fileList = []

		for file in fileList:
			if file["fileName"] == fileName:
				file["lastModified"] = str(datetime.datetime.now())
				fileFound = file
				fileList.remove(file)
				break

		if fileFound == 0:
			fileFound = self.newFile(fileName, filePath)
		
		fileList.append(fileFound)

		return project

	def newFile(self, fileName, filePath):
		newFile = {
			"fileName" : fileName,
			"filePath" : filePath,
			"firstAdded" : str(datetime.datetime.now()),
			"lastModified" : str(datetime.datetime.now())
		}

		return newFile

	def getFiles(self, project):
		print('')

	def deleteFiles(self, project):
		project["fileList"] = []

		return project

	def deleteFile(self, project, filePath):
		fileFound = 0

		fileList = project["fileList"]

		if fileList == None:
			fileList = []

		for file in fileList:
			if file["filePath"] == filePath:
				fileList.remove(file)
				break

		project["fileList"] = fileList

		return project

	def getFileFieldList(self, project, fileField):
		result = []
		fileList = project["fileList"]

		for file in fileList:
			result.append(file[fileField])

		return result

