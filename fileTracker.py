import sublime
import sublime_plugin
import os.path
import subprocess
import functools
import datetime
from ftProject import ftProject

sublime.FT_CURRENT_PROJECT = ""

sublime.FT_ROJECT_MENU_ITEMS = ["Set active project", "List files...", "Rename project...", "Delete project..."]
sublime.FT_FILE_MENU_ITEMS = ["Open file", "Remove file..."]

sublime.FT_ATIVE_PROJECT = ""

class ftController(ftProject):
	def setActiveProject(self, name):
		sublime.FT_CURRENT_PROJECT = name
		sublime.FT_ATIVE_PROJECT = self.getProject(name)

		ftSettings = sublime.load_settings('Preferences.sublime-settings')
		ftSettings.set('ftActiveProject', name)
		sublime.save_settings('Preferences.sublime-settings')

		self.moveToFront(name)
		sublime.status_message("Active project set to: " + name)

	def getActiveProject(self):
		if sublime.FT_ATIVE_PROJECT == "":
			currentProjectName = sublime.FT_CURRENT_PROJECT

			if currentProjectName == "":
				ftSettings = sublime.load_settings('Preferences.sublime-settings')

				if not ftSettings.has('ftActiveProject'):
					ftSettings.set('ftActiveProject', "")
					sublime.save_settings('Preferences.sublime-settings')

				currentProjectName = ftSettings.get('ftActiveProject')

				sublime.FT_CURRENT_PROJECT = currentProjectName
				sublime.FT_ATIVE_PROJECT = self.getProject(currentProjectName)

		return sublime.FT_ATIVE_PROJECT

	def moveToFront(self, name):
		ftProjectSettings = sublime.load_settings('ftProjects.sublime-settings')
		if not ftProjectSettings.has('ftProjects'):
			ftProjectSettings.set('ftProjects', [])
			sublime.save_settings('ftProjects.sublime-settings')

		ftProjects = ftProjectSettings.get('ftProjects');

		projectFound = 0

		for Project in list(ftProjects):
			if Project["projectName"] == name:
				projectFound = Project
				ftProjects.remove(Project)

		if projectFound == 0:
			newProject = self.newProject(name)
		else:
			newProject = projectFound

		ftProjects.reverse()
		ftProjects.append(newProject)
		ftProjects.reverse()

		ftProjectSettings.set("ftProjects", ftProjects)
		sublime.save_settings('ftProjects.sublime-settings')



class ftAddFileToProjectOnSave(sublime_plugin.EventListener, ftController):
	def on_post_save(self, view):
		filepath = sublime.active_window().active_view().file_name()
		filename = filepath[(filepath.rfind('\\') + 1):]

		activeProject = self.getActiveProject()

		self.addFileToProject(activeProject, filename, filepath)



class ftListProjectsCommand(sublime_plugin.TextCommand, ftController):
	def run(self, edit):
		self.showProjectNames()

	def showProjectNames(self):
		self.projects = self.getProjectNames()
		# projectNames = self.projects["projectName"] 

		sublime.active_window().show_quick_panel(self.projects, self.showFile)

	def showFile(self, index):
		sublime.status_message("test")



class ftAddProjectCommand(sublime_plugin.TextCommand, ftController):
	def run(self, edit):
		#
		sublime.active_window().show_input_panel("Project name:", "", self.do_add, None, None) 

	def do_add(self, name):
		if name == "":
			return
		self.addProject(name)
		self.setActiveProject(name)



class ftSetActiveProjectCommand(sublime_plugin.TextCommand, ftController):
	def run(self, edit):
		self.projectNames = self.getProjectNames()
		self.projectNames.insert(min(len(self.projectNames), 1), 'New project...')
		sublime.active_window().show_quick_panel(self.projectNames, self.do_set)

	def do_set(self, index):
		if index == -1:
			return
		elif index == 1:
			sublime.active_window().run_command('ft_add_project')
		else:
			self.setActiveProject(self.projectNames[index])



class ftShowActiveProjectCommand(sublime_plugin.TextCommand, ftController):
	def run(self, edit):
		currentProject = self.getActiveProject()
		sublime.status_message(currentProject)



class ftRenameProjectCommand(sublime_plugin.TextCommand, ftController):
	def run(self, view):
		self.projectNames = self.getProjectNames()
		sublime.active_window().show_quick_panel(self.projectNames, self.get_name)

	def get_name(self, index):
		if index == -1:
			return
		else:
			self.oldName = self.projectNames[index]
			sublime.active_window().show_input_panel("enter new project name:", self.oldName, self.do_rename, None, None)

	def do_rename(self, newName):
		if newName == "":
			return
		else:
			self.renameProject(self.oldName, newName)


