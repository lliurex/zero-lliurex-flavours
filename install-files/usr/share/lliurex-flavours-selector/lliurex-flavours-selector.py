#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('PangoCairo', '1.0')

import cairo
import os
import glob
import threading
import configparser
import platform
import subprocess
import sys
import datetime
import copy
from math import pi

from gi.repository import Gtk, Gdk, GObject, GLib, PangoCairo, Pango

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)


import gettext
gettext.textdomain('zero-lliurex-flavours')
_ = gettext.gettext


BASE_DIR="/usr/share/lliurex-flavours-selector/"
RSRC_DIR=BASE_DIR+"rsrc/"
SHADOW_BANNER=RSRC_DIR+"shadow.png"
UNKNOWN_BANNER=RSRC_DIR+"unknown.png"
BANNERS_PATH=BASE_DIR+"banners/"
FLAVOURS_CONFIG_PATH=BASE_DIR+"supported-flavours/"

CURRENT_PLATFORM=platform.machine()

class GridButton:
	
	def __init__(self,info):
		
		self.info=info
		self.info["installed"]=False
		self.info["checked"]=False
		self.info["incompatible"]=False
		self.info["minimal"]=False
		self.info["lite"]=False
		self.info["shadow_alpha"]=0.1
		self.info["animation_active"]=False
		self.info["shadow_start"]=0
		self.info["available"]=True
		self.info["drawingarea"]=None
		
		if os.path.exists(BANNERS_PATH+self.info["pkg"]+".png"):
			self.info["image"]=BANNERS_PATH+self.info["pkg"]+".png"
		else:
			self.info["image"]=UNKNOWN_BANNER
		
	#def init
	
	
#class GridButton


class ConfButton:
	
	def __init__(self,info):
		
		self.txt=info["txt"]
		self.icon=info["icon"]
		self.name=info["name"]
		self.da=None
		if "active" not in info:
			self.active=False
		else:
			self.active=info["active"]
		
	#def

#class ConfButton
	
	
class ConfigurationParser:
	
	def __init__(self):
		pass
	
	def load_plugin(self,path):
	
		try:
			config = configparser.ConfigParser()
			config.optionxform=str
			config.read(path)
			if config.has_section("FLAVOUR"):
				info={}
				info["pkg"]=config.get("FLAVOUR","pkg")
				info["name"]=config.get("FLAVOUR","name")
				
				return GridButton(info)
				
		except Exception as e:
			print(e)
			return None
	
	
#class ConfigParser


class CustomColor:
	
	def __init__(self,r,g,b):
		
		self.r=r/255.0
		self.g=g/255.0
		self.b=b/255.0

#class CustomColor		

