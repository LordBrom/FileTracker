import sublime
import sublime_plugin
import os.path
import subprocess
import functools
import datetime
from ftFile import ftFile

class ftProject(ftFile):
	def getProject(self, projectName):

		projects = self.getProjects()

		for project in projects:
			if project["projectName"] == projectName:
				return project

		return ""

	def getProjects(self):
		ftProjectSettings = sublime.load_settings('ftProjects.sublime-settings')

		if not ftProjectSettings.has('ftProjects'):
			ftProjectSettings.set('ftProjects', [])
			sublime.save_settings('ftProjects.sublime-settings')

		return ftProjectSettings.get('ftProjects')

	def getProjectNames(self):
		projects = self.getProjects()

		names = []

		for project in projects:
			names.append(project["projectName"])

		return names

	def addProject(self, projectName):
		ftProjectSettings = sublime.load_settings('ftProjects.sublime-settings')
		if not ftProjectSettings.has('ftProjects'):
			ftProjectSettings.set('ftProjects', [])
			sublime.save_settings('ftProjects.sublime-settings')

		ftProjects = ftProjectSettings.get('ftProjects');

		projectFound = 0

		for Project in list(ftProjects):
			if Project["projectName"] == projectName:
				projectFound = Project
				ftProjects.remove(Project)

		if projectFound == 0:
			newProject = self.newProject(projectName)
		else:
			newProject = projectFound

		ftProjects.reverse()
		ftProjects.append(newProject)
		ftProjects.reverse()

		ftProjectSettings.set("ftProjects", ftProjects)
		sublime.save_settings('ftProjects.sublime-settings')

	def newProject(self, name):
		newProject = {
			"projectName" : name,
			"fileList" : []
		}

		return newProject

	def addFileToProject(self, project, fileName, filePath):
		projectName = project["projectName"]
		ftProjectSettings = sublime.load_settings('ftProjects.sublime-settings')

		if not ftProjectSettings.has('ftProjects'):
			ftProjectSettings.set('ftProjects', [])
			sublime.save_settings('ftProjects.sublime-settings')

		ftProjects = ftProjectSettings.get('ftProjects');

		projectFound = 0
		
		for Project in list(ftProjects):
			if Project["projectName"] == projectName:
				projectFound = Project
				ftProjects.remove(Project)

		if projectFound == 0:
			# error: project not found :C
			return
		else:
			newProject = self.addFile(projectFound, fileName, filePath)

		ftProjects.reverse()
		ftProjects.append(newProject)
		ftProjects.reverse()

		ftProjectSettings.set("ftProjects", ftProjects)
		sublime.save_settings('ftProjects.sublime-settings')
	
	def renameProject(self, projectName, newProjectName):
		ftProjectSettings = sublime.load_settings('ftProjects.sublime-settings')
		if not ftProjectSettings.has('ftProjects'):
			ftProjectSettings.set('ftProjects', [])
			sublime.save_settings('ftProjects.sublime-settings')

		ftProjects = ftProjectSettings.get('ftProjects');

		projectFound = 0

		for Project in list(ftProjects):
			if Project["projectName"] == projectName:
				Project["projectName"] = newProjectName
				projectFound = 1

		if projectFound == 0:
			# error: project not found :C
			return

		ftProjectSettings.set("ftProjects", ftProjects)
		sublime.save_settings('ftProjects.sublime-settings')

	def deleteProject(self, projectName):
		ftProjectSettings = sublime.load_settings('ftProjects.sublime-settings')
		if not ftProjectSettings.has('ftProjects'):
			ftProjectSettings.set('ftProjects', [])
			sublime.save_settings('ftProjects.sublime-settings')

		ftProjects = ftProjectSettings.get('ftProjects');

		projectFound = 0

		for Project in list(ftProjects):
			if Project["projectName"] == projectName:
				ftProjects.remove(Project)
				projectFound = 1

		if projectFound == 0:
			# error: project not found :C
			return

		if self.getActiveProject() == projectName:
			self.setActiveProject("")

		ftProjectSettings.set("ftProjects", ftProjects)
		sublime.save_settings('ftProjects.sublime-settings')

	def getProjectFileFieldList(self, projectName, fileField):
		project = self.getProject(projectName)

		if project == "":
			return
		else:
			fileFieldList = self.getFileFieldList(project, fileField)

			return fileFieldList

	def removeFileFromProject(self, project, filePath):
		projectName = project["projectName"]
		ftProjectSettings = sublime.load_settings('ftProjects.sublime-settings')

		if not ftProjectSettings.has('ftProjects'):
			ftProjectSettings.set('ftProjects', [])
			sublime.save_settings('ftProjects.sublime-settings')

		ftProjects = ftProjectSettings.get('ftProjects', []);

		projectFound = 0
		
		for Project in list(ftProjects):
			if Project["projectName"] == projectName:
				projectFound = Project
				ftProjects.remove(Project)
				break

		if projectFound == 0:
			# error: project not found :C
			return
		else:
			newProject = self.deleteFile(projectFound, filePath)

		ftProjects.reverse()
		ftProjects.append(newProject)
		ftProjects.reverse()

		ftProjectSettings.set("ftProjects", ftProjects)
		sublime.save_settings('ftProjects.sublime-settings')

	def checkFileInProject(self, project, filePath):
		return self.containsFile(project, filePath)