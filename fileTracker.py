import sublime
import sublime_plugin
import os.path
import subprocess
import functools
import datetime
from FileTracker.ftProject import ftProject

sublime.FT_CURRENT_PROJECT = ""

sublime.FT_MENU_ITEMS = ["Set active project", "List files...", "Rename project...", "Delete project..."]


class ftController(ftProject):
	def setActiveProject(self, name):
		sublime.FT_CURRENT_PROJECT = name

		ftSettings = sublime.load_settings('Preferences.sublime-settings')
		ftSettings.set('ftActiveProject', name)
		sublime.save_settings('Preferences.sublime-settings')

		self.moveToFront(name)
		sublime.status_message("Active project set to: " + name)

	def getActiveProject(self):
		currentProject = sublime.FT_CURRENT_PROJECT

		if currentProject == "":
			ftSettings = sublime.load_settings('Preferences.sublime-settings')

			if not ftSettings.has('ftActiveProject'):
				ftSettings.set('ftActiveProject', "")
				sublime.save_settings('Preferences.sublime-settings')

			currentProject = ftSettings.get('ftActiveProject')

		return currentProject

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
		windowDetails = sublime.active_window().extract_variables()
		fileName = windowDetails["file_base_name"] + "." + windowDetails["file_extension"]
		filePath = windowDetails["file"]
		self.addFileToProject(self.getActiveProject(), fileName, filePath)



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
		menuItems = list(sublime.FT_MENU_ITEMS)

		sublime.active_window().show_quick_panel(menuItems, self.do_action)

	def do_action(self, index):
		if index == -1:
			return
		elif sublime.FT_MENU_ITEMS[index] == "List projects...":
			sublime.active_window().run_command('ft_list_projects')
		elif sublime.FT_MENU_ITEMS[index] == "Add project...":
			sublime.active_window().run_command('ft_add_project')
		elif sublime.FT_MENU_ITEMS[index] == "Set active project...":
			sublime.active_window().run_command('ft_set_active_project')
		elif sublime.FT_MENU_ITEMS[index] == "Delete project...":
			sublime.active_window().run_command('ft_delete_project')
		elif sublime.FT_MENU_ITEMS[index] == "Rename project...":
			sublime.active_window().run_command('ft_rename_project')



class ftShowMainManuCommand(sublime_plugin.TextCommand, ftController):
	def run(self, edit):
		self.projects = self.getProjects()
		print("test")
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
			menuItems = list(sublime.FT_MENU_ITEMS)
			sublime.active_window().show_quick_panel(menuItems, self.do_action)
		elif index == 1:
			sublime.active_window().run_command('ft_add_project')
		else:
			self.selectedIndex = index - 1
			self.selectedName = self.projects[self.selectedIndex]["projectName"]
			menuItems = list(sublime.FT_MENU_ITEMS)
			sublime.active_window().show_quick_panel(menuItems, self.do_action)

	def do_add_new(self, index):
		if index == -1:
			return
		else:
			sublime.active_window().run_command('ft_add_project')

	def do_action(self, index):
		if index == -1:
			return
		elif sublime.FT_MENU_ITEMS[index] == "Set active project":
			self.setActiveProject(self.selectedName)
		elif sublime.FT_MENU_ITEMS[index] == "List files...":
			print('')
			# sublime.active_window().run_command('ft_list_projects')
		elif sublime.FT_MENU_ITEMS[index] == "Rename project...":
			print('')
			# sublime.active_window().run_command('ft_add_project')
		elif sublime.FT_MENU_ITEMS[index] == "Delete project...":
			sublime.active_window().show_quick_panel(list(["No, keep the project", "Yes, delete the project"]), self.do_delete)
		elif sublime.FT_MENU_ITEMS[index] == "Rename project...":
			sublime.active_window().run_command('ft_rename_project')

	def do_delete(self, index):
		if index == -1:
			return
		elif index == 0:
			return
		else:
			self.deleteProject(self.selectedName)