class AwesomeTabs:
	
	def __init__(self):
		
		self.check_root()

		self.configuration_parser=ConfigurationParser()
		
		self.current_tab=-1
		self.current_width=0
		self.animation_left=False
		self.animation_right=False
		
		self.current_red_width=0
		self.current_red_pos=0
		self.configuration_start=0
		
		self.current_grid_width=0
		self.current_grid_height=0
		
		self.max_grid_width=2
		
		self.dark_gray=CustomColor(130.0,151.0,161.0)
		self.light_gray=CustomColor(185.0,195.0,195.0)
		
		self.green=CustomColor(74.0,166.,69.0)
		self.light_green=CustomColor(88.0,208.0,86.0)
		
		self.conf_light=CustomColor(49.0,55.0,66.0)
		self.conf_dark=CustomColor(30.0,36.0,42.0)
		
		self.conf_light_shadow=CustomColor(107.0,116.0,137.0)
		self.conf_dark_shadow=CustomColor(0,0,0)
		
		self.current_conf_height=0
		self.conf_buttons=[]
		log_msg="---------------------------------------------------------\n"+"LLIUREX FLAVOUR SELECTOR STARTING AT: " + datetime.datetime.today().strftime("%d/%m/%y %H:%M:%S") +"\n---------------------------------------------------------"
		self.log(log_msg)
		self.start_gui()

	#def __init__
	
	
	def check_root(self):
		
		try:
			f=open("/etc/zero-lliurex-flavours.token","w")
			f.close()
			os.remove("/etc/zero-lliurex-flavours.token")
		except:
			dialog = Gtk.MessageDialog(None,0,Gtk.MessageType.ERROR, Gtk.ButtonsType.CANCEL, "Lliurex Flavours Selector")
			dialog.format_secondary_text("You need administration privileges to run this application.")
			dialog.run()
			sys.exit(1)

	#def check_root		
	
	def start_gui(self):
		
		builder=Gtk.Builder()
		builder.set_translation_domain('zero-lliurex-flavours')
		glade_path=RSRC_DIR+"lliurex-flavours-selector.ui"
		builder.add_from_file(glade_path)
		
		self.installers_eb=builder.get_object("installers_eventbox")
		self.installers_label=builder.get_object("installers_label")
		
		
		self.top_divider_da=builder.get_object("top_divider_drawingarea")
		self.bottom_divider_da=builder.get_object("bottom_divider_drawingarea")
		self.top_divider_da.connect("draw",self.draw_top_divider)
		self.bottom_divider_da.connect("draw",self.draw_bottom_divider)
		
		self.button_scroll=builder.get_object("button_scrolledwindow")
		self.main_box=builder.get_object("main_box")
		self.apply_button=builder.get_object("apply_button")
		self.apply_button.connect("clicked",self.apply_clicked)
		self.close_button=builder.get_object("close_button")
		self.close_button.connect("clicked",self.quit)
		'''
		self.apply_eb=builder.get_object("apply_eventbox")
		self.apply_da=builder.get_object("apply_drawingarea")
		self.apply_eb.connect("button-press-event",self.accept_clicked)
		self.apply_da.connect("draw",self.draw_apply_button)
		self.close_eb=builder.get_object("close_eventbox")
		self.close_da=builder.get_object("close_drawingarea")
		self.close_eb.connect("button-press-event",self.quit)
		self.close_da.connect("draw",self.draw_close_button)
		'''
		self.msg_label=builder.get_object("msg_label")
		
		self.stack = Gtk.Stack()
		self.stack.set_transition_duration(1000)
		self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
		
		self.installers_grid=builder.get_object("button_grid")
				
		
		
		self.stack.add_titled(self.button_scroll, "installers", "Installers")
		
		
		self.main_box.add(self.stack)
		
		self.main_window=builder.get_object("main_window")
		
		
		self.main_window.connect("destroy",self.quit)
		
		
		self.progress_window=builder.get_object("progress_window")
		self.pbar=builder.get_object("progressbar")
		self.installing_label=builder.get_object("installing_label")
		self.progress_window.set_transient_for(self.main_window)
		
		self.gather_window=builder.get_object("gather_window")
		self.gather_pbar=builder.get_object("progressbar1")
		self.progress_label=builder.get_object("progress_label")
		
		self.configuration_client_window=builder.get_object("configuration_client_window")
		self.configuration_title_label=builder.get_object("configuration_title_label")
		self.full_client_rb=builder.get_object("full_client_rb")
		self.full_client_rb.connect("toggled",self.client_options_toggled,"full")
		self.lite_client_rb=builder.get_object("lite_client_rb")
		self.lite_client_rb.connect("toggled",self.client_options_toggled,"lite")
		self.minimal_client_rb=builder.get_object("minimal_client_rb")
		self.minimal_client_rb.connect("toggled",self.client_options_toggled,"minimal")
		self.client_sourceslist_cb=builder.get_object("client_sourceslist_cb")
		self.client_sourceslist_cb.connect("toggled",self.client_sourceslist_toggled,"mirror")
		self.client_apply_btn=builder.get_object("client_apply_btn")
		self.client_apply_btn.connect("clicked",self.client_apply)
		self.client_cancel_btn=builder.get_object("client_cancel_btn")
		self.client_cancel_btn.connect("clicked",self.client_cancel)

		self.configuration_server_window=builder.get_object("configuration_server_window")
		self.configuration_title_label_server=builder.get_object("configuration_title_label_server")
		self.full_server_rb=builder.get_object("full_server_rb")
		self.full_server_rb.connect("toggled",self.server_options_toggled,"full")
		self.lite_server_rb=builder.get_object("lite_server_rb")
		self.lite_server_rb.connect("toggled",self.server_options_toggled,"lite")
		self.server_apply_btn=builder.get_object("server_apply_btn")
		self.server_apply_btn.connect("clicked",self.server_apply)
		self.server_cancel_btn=builder.get_object("server_cancel_btn")
		self.server_cancel_btn.connect("clicked",self.server_cancel)

		self.configuration_desktop_window=builder.get_object("configuration_desktop_window")
		self.configuration_title_label_desktop=builder.get_object("configuration_title_label_desktop")
		self.full_desktop_rb=builder.get_object("full_desktop_rb")
		self.full_desktop_rb.connect("toggled",self.desktop_options_toggled,"full")
		self.lite_desktop_rb=builder.get_object("lite_desktop_rb")
		self.lite_desktop_rb.connect("toggled",self.desktop_options_toggled,"lite")
		self.desktop_apply_btn=builder.get_object("desktop_apply_btn")
		self.desktop_apply_btn.connect("clicked",self.desktop_apply)
		self.desktop_cancel_btn=builder.get_object("desktop_cancel_btn")
		self.desktop_cancel_btn.connect("clicked",self.desktop_cancel)

		self.set_css_info()
		
		self.show_client_options=False
		self.add_mirror_repo=True
		self.full_client=True
		self.lite_client=False
		self.minimal_client=False
		self.full_server=True
		self.full_desktop=True
		self.defaultMirror = 'llx19'
		self.defaultVersion = 'bionic'
		self.textsearch_mirror="/mirror/"+str(self.defaultMirror)
		self.sourcesListPath='/etc/apt/sources.list'
		self.gather_window.show_all()
		self.minimal_client_installed=False
		self.lite_server_installed=False
		self.lite_client_installed=False
		self.lite_desktop_installed=False
		self.full_desktop_installed=False
		self.button_selected=False

		self.server_meta_available=["lliurex-meta-server","lliurex-meta-server-lite"]
		self.client_meta_available=["lliurex-meta-client","lliurex-meta-client-lite","lliure-meta-minimal-client"]
		self.desktop_meta_avaiable=["lliurex-meta-desktop","lliurex-meta-desktop-lite"]
		self.hide_meta_banners=["lliurex-meta-server-lite","lliurex-meta-client-lite","lliurex-meta-minimal-client","lliurex-meta-desktop-lite"]

		log_msg="-Current flavours installed:"
		self.log(log_msg)
		GLib.timeout_add(100,self.pulsate_gathering_info)
		
		self.t=threading.Thread(target=self.gather_info)
		self.t.daemon=True
		self.t.start()
		self.install_metas=[]
		self.update_metas=[]
		GObject.threads_init()		
		Gtk.main()
		
	#def start_gui
	
	def gather_info(self):
		
		import time
		base_apt_cmd="apt-cache policy "
		
		self.gbs=[]
		self.flavours_installed=0
		
		for item in sorted(os.listdir(FLAVOURS_CONFIG_PATH)):
			if os.path.isfile(FLAVOURS_CONFIG_PATH+item):
				gb=self.configuration_parser.load_plugin(FLAVOURS_CONFIG_PATH+item)
				if gb!=None:
					sys.stdout.write("* Checking %s ...\t"%gb.info["pkg"])
					gb.info["installed"]=self.is_installed(gb.info["pkg"])
					sys.stdout.write("%s\n"%gb.info["installed"])
					base_apt_cmd += "%s "%gb.info["pkg"]
					self.gbs.append(gb)
					
		p=subprocess.Popen([base_apt_cmd],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)	
		output=p.communicate()[0]

		if type(output) is bytes:
			output=output.decode()
		
		for gb in self.gbs:
			
			if gb.info["pkg"] not in output:
				print(" [!] %s not available [!] "%gb.info["pkg"])
				gb.info["available"]=False
			else:
				if gb.info["installed"]==True:
					if gb.info["pkg"]=="lliurex-meta-desktop":
						self.full_desktop_installed=True
					self.check_meta_blocked(gb)
					self.flavours_installed+=1
					self.check_meta_lite(gb)

					'''
					if gb.info["pkg"]=="lliurex-meta-minimal-client":
						self.minimal_client_installed=True
						for flavour in self.gbs:
							if flavour.info["pkg"]=="lliurex-meta-client" or flavor.info["pkg"]=="lliurex-meta-client-lite":
								if flavour.info["installed"]==False:
									if not flavour.info["incompatible"]:
										flavour.info["minimal"]=True
					'''
				if gb.info["pkg"] not in self.hide_meta_banners:				
					self.add_grid_button(gb)	
			
	#def gather_info
	
	def check_meta_blocked(self, gb):

		if gb.info["pkg"] in self.server_meta_available:
			for gb in self.gbs:
				if gb.info["pkg"] in self.client_meta_available: 
					gb.info["incompatible"]=True
				elif gb.info["pkg"] in self.desktop_meta_avaiable and not gb.info["installed"]:
					gb.info["incompatible"]=True	
		elif gb.info["pkg"] in self.client_meta_available:
			for gb in self.gbs:
				if gb.info["pkg"] in self.server_meta_available or gb.info["pkg"] in self.desktop_meta_avaiable:
					gb.info["incompatible"]=True				

	
	#def check_meta_blocked		

	def check_meta_lite(self,gb):

		if gb.info["pkg"]=="lliurex-meta-minimal-client":
			self.minimal_client_installed=True
			for flavour in self.gbs:
				if flavour.info["pkg"] in ["lliurex-meta-client","lliurex-meta-client-lite"]:
					if flavour.info["installed"]==False:
						if not flavour.info["incompatible"]:
							flavour.info["minimal"]=True
		
		elif gb.info["pkg"]=="lliurex-meta-client-lite":
			self.lite_client_installed=True
			for flavour in self.gbs:
				if flavour.info["pkg"] in ["lliurex-meta-client","lliurex-meta-minimal-client"]:
					if flavour.info["installed"]==False:
						if not flavour.info["incompatible"]:
							flavour.info["lite"]=True

		elif gb.info["pkg"]=="lliurex-meta-server-lite":
			self.lite_server_installed=True
			for flavour in self.gbs:
				if flavour.info["pkg"]=="lliurex-meta-server":
					if flavour.info["installed"]==False:
						if not flavour.info["incompatible"]:
							flavour.info["lite"]=True

		elif gb.info["pkg"]=="lliurex-meta-desktop-lite":
			self.lite_desktop_installed=True
			for flavour in self.gbs:
				if flavour.info["pkg"]=="lliurex-meta-desktop":
					if flavour.info["installed"]==False:
						if not flavour.info["incompatible"]:
							flavour.info["lite"]=True	

	#def check_meta_lite																								

	def pulsate_gathering_info(self):
		
		self.gather_pbar.pulse()
		
		if not self.t.is_alive():
			
			self.gather_window.hide()
			self.main_window.show_all()
		
			if self.flavours_installed<1:
				log_msg="No flavour detected"
				self.log(log_msg)
				msg=_("No flavour detected. Check one at least")
				self.msg_label.show()
				self.msg_label.set_markup(msg)
		return self.t.is_alive()
		
	#def pulsate_gathering
	
	def set_css_info(self):
		
		css = b"""
		
		#BLUE {
			background-image:-gtk-gradient (linear,	left top, left bottom, from (#0f72ff),  to (#0f72ff));;
		
		}
		
		#BLACK{
			background-image:-gtk-gradient (linear,	left top, left bottom, from (#000000),  to (#000000));;
		
		}
		
		
		#BACK_GRADIENT{
			background-image:-gtk-gradient (linear,	left top, left bottom, from (#ffffff), to (#eceff3));;
		}
		
		#WHITE {
			color: white;
			text-shadow: 0px 1px black;
		}
		
		#MAIN_LABEL_ENABLED{
			color: #8297a1;
			font: 18pt Noto Sans Bold;
		}
		
		#ALTERNATIVES_LABEL{
			color: #8297a1;
			font: 12pt Noto Sans Bold;		
		}

		#ALTERNATIVES_LABEL_CLIENT{
			color: #0f72ff;
			font: 10pt Noto Sans Bold;		
		}

		#ALTERNATIVES_LABEL_PROGRESS{
			color: #0f72ff;
			font: 12pt Noto Sans Bold;		
		}
		
		#DIALOG_LABEL{
			color: #8297a1;
			font: 10pt Noto Sans Bold;		
		}

		#MAIN_LABEL_DISABLED{
			color: #c9d4e2;
			font: 18pt Noto Sans Bold;
		}
		
		#RED_PROGRESS{
			
			background-color: #FF0000;
			border: 0px;

		}
		
		#DARK_BACK{
			background-color: #070809;
		}
		
		#GREEN {
			background-image:-gtk-gradient (linear,	left top, left bottom, from (#41ff70),  to (#41ff70));;
		
		}
		
		#ORANGE {
			background-image:-gtk-gradient (linear,	left top, left bottom, from (#ff7f2a),  to (#ff7f2a));;
		
		}
		
		#LIGHTBLUE {
			-unico-border-gradient: -gtk-gradient (linear, left top, left bottom,
			from (shade (#ff0000, 0.68)),
			to (shade (#ff0000, 0.68)));
		
		}
		
		#RED_LABEL{
			
			color: red;
			font: 10pt Noto Sans Bold;
		}

		
		GtkButton#RED GtkLabel {
			color: #8297a1;
			font: 11pt Noto Sans;
		}


		"""
		self.style_provider=Gtk.CssProvider()
		self.style_provider.load_from_data(css)
		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),self.style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		
		self.main_window.set_name("BACK_GRADIENT")
		self.installers_label.set_name("MAIN_LABEL_ENABLED")
		#self.pbar.set_name("RED_PROGRESS")
		#self.gather_pbar.set_name("RED_PROGRESS")
		self.progress_label.set_name("ALTERNATIVES_LABEL_PROGRESS")
		self.installing_label.set_name("ALTERNATIVES_LABEL_PROGRESS")
		self.configuration_title_label.set_name("ALTERNATIVES_LABEL_CLIENT")
		self.msg_label.set_name("RED_LABEL")
		
		
	#def css_info

	def is_installed(self,pkg):
		
		
		p=subprocess.Popen(["dpkg-query -W -f='${db:Status-Status}' %s"%pkg],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		output=p.communicate()[0]

		if type(output) is bytes:
			output=output.decode()
		
		if output=="installed":
			self.log(pkg)
			return True
			
		return False
		
		
	#def is_installed
	
	def quit(self,widget,event=None):
		
		Gtk.main_quit()
		
	#def quit
	
	def execute(self,command):
		
		self.thread_ret=-1
		p=subprocess.Popen([command],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)	
		output,perror=p.communicate()

		if len(output)>0:
			if type(output) is bytes:
				output=output.decode()
		if len(perror)>0:
			if type(perror) is bytes:
				perror=perror.decode()		

		self.thread_ret=p.returncode
		self.flavour_error=perror
	
		#Delete extra sources if music meta is being installed
		if 'lliurex-meta-music' in command:
			sourcesFile=open('/etc/apt/sources.list','r')
			repos=sourcesFile.readlines()
			repos_orig=[]
			for repo in repos:
				if 'kxstudio' not in repo:
					repos_orig.append(repo)
			sourcesFile.close()
			try:
				sourcesFile=open('/etc/apt/sources.list','w')
				sourcesFile.writelines(repos_orig)
				sourcesFile.close()
			except e as Exception:
				msg_log="Couldn't open sources.list for writting"
				self.log(msg_log)
	#def execute
	
	
	def pulsate_pbar(self,da):
		
		if self.t.is_alive():
			
			self.pbar.pulse()
				
		if not self.t.is_alive():
			self.progress_window.hide()
			if self.thread_ret==0:
				for item in self.install_metas:
				
					if item.info["checked"]:
						item.info["checked"]=False
						item.info["drawingarea"].queue_draw()
						self.mouse_left(item.info["drawingarea"],None,item)
						if item.info["pkg"] not in self.hide_meta_banners:
							item.info["installed"]=True
						elif item.info["pkg"] =="lliurex-meta-minimal-client":
							item.info["minimal"]=True
						else:
							item.info["lite"]=True	

						if self.add_mirror_repo:
							self.write_mirror_repository()
				try:
					self.remove_desktop.info["checked"]=False
					self.remove_desktop.info["drawingarea"].queue_draw()
					self.mouse_left(self.remove_desktop.info["drawingarea"],None,self.remove_desktop)
				except:
					print("No desktop flavour to remove")
					
				self.install_metas=[]	
				self.msg_label.show()
				self.msg_label.set_markup("<span foreground='#4aa645'><b>"+_("Installation succesful. A reboot is required")+"</b></span>")
				log_msg="Installation of new flavour OK"
				self.log(log_msg)
			else:
				self.msg_label.show()
				msg=_("An error ocurred. See log in /var/log/lliurex-flavours-selector")
				self.msg_label.set_markup(msg)
				log_msg="Error during installation of new flavours. " + self.flavour_error 
				self.log(log_msg)	
		return self.t.is_alive()
	
	#def pulsate_pbar

	
	def write_mirror_repository(self):

		sourcesFile=open(self.sourcesListPath,'r')
		repos=sourcesFile.readlines()
		repos_orig=[]
		for repo in repos:
			if self.textsearch_mirror not in repo:
				repos_orig.append(repo)
		sourcesFile.close()
		try:
			f = open(self.sourcesListPath,'w')
			f.write('deb http://mirror/{version_mirror} {version} main restricted universe multiverse\n'.format(version_mirror=self.defaultMirror,version=self.defaultVersion))
			f.write('deb http://mirror/{version_mirror} {version}-updates main restricted universe multiverse\n'.format(version_mirror=self.defaultMirror,version=self.defaultVersion))
			f.write('deb http://mirror/{version_mirror} {version}-security main restricted universe multiverse\n'.format(version_mirror=self.defaultMirror,version=self.defaultVersion))
			f.writelines(repos_orig)
			f.close()
			log_msg="Addedd local mirror repository to sources list"
			self.log(log_msg)
		except e as Exception:
			msg_log="Couldn't open sources.list for writting"
			self.log(msg_log)	

	#def write_mirror_repository
		
	def add_grid_button(self,grid_button):
		
		da=Gtk.DrawingArea()
		da.set_size_request(140,148)
		da.add_events(Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK | Gdk.EventMask.BUTTON_PRESS_MASK )
		
		da.connect("draw",self.draw_button,grid_button)
		da.connect("motion-notify-event",self.mouse_over,grid_button)
		da.connect("leave_notify_event",self.mouse_left,grid_button)
		da.connect("button-press-event",self.button_clicked,grid_button)
		grid_button.info["drawingarea"]=da
		
		da.show()
		self.installers_grid.attach(da,self.current_grid_width,self.current_grid_height,1,1)
		
		self.current_grid_width+=1
		
		if self.current_grid_width > self.max_grid_width:
			self.current_grid_width=0
			self.current_grid_height+=1
			
			
	#def add_grid_button
	
	#Function to show in each banner information about type of meta to be installed
	def button_clicked(self,widget,event,grid_button):
		
	
		if not (grid_button.info["installed"] or grid_button.info["incompatible"]):
			if grid_button.info["checked"]:
				self.install_metas.remove(grid_button)
				grid_button.info["checked"]=False
				if grid_button.info["pkg"]=="lliurex-meta-client":
					if self.minimal_client_installed:
						grid_button.info["minimal"]=True
					elif self.lite_client_installed:
						grid_button.info["lite"]=True
					self.button_selected=False	
				elif grid_button.info["pkg"]=="lliurex-meta-server":
					if self.lite_server_installed:
						grig_button.info["lite"]=True
					self.button_selected=False	
				elif grid_button.info["pkg"]=="lliurex-meta-desktop":
					if self.lite_desktop_installed:
						grid_button.info["lite"]=True
					self.button_selected=False				

				grid_button.info["drawingarea"].queue_draw()
				self.mouse_left(grid_button.info["drawingarea"],None,grid_button)
				
			
			else:
				if grid_button.info["pkg"] in ["lliurex-meta-server","lliurex-meta-client","lliurex-meta-desktop"]:
					if not self.button_selected:
						self.button_selected=True
						self.install_metas.append(grid_button)
						grid_button.info["checked"]=True
						grid_button.info["shadow_alpha"]+=0.1
						widget.queue_draw()
						if grid_button.info["pkg"]=="lliurex-meta-client":
							if self.minimal_client_installed:
								grid_button.info["minimal"]=False
							elif self.lite_client_installed:
								grid_button.info["lite"]=False
						elif grid_button.info["pkg"]=="lliurex-meta-server":
							if self.lite_server_installed:
								grid_button.info["lite"]=False
						elif grid_button.info["pkg"]=="lliurex-meta-desktop":
							if self.lite_desktop_installed:
								grid_button.info["lite"]=False				
						
				else:
					self.install_metas.append(grid_button)
					grid_button.info["checked"]=True
					grid_button.info["shadow_alpha"]+=0.1
					widget.queue_draw()
		
	#def button_clicked
	

	def apply_clicked(self,widget,even=None):
		
		type_dialog=""
		ret, msg=self.check_meta_compatibility()
		
		if not ret:
			self.msg_label.show()
			self.msg_label.set_markup(msg)
			return
		else:
			self.msg_label.hide()
			#self.show_confirm_dialog(widget)
			for item in self.install_metas:
				if item.info["pkg"] in self.client_meta_available:
					type_dialog="client"
				elif item.info["pkg"] in self.server_meta_available:
					type_dialog="server"
					
				elif item.info["pkg"] in self.desktop_meta_avaiable:
					type_dialog="desktop"
				
			
			if type_dialog=="":
				self.show_confirm_dialog(widget)
			elif type_dialog=="client":
				self.config_client_meta(widget)
			elif type_dialog=="server":
				self.config_server_meta(widget)
			elif type_dialog=="desktop":
				self.config_desktop_meta(widget)		
	
	# def accept_clicked	

	def config_client_meta(self,widget):

		self.show_client_options=True
		self.client_sourceslist_cb.set_active("mirror")
		self.full_client_rb.set_active("full")

		if self.full_desktop_installed:
			self.minimal_client_rb.set_sensitive(True)
			self.full_client_rb.set_sensitive(True)
			self.lite_client_rb.set_sensitive(False)

		else:
			if self.minimal_client_installed:
				self.minimal_client_rb.set_sensitive(False)
				self.full_client_rb.set_sensitive(True)
				self.lite_client_rb.set_sensitive(True)
			elif self.lite_client_installed:
				self.minimal_client_rb.set_sensitive(False)
				self.full_client_rb.set_sensitive(False)
				self.lite_client_rb.set_sensitive(False) 	

				if self.is_mirror_in_sourceslist():
					self.client_sourceslist_cb.set_active(False)
					self.show_client_options=False
					self.add_mirror_repo=False
				
		if self.show_client_options:
			self.configuration_client_window.show()
		else:
			self.show_confirm_dialog(widget)	

	#def config_client_meta

	def config_server_meta(self,widget):

		if self.full_desktop_installed:
			self.show_confirm_dialog(widget)
		else:	
			if self.lite_server_installed:
				self.show_confirm_dialog(widget)
			else:
				self.configuration_server_window.show()

	#def config_server_meta

	def config_desktop_meta(self,widget):

		if self.lite_desktop_installed:
			self.show_confirm_dialog(widget)
		else:
			self.configuration_desktop_window.show()

	#def config_server_meta

	def is_mirror_in_sourceslist(self):

		count=0
		if os.path.exists(self.sourcesListPath):
			origsources=open(self.sourcesListPath,'r')
			for line in origsources:
				if self.textsearch_mirror in line:
					count=+1

		if count==0:			
			return False
		else:
			return True	

	#def is_mirror_in_sourceslist
			
	def client_options_toggled(self,button,name):

		if button.get_active():
			if name=="full":
				self.full_client=True
				self.lite_client=False
				self.minimal_client=False
			elif name=="lite":
				self.full_client=False
				self.minimal_client=False
				self.lite_client=True
			elif name=="minimal":
				self.full_client=False
				self.lite_client=False
				self.minimal_client=True
		
	#def client_options_toggled

	def client_sourceslist_toggled(self,button,name):
	
		if button.get_active():
			self.add_mirror_repo=True
		else:
			self.add_mirror_repo=False	

	#def client_sourceslist_toggled
			
	def client_apply(self,widget,event=None):
	
		self.configuration_client_window.hide()	
		self.show_confirm_dialog(widget)	

	#def client_apply	

	def client_cancel(self,widget,event=None):
	
		self.configuration_client_window.hide()	

	#def client_cancel



	def server_options_toggled(self,button,name):

		if button.get_active():
			if name=="full":
				self.full_server=True
			else:
				self.full_server=False
	
	#def server_options_toggled

	def server_apply(self,widget,event=None):
	
		self.configuration_server_window.hide()	
		self.show_confirm_dialog(widget)	

	#def server_apply	

	def server_cancel(self,widget,event=None):
	
		self.configuration_server_window.hide()	

	#def server_cancel

	def desktop_options_toggled(self,button,name):

		if button.get_active():
			if name=="full":
				self.full_desktop=True
			else:
				self.full_desktop=False
	
	#def desktop_options_toggled

	def desktop_apply(self,widget,event=None):
	
		self.configuration_desktop_window.hide()	
		self.show_confirm_dialog(widget)	

	#def desktop_apply	

	def desktop_cancel(self,widget,event=None):
	
		self.configuration_desktop_window.hide()	

	#def desktop_cancel

	def show_confirm_dialog(self, widget):

		message=_("The selected flavours will be installed. Do you wish to continue?")
		'''
		label = Gtk.Label(message)

		dialog = Gtk.Dialog("Lliurex Flavours Selector", None, Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT, (Gtk.STOCK_YES, Gtk.ResponseType.YES,Gtk.STOCK_NO, Gtk.ResponseType.NO))
		dialog.vbox.pack_start(label,True,True,10)

		label.show()
		dialog.set_border_width(6)
		dialog.set_name("BACK_GRADIENT")
		label.set_name("DIALOG_LABEL")
		'''
		dialog = Gtk.MessageDialog(None,0,Gtk.MessageType.WARNING,Gtk.ButtonsType.YES_NO, "LliureX Flavours Selector")
		dialog.format_secondary_text(message)
		response = dialog.run()

		if response==Gtk.ResponseType.YES:
			self.install_packages(widget)
		dialog.destroy()		
		
	# def show_confirm_dialog	
				
	def install_packages(self,widget):
		
		cmd='lliurex-preseed --update; apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y '
		pkg=""
		log_pkg=""
		for item in self.update_metas:
			pkg+=item.info["pkg"] + ' '
			
		for item in self.install_metas:
			if item.info["pkg"]=="lliurex-meta-client":
				if not self.full_client:
					if not self.minimal_client:
						item.info["pkg"]="lliurex-meta-minimal-client"
					else:
						item.info["pkg"]="lliurex-meta-client-lite"

			elif item.info["pkg"]=="lliurex-meta-server":
				if not self.full_server:
					item.info["pkg"]="lliurex-meta-server-lite"
			
			elif item.info["pkg"]=="lliurex-meta-desktop":
				if not self.full_desktop:
					item.info["pkg"]="lliurex-meta-desktop-lite"						

			elif item.info["pkg"]=="lliurex-meta-infantil":
				cmdInfantil=["sudo","/usr/bin/add-apt-repository", "deb http://lliurex.net/xenial xenial preschool"]
				x=subprocess.Popen((cmdInfantil),stdin=subprocess.PIPE,stdout=subprocess.PIPE)
				log_msg="Adding repository recursos"
				self.log(log_msg)
				x.communicate(b"\n")[0]
				
			elif item.info["pkg"]=="lliurex-meta-musica":
				lxRepos=["deb http://ppa.launchpad.net/kxstudio-debian/libs/ubuntu xenial main",
					"deb http://ppa.launchpad.net/kxstudio-debian/music/ubuntu xenial main",
					"deb http://ppa.launchpad.net/kxstudio-debian/plugins/ubuntu xenial main",
					"deb http://ppa.launchpad.net/kxstudio-debian/apps/ubuntu xenial main",
					"deb http://ppa.launchpad.net/kxstudio-debian/kxstudio/ubuntu xenial main"]

				cmdMusica=["sudo","/usr/bin/add-apt-repository"]
				for repo in lxRepos:
					log_msg="Adding repository "+repo
					self.log(log_msg)
					cmdAux=cmdMusica+[repo]
					x=subprocess.Popen((cmdAux),stdin=subprocess.PIPE,stdout=subprocess.PIPE)
					x.communicate(b"\n")[0]

			pkg+=item.info["pkg"] + ' '
			log_pkg=log_pkg+item.info["pkg"]+ ' '

		command=cmd+pkg
	
		self.t=threading.Thread(target=self.execute,args=(command,))
		self.t.daemon=True
		self.t.start()
		log_msg="-New flavours to install:"
		self.log(log_msg)
		log_msg=str(log_pkg)
		self.log(log_msg)
		GLib.timeout_add(100,self.pulsate_pbar,widget)
		self.progress_window.show()	
		
		
	# def install_packages	
		
	def check_meta_compatibility(self):
				
		if len(self.install_metas)>0:
			
			for gb in self.gbs:
				if gb.info["available"]:
					if gb.info["installed"]:
						if not gb in self.update_metas:
							self.update_metas.append(gb)
							
						if gb.info["pkg"] in self.server_meta_available:
							for item in self.install_metas:
								if item.info["pkg"] in self.client_meta_available:
									return [False,_("Incompatibility between Server and Client detected")]
																		
								if item.info["pkg"] in self.desktop_meta_avaiable:
									return [False, _("Is not possible adding Desktop Flavour in Server")] 	
									
						if gb.info["pkg"] in self.client_meta_available:
							for item in self.install_metas:
								if item.info["pkg"] in self.server_meta_available:
									return [False,_("Incompatibility between Server and Client detected")]
						
						if gb.info["pkg"] in self.desktop_meta_avaiable:
							for item in self.install_metas:
								if item.info["pkg"] in self.server_meta_available:
									if  gb in self.update_metas:
										self.update_metas.remove(gb)			
			i=0		
			
			for item in self.install_metas:
				if item.info["pkg"] in self.server_meta_available:
					i+=1
					for item in self.install_metas:
						if item.info["pkg"] in self.client_meta_available:
							i+=1
						if item.info["pkg"] in self.desktop_meta_avaiable:
							self.install_metas.remove(item)
							self.remove_desktop=item
									
			if i>1:
				return [False,_("Incompatibility between Server and Client detected")]
			
			return [True,""]
			
		else:
			return [False,_("Choose new flavour to incorporate or close button")]
			
	#def check_meta_compatibility
				
	def draw_button(self,widget,ctx,grid_button):
		
		ctx.move_to(0,0)
		img=cairo.ImageSurface.create_from_png(SHADOW_BANNER)
		ctx.set_source_surface(img,0,grid_button.info["shadow_start"])
		ctx.paint_with_alpha(grid_button.info["shadow_alpha"])
		
		ctx.move_to(0,0)
		img=cairo.ImageSurface.create_from_png(grid_button.info["image"])
		ctx.set_source_surface(img,0,0)
		ctx.paint()
		
		ctx.move_to(0,0)
		ctx.set_source_rgba(1,1,1,1)
		ctx.rectangle(0,110,140,30)
		ctx.fill()
		
		
		ctx.set_source_rgba(self.dark_gray.r,self.dark_gray.g,self.dark_gray.b,1)
		
		pctx = PangoCairo.create_layout(ctx)
		desc = Pango.font_description_from_string ("Noto Sans Bold 7.5")
		pctx.set_font_description(desc)
		pctx.set_markup(grid_button.info["name"])
		ctx.move_to(5,118)
		PangoCairo.show_layout(ctx, pctx)
		width=pctx.get_pixel_size()[0]
		
		
		
		if grid_button.info["installed"]:
		
			desc = Pango.font_description_from_string ("Noto Sans Bold 7")
			pctx.set_font_description(desc)
			ctx.set_source_rgba(self.green.r,self.green.g,self.green.b,1)
			txt=_("Installed")
			pctx.set_markup(txt)
			width=pctx.get_pixel_size()[0]
			ctx.move_to(140-width-5,120)
			PangoCairo.show_layout(ctx, pctx)
			
			ctx.rectangle(5,139,130,1)
			ctx.fill()
		
		if grid_button.info["checked"]:
		
			desc = Pango.font_description_from_string ("Noto Sans Bold 7")
			pctx.set_font_description(desc)
			ctx.set_source_rgba(self.green.r,self.green.g,self.green.b,1)
			txt=_("Install")
			pctx.set_markup(txt)
			width=pctx.get_pixel_size()[0]
			ctx.move_to(140-width-5,120)
			PangoCairo.show_layout(ctx, pctx)
			
			ctx.rectangle(5,139,130,1)
			ctx.fill()
		

		if grid_button.info["incompatible"]:
		
			desc = Pango.font_description_from_string ("Noto Sans Bold 7")
			pctx.set_font_description(desc)
			ctx.set_source_rgba(255,0,0,1)
			txt=_("Incompatible")
			pctx.set_markup(txt)
			width=pctx.get_pixel_size()[0]
			ctx.move_to(140-width-5,120)
			PangoCairo.show_layout(ctx, pctx)
			
			ctx.rectangle(5,139,130,1)
			ctx.fill()

		if grid_button.info["minimal"]:
		
			desc = Pango.font_description_from_string ("Noto Sans Bold 7")
			pctx.set_font_description(desc)
			ctx.set_source_rgba(0,0,255,1)
			txt=_("Minimal")
			pctx.set_markup(txt)
			width=pctx.get_pixel_size()[0]
			ctx.move_to(140-width-5,120)
			PangoCairo.show_layout(ctx, pctx)
			
			ctx.rectangle(5,139,130,1)
			ctx.fill()	

		if grid_button.info["lite"]:
		
			desc = Pango.font_description_from_string ("Noto Sans Bold 7")
			pctx.set_font_description(desc)
			ctx.set_source_rgba(0,0,255,1)
			txt=_("Lite")
			pctx.set_markup(txt)
			width=pctx.get_pixel_size()[0]
			ctx.move_to(140-width-5,120)
			PangoCairo.show_layout(ctx, pctx)
			
			ctx.rectangle(5,139,130,1)
			ctx.fill()	

	#def draw_button
	
	
	def drawing_label_event(self,widget,ctx,id):
		
		if id==self.current_tab:

			lg1 = cairo.LinearGradient(0.0,0.0, 300.0, 3.0)
			lg1.add_color_stop_rgba(0, 0, 1, 1, 0)
			lg1.add_color_stop_rgba(0.5, 0, 1, 1, 1)
			lg1.add_color_stop_rgba(1, 0, 1, 1, 0)
			ctx.rectangle(0, 0, 300, 3)
			ctx.set_source(lg1)
			ctx.fill()
			
	#drawing_label_event
	
	'''
	def draw_apply_button(self,widget,ctx):
		
		
		button_border=22
		
		pctx = PangoCairo.create_layout(ctx)
		desc = Pango.font_description_from_string ("Noto Sans Bold 10")
		pctx.set_font_description(desc)
		
		pctx.set_markup(_("APPLY"))
		width=pctx.get_pixel_size()[0]
		widget.set_size_request(width+button_border*2,30)
		
		ctx.set_source_rgba(1,1,0,1)
		xx=0
		yx=0
		widthx=width+44
		heightx=30
		radius=5
		
		r=47.0
		g=167.0
		b=223.0
		alpha=1.0
		
		r=r/255.0
		g=g/255.0
		b=b/255.0
		
		r2=83
		g2=153
		b2=252
		
		r2=r2/255.0
		g2=g2/255.0
		b2=b2/255.0
		
		
		lg1 = cairo.LinearGradient(0.0,0.0, 90.0, 0)
		lg1.add_color_stop_rgba(0, r, g, b, 1)
		lg1.add_color_stop_rgba(1, r2, g2, b2, 1)
		ctx.set_source(lg1)
		
		
		ctx.move_to (xx + radius, yx);
		ctx.arc (xx + widthx - radius, yx + radius, radius, pi * 1.5, pi * 2);
		ctx.arc (xx + widthx - radius, yx + heightx - radius, radius, 0, pi * .5);
		ctx.arc (xx + radius, yx + heightx - radius, radius, pi * .5, pi);
		ctx.arc (xx + radius, yx + radius, radius, pi , pi * 1.5);
		ctx.fill ();
		
		ctx.set_source_rgb(0.9,0.9,0.9)
		ctx.move_to(button_border,7)
		PangoCairo.show_layout(ctx, pctx)
	
	#draw_apply_button
	
	def draw_close_button(self,widget,ctx):
		
		
		button_border=22
		
		pctx = PangoCairo.create_layout(ctx)
		desc = Pango.font_description_from_string ("Noto Sans Bold 10")
		pctx.set_font_description(desc)
		
		pctx.set_markup(_("CLOSE"))
		width=pctx.get_pixel_size()[0]
		widget.set_size_request(width+button_border*2,30)
		
		ctx.set_source_rgba(1,1,0,1)
		xx=0
		yx=0
		widthx=width+44
		heightx=30
		radius=5
		
		r=47.0
		g=167.0
		b=223.0
		alpha=1.0
		
		r=r/255.0
		g=g/255.0
		b=b/255.0
		
		r2=83
		g2=153
		b2=252
		
		r2=r2/255.0
		g2=g2/255.0
		b2=b2/255.0
		
		
		lg1 = cairo.LinearGradient(0.0,0.0, 90.0, 0)
		lg1.add_color_stop_rgba(0, r, g, b, 1)
		lg1.add_color_stop_rgba(1, r2, g2, b2, 1)
		ctx.set_source(lg1)
		
		
		ctx.move_to (xx + radius, yx);
		ctx.arc (xx + widthx - radius, yx + radius, radius, pi * 1.5, pi * 2);
		ctx.arc (xx + widthx - radius, yx + heightx - radius, radius, 0, pi * .5);
		ctx.arc (xx + radius, yx + heightx - radius, radius, pi * .5, pi);
		ctx.arc (xx + radius, yx + radius, radius, pi , pi * 1.5);
		ctx.fill ();
		
		ctx.set_source_rgb(0.9,0.9,0.9)
		ctx.move_to(button_border,7)
		PangoCairo.show_layout(ctx, pctx)
		
	#def draw_close_button
	'''
	
	def draw_top_divider(self,widget,ctx):
		
		r=self.dark_gray.r
		g=self.dark_gray.g
		b=self.dark_gray.b
		alpha=1.0
		
		ctx.set_source_rgba(r,g,b,alpha)
		ctx.rectangle(0,1,500,3)
		ctx.fill()
		
		
	#def draw_top_divider
	
	
	def draw_bottom_divider(self,widget,ctx):
		
		r=self.dark_gray.r
		g=self.dark_gray.g
		b=self.dark_gray.b
		alpha=1.0
		
		ctx.set_source_rgba(r,g,b,alpha)
		ctx.rectangle(0,1,500,3)
		ctx.fill()
		
	#def draw_bottom_divider
	
	
	def mouse_over(self,widget,event,grid_button):
		
		grid_button.info["animation_active"]=False
		if grid_button.info["shadow_alpha"] <0.5 :
			grid_button.info["shadow_alpha"]+=0.1
			widget.queue_draw()
			return True
			
		return False
		
	#def mouse_over

	def mouse_left(self,widget,event,grid_button):
		if not grid_button.info["checked"]:
			if not grid_button.info["animation_active"]:
			
				grid_button.info["animation_active"]=True
				GLib.timeout_add(10,self.restore_shadow_alpha,grid_button,widget)
			
	#def mouse_left

	
	def restore_shadow_alpha(self,grid_button,widget):
		
		if grid_button.info["shadow_alpha"] >0.2 :
			grid_button.info["shadow_alpha"]-=0.1
		
			widget.queue_draw()
			return True
			
		grid_button.info["animation_active"]=False
		return False
		
	# def restore_shadow_alfpha	

	def log(self,log_msg):
		log_file="/var/log/lliurex-flavour-selector.log"
		f=open(log_file,"a+")
		f.write(log_msg + '\n')
		f.close()
		
	# def log		
		

			
#awesome tabs

if __name__=="__main__":
	
	at=AwesomeTabs()