class ftListProjectFileListCommand(sublime_plugin.TextCommand, ftController):
	def run(self, view):
		self.activeProject = self.getActiveProject()
		filePathList = []

		for file in self.activeProject["fileList"]:
			filePathList.append(file["filePath"])

		sublime.active_window().show_quick_panel(filePathList, self.do_file_menu)


	def do_file_menu(self, index):
		self.selectedFileName = self.activeProject["fileList"][index]["fileName"]
		self.selectedFilePath = self.activeProject["fileList"][index]["filePath"]
		self.menuItems = list(sublime.FT_FILE_MENU_ITEMS)

		sublime.active_window().show_quick_panel(self.menuItems, self.do_action)

	def do_action(self, index):
		if index == -1:
			return
		elif self.menuItems[index] == "Open file":
			self.open_file()
		elif self.menuItems[index] == "Remove file...":
			self.deleteFile(self.activeProject, self.selectedFilePath)

	def open_file(self):
		if os.path.exists(self.selectedFilePath):
			sublime.active_window().run_command('open_file', {"file": self.selectedFilePath} )


class ftDeleteProjectCommand(sublime_plugin.TextCommand, ftController):
	def run(self, view):
		self.projectNames = self.getProjectNames()
		sublime.active_window().show_quick_panel(self.projectNames, self.do_confirm)

	def do_confirm(self, index):
		if index == -1:
			return
		else:
			self.selectedName = self.projectNames[index]
			sublime.active_window().show_quick_panel(list(["No, keep the project", "Yes, delete the project"]), self.do_delete)

	def do_delete(self, index):
		if index == -1:
			return
		elif index == 0:
			return
		else:
			self.deleteProject(self.selectedName)



class ftShowMainManuOldCommand(sublime_plugin.TextCommand, ftController):
	def run(self, edit):
		self.menuItems = list(sublime.FT_ROJECT_MENU_ITEMS)

		sublime.active_window().show_quick_panel(self.menuItems, self.do_action)

	def do_action(self, index):
		if index == -1:
			return
		elif self.menuItems[index] == "List projects...":
			sublime.active_window().run_command('ft_list_projects')

		elif self.menuItems[index] == "Add project...":
			sublime.active_window().run_command('ft_add_project')

		elif self.menuItems[index] == "Set active project...":
			sublime.active_window().run_command('ft_set_active_project')

		elif self.menuItems[index] == "Delete project...":
			sublime.active_window().run_command('ft_delete_project')

		elif self.menuItems[index] == "Rename project...":
			sublime.active_window().run_command('ft_rename_project')



class ftShowMainManuCommand(sublime_plugin.TextCommand, ftController):
	def run(self, edit):
		self.projects = self.getProjects()
		menuItems = []

		if len(self.projects) == 0:
			sublime.active_window().show_quick_panel(["Add new..."], self.do_add_new)
		else:
			first = 1
			for project in self.projects:
				menuItems.append(project["projectName"])
				if first == 1:
					menuItems.append("Add new...")
					first = 0

			sublime.active_window().show_quick_panel(menuItems, self.do_project_menu)

	def do_project_menu(self, index):
		if index == -1:
			return
		elif index == 0:
			self.selectedIndex = index
			self.selectedName = self.projects[self.selectedIndex]["projectName"]
			menuItems = list(sublime.FT_ROJECT_MENU_ITEMS)
			sublime.active_window().show_quick_panel(menuItems, self.do_action)
		elif index == 1:
			sublime.active_window().run_command('ft_add_project')
		else:
			self.selectedIndex = index - 1
			self.selectedName = self.projects[self.selectedIndex]["projectName"]
			menuItems = list(sublime.FT_ROJECT_MENU_ITEMS)
			sublime.active_window().show_quick_panel(menuItems, self.do_action)

	def do_add_new(self, index):
		if index == -1:
			return
		else:
			sublime.active_window().run_command('ft_add_project')

	def do_action(self, index):
		if index == -1:
			return
		
		elif sublime.FT_ROJECT_MENU_ITEMS[index] == "Set active project":
			self.setActiveProject(self.selectedName)
		
		elif sublime.FT_ROJECT_MENU_ITEMS[index] == "List files...":
			print('')
			# sublime.active_window().show_quick_panel(list(self.getProjectFileFieldList(self.selectedName, "filePath")), self.do_delete)
			sublime.active_window().run_command('ft_list_project_file_list')
		
		elif sublime.FT_ROJECT_MENU_ITEMS[index] == "Rename project...":
			sublime.active_window().show_input_panel("enter new project name:", self.selectedName, self.do_rename, None, None)
		
		elif sublime.FT_ROJECT_MENU_ITEMS[index] == "Delete project...":
			sublime.active_window().show_quick_panel(list(["No, keep the project", "Yes, delete the project"]), self.do_delete)

	def do_delete(self, index):
		if index == -1:
			return
		elif index == 0:
			return
		else:
			self.deleteProject(self.selectedName)

	def do_rename(self, newName):
		if newName == "":
			return
		else:
			self.renameProject(self.selectedName, newName)
