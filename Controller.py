#!/usr/bin/env python
'''
Apache Web Developer Controller
Written by @kennydude
Written for Ubuntu 10.10
(probably won't work at all on anything else!)
'''
print "Welcome to Apache Wed Developer Controller"
print "Created by @kennydude"
print "------------"
print "MUST BE RAN AS ROOT ON UBUNTU!"
print "pygtk is required"
print "------------"
print ""
# import stuff!
import sys, os, fnmatch, time, re
import subprocess
try:
 	import pygtk
  	pygtk.require("2.0")
except:
  	pass
try:
	import gtk
except:
	sys.exit(1)
def responseToDialog(x,d,r):
	d.response(r)
# window
class ControllerWindow:
	def inputBox(self, primary, secondary, label): # Todo: get link of bar and copy (c&p being a dick)
		#base this on a message dialog
		dialog = gtk.MessageDialog(
			None,
			gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
			gtk.MESSAGE_QUESTION,
			gtk.BUTTONS_OK,
			None)
		dialog.set_markup('<b>%s</b>' % primary)
		#create the text input field
		entry = gtk.Entry()
		#allow the user to press enter to do ok
		entry.connect("activate", responseToDialog, dialog, gtk.RESPONSE_OK)
		#create a horizontal box to pack the entry and a label
		hbox = gtk.HBox()
		hbox.pack_start(gtk.Label(label), False, 5, 5)
		hbox.pack_end(entry)
		#some secondary text
		dialog.format_secondary_markup(secondary)
		#add it and show it
		dialog.vbox.pack_end(hbox, True, True, 0)
		dialog.show_all()
		#go go go
		dialog.run()
		text = entry.get_text()
		dialog.destroy()
		return text
	def call(self, app):
		self.window.set_sensitive(False)
		print "> " + str(app)
		r = subprocess.Popen(app.split(" "), stdout=subprocess.PIPE).communicate()[0]
		print r
		self.window.set_sensitive(True)
		return r
	def refresh(self):
		# 1: Apache Running
		apache_status = self.call('service apache2 status')
		status_widget = self.wTree.get_object("ApacheStatus")
		flippy_button = self.wTree.get_object("ApacheStatusButton")
		if "NOT" not in apache_status:
			self.apache_running = True
			flippy_button.set_label("Stop")
			status_widget.set_text("Apache is running")
		else:	
			self.apache_running = False
			flippy_button.set_label("Start")
			status_widget.set_text("Apache is not running")
		# 2: Apache Launch on Boot
		self.apache_onstartup = True
		if len(fnmatch.filter(os.listdir('/etc/rc1.d'), "*apache2")) == 0:
			self.apache_onstartup = False
		startup_switch = self.wTree.get_object("ApacheAutostart")
		self.kill_se = True
		startup_switch.set_active(self.apache_onstartup)
		self.kill_se = False
		# 3: Read hosts
		hfile = open('/etc/hosts', 'r')
		tag = False
		hosts = []
		for hline in hfile:
			if hline == "#AWDC-kennydude AUTOGEN\n":
				tag = True
			elif tag == True:
				tag = False
				hosts.append(hline.split("\n")[0].split("\t")[1])
		self.hostList.clear()
		for host in hosts:
			self.hostList.append([host])
	def changeApacheStatus(self, x):
		if self.apache_running:
			self.call('service apache2 stop')
		else:
			self.call('service apache2 start')
		self.refresh()
	def changeAutostart(self, x):
		if self.kill_se:
			return
		if self.apache_onstartup:
			self.call('update-rc.d -f apache2 remove')
		else:
			self.call('update-rc.d apache2 defaults')
		self.refresh()
	def readHosts(self):
		hfile = open('/etc/hosts', 'r')
		h = hfile.readlines()
		hfile.close()
		return h
	def addNewHost(self, x):
		i = self.inputBox("New host", "Enter the address you wish Apache to handle on this computer", "Host: ")
		if not re.match("^[.A-Za-z]+$", i):
			print "Host invalid"
			return
		# write hosts
		h = self.readHosts()
		hfile = open('/etc/hosts', 'w')
		for line in h:
			hfile.write(line)
		hfile.write('\n#AWDC-kennydude AUTOGEN\n')
		hfile.write('127.0.0.1\t%s\n' % i)
		hfile.close()
		self.refresh()
	def removeHost(self, x):
		host_list = self.wTree.get_object("HostList")
		(tm, ti) = host_list.get_selection().get_selected()
		host_to_delete = tm[ti][0]
		h = self.readHosts()
		i = 0
		for line in h:
			if line[0] == "#" or line == "\n" or line == "":
				pass
			try:
				if line.split('\n')[0].split('\t')[1] == host_to_delete:
					del h[i]
					del h[i-1]
			except Exception:
				pass
			i+=1
		hfile = open('/etc/hosts', 'w')
		for line in h:
			hfile.write(line)
		hfile.close()
		self.refresh()
	def __init__(self):
		self.gladefile = "Window.ui"  
	        self.wTree = gtk.Builder()
		self.wTree.add_from_file(self.gladefile) 
		self.window = self.wTree.get_object("MainWindow")
		if (self.window):
			flippy_button = self.wTree.get_object("ApacheStatusButton")
			flippy_button.connect("clicked", self.changeApacheStatus)
			startup_switch = self.wTree.get_object("ApacheAutostart")
			startup_switch.connect("toggled", self.changeAutostart)
			host_list = self.wTree.get_object("HostList")
			column = gtk.TreeViewColumn("Host", gtk.CellRendererText(), text=0)
			column.set_resizable(True)
			column.set_sort_column_id(0)
			host_list.append_column(column)
			self.hostList = gtk.ListStore(str)
			host_list.set_model(self.hostList)
			add_button = self.wTree.get_object("AddNewHost")
			add_button.connect("clicked", self.addNewHost)
			remove_button = self.wTree.get_object("RemoveHost")
			remove_button.connect("clicked", self.removeHost)
			self.window.connect("destroy", gtk.main_quit)
		self.window.show()
		self.refresh()

if __name__ == "__main__":
	hwg = ControllerWindow()
	gtk.main()
