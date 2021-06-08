#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import subprocess
import configparser
import datetime
import dpkgunlocker.dpkgunlockermanager as DpkgUnlockerManager
import copy


BASE_DIR="/usr/share/lliurex-flavours-selector/"


class flavourSelectorManager:

	def __init__(self):

		self.core=Core.Core.get_core()
		self.supported_flavours=self.core.supported_flavours
		self.banners=self.core.banners
		self.flavour_list={}
		self.order=0
		self.result_install={}
		self.server_meta_available=["lliurex-meta-server","lliurex-meta-server-lite"]
		self.client_meta_available=["lliurex-meta-client","lliurex-meta-client-lite","lliurex-meta-minimal-client"]
		self.desktop_meta_available=["lliurex-meta-desktop","lliurex-meta-desktop-lite"]
		self.minimal_client_installed=False
		self.flavours_installed=[]
		self.defaultMirror = 'llx21'
		self.defaultVersion = 'focal'
		self.textsearch_mirror="/mirror/"+str(self.defaultMirror)
		self.sourcesListPath='/etc/apt/sources.list'
		self.numberPackages=[]
		self.initialNumberPackages=[]
		self.progressInstallation=0
		self.aptIsRunning=False
		log_msg="---------------------------------------------------------\n"+"LLIUREX FLAVOUR SELECTOR STARTING AT: " + datetime.datetime.today().strftime("%d/%m/%y %H:%M:%S") +"\n---------------------------------------------------------"
		self.log(log_msg)
		self.dpkgUnlocker=DpkgUnlockerManager.DpkgUnlockerManager()

	
	def loadFile(self,path):

		try:
			config = configparser.ConfigParser()
			config.optionxform=str
			config.read(path)
			if config.has_section("FLAVOUR"):
				info={}
				info["pkg"]=config.get("FLAVOUR","pkg")
				info["name"]=config.get("FLAVOUR","name")
				info["show"]=True
				info["incompatible"]=False
				if os.path.exists(self.core.banners+info["pkg"]+".png"):
					info["banner"]=self.core.banners+info["pkg"]+".png"
				else:
					info["banner"]=None

				return info
				
		except Exception as e:
			return None

	#def loadFile

	def getSupportedFlavour(self):

		for item in sorted(os.listdir(self.supported_flavours)):
			if os.path.isfile(self.supported_flavours+item):
				tmp_info=self.loadFile(self.supported_flavours+item)
				if tmp_info!=None:
					tmp_info["installed"]=self.isInstalled(tmp_info["pkg"])

					base_apt_cmd = "apt-cache policy %s "%tmp_info["pkg"]
					p=subprocess.Popen([base_apt_cmd],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)	
					output=p.communicate()[0]
					if type(output) is bytes:
						output=output.decode()

					if tmp_info["pkg"] not in output:
						available=False
					else:	
						version=output.split("\n")[4]
						if version !='':
							available=True
						else:
							available=False
						
					if available:
						self.flavour_list[self.order]=tmp_info
						self.order+=1
					if tmp_info["installed"]:
						tmp_info["show"]=False
						self.flavours_installed.append(tmp_info["pkg"])
		
		#if len(self.flavours_installed)>0:
		log_msg="Current flavours installed: "+str(self.flavours_installed)
		self.log(log_msg)
		self.checkMetaInstalled()
		self.showHideMeta()
		self.createAlternatives()
		#else:
		#	log_msg="No flavour detected"
		#	self.log(log_msg)
	

	#def getSupportedFlavours	

	def isInstalled(self,pkg):
		
		p=subprocess.Popen(["dpkg-query -W -f='${db:Status-Status}' %s"%pkg],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		output=p.communicate()[0]

		if type(output) is bytes:
			output=output.decode()
		
		if output=="installed":
			return True
			
		return False
		
	#def isInstalled

	def checkMetaInstalled(self):

		self.server=False
		self.server_lite=False
		self.client=False
		self.client_lite=False
		self.minimal_client=False
		self.desktop=False
		self.desktop_lite=False
		self.pime=False
		self.music=False
		self.infantil=False
		self.empty=False

		if len(self.flavours_installed)>0:
			for item in self.flavours_installed:
				if item=="lliurex-meta-server":
					self.server=True
					self.server_lite=False
					self.desktop=False
					self.desktop_lite=False
					self.pime=False
					break
				elif item=="lliurex-meta-server-lite":
					self.server_lite=True
					self.desktop=False
					self.desktop_lite=False
					self.pime=False
				elif item=="lliurex-meta-client":
					self.client=True
					self.cliente_lite=False
					self.minimal_client=False
					self.desktop=False
					self.desktop_lite=False
					self.pime=False
					break
				elif item=="lliurex-meta-client-lite":
					self.client_lite=True
					self.minimal_client=False
					self.desktop=False
					self.desktop_lite=False
					self.pime=False
				elif item=="lliurex-meta-minimal-client":
					if not self.client_lite:
						self.minimal_client=True
					self.desktop=False
					self.desktop_lite=False
					self.pime=False
				elif item=="lliurex-meta-desktop":
					self.desktop=True
					self.desktop_lite=False
					self.pime=False
				elif item=="lliurex-meta-desktop-lite":
					self.desktop_lite=True
					self.pime=False
				elif item=="lliurex-meta-pime":
					self.pime=True
				elif item=="lliurex-meta-music":
					self.music=True
				elif item=="lliurex-meta-infantil":
					self.infantil=True
		else:
			self.empty=True

	#def checkMetaInstalled
	
	def showHideMeta(self):


		for item in self.flavour_list:
			if self.server or self.server_lite:
				if self.flavour_list[item]["pkg"] in self.client_meta_available:
					self.flavour_list[item]["incompatible"]=True
					self.flavour_list[item]["show"]=False
				elif self.flavour_list[item]["pkg"] in self.desktop_meta_available:
					self.flavour_list[item]["incompatible"]=True	
					self.flavour_list[item]["show"]=False
				elif self.flavour_list[item]["pkg"]=="lliurex-meta-pime":
					self.flavour_list[item]["incompatible"]=True
					self.flavour_list[item]["show"]=False	
				elif self.flavour_list[item]["pkg"]=="lliurex-meta-server-lite" and self.server:
					self.flavour_list[item]["show"]=False
			
			elif self.client or self.client_lite or self.minimal_client:
				if self.flavour_list[item]["pkg"] in self.server_meta_available: 
					self.flavour_list[item]["incompatible"]=True
					self.flavour_list[item]["show"]=False
				elif self.flavour_list[item]["pkg"] in self.desktop_meta_available:
					self.flavour_list[item]["incompatible"]=True	
					self.flavour_list[item]["show"]=False
				elif self.flavour_list[item]["pkg"]=="lliurex-meta-pime":
					self.flavour_list[item]["incompatible"]=True
					self.flavour_list[item]["show"]=False	
				elif self.flavour_list[item]["pkg"] in ["lliurex-meta-client-lite","lliurex-meta-minimal-client"] and self.client:
					self.flavour_list[item]["show"]=False
				elif self.client_lite and self.flavour_list[item]["pkg"]=="lliurex-meta-minimal-client":
					self.flavour_list[item]["show"]=False
				elif self.minimal_client and self.flavour_list[item]["pkg"]=="lliurex-meta-client":
					self.flavour_list[item]["show"]=False


			elif self.desktop:
				if self.flavour_list[item]["pkg"] not in ["lliurex-meta-server","lliurex-meta-client","lliurex-meta-music","lliurex-meta-infantil"]: 
					self.flavour_list[item]["show"]=False

			elif self.desktop_lite:
				if self.flavour_list[item]["pkg"] not in ["lliurex-meta-desktop","lliurex-meta-server-lite","lliurex-meta-client-lite","lliurex-meta-music","lliurex-meta-infantil"]: 
					self.flavour_list[item]["show"]=False
		
			elif self.music or self.infantil:
				if self.flavour_list[item]["pkg"] not in ["lliurex-meta-desktop","lliurex-meta-server","lliurex-meta-client"]: 
					self.flavour_list[item]["show"]=False	
			
			elif self.pime:
				if self.flavour_list[item]["pkg"] not in ["lliurex-meta-desktop","lliurex-meta-server-lite","lliurex-meta-client-lite","lliurex-meta-music","lliurex-meta-infantil"]: 
					self.flavour_list[item]["show"]=False
	
			elif self.empty:
				if self.flavour_list[item]["pkg"] not in ["lliurex-meta-server","lliurex-meta-client","lliurex-meta-desktop","lliurex-meta-music","lliurex-meta-infantil"]:
					self.flavour_list[item]["show"]=False
	#def showHideMeta			

	def createAlternatives(self):

		self.client_desktop_alternatives=[]
		self.client_lite_alternatives=[]
		self.server_alternatives=[]
		self.desktop_alternatives=[]

		for item in self.flavour_list:
			if self.desktop or self.desktop_lite or self.music or self.infantil or self.empty or self.pime:
				if self.flavour_list[item]["pkg"] in self.client_meta_available and self.flavour_list[item]["pkg"] not in self.flavours_installed:
					tmp=[]
					tmp.append(self.flavour_list[item]["name"])
					tmp.append(self.flavour_list[item]["pkg"])
					self.client_desktop_alternatives.append(tmp)

				if self.flavour_list[item]["pkg"] in self.server_meta_available and self.flavour_list[item]["pkg"] not in self.flavours_installed:
					tmp=[]
					tmp.append(self.flavour_list[item]["name"])
					tmp.append(self.flavour_list[item]["pkg"])
					self.server_alternatives.append(tmp)

				if self.empty:
					if self.flavour_list[item]["pkg"] in self.desktop_meta_available and self.flavour_list[item]["pkg"] not in self.flavours_installed:
						tmp=[]
						tmp.append(self.flavour_list[item]["name"])
						tmp.append(self.flavour_list[item]["pkg"])
						self.desktop_alternatives.append(tmp)
	
			
			elif self.minimal_client:
				if self.flavour_list[item]["pkg"] in ["lliurex-meta-client","lliurex-meta-client-lite"] and self.flavour_list[item]["pkg"] not in self.flavours_installed:
					tmp=[]
					tmp.append(self.flavour_list[item]["name"])
					tmp.append(self.flavour_list[item]["pkg"])
					self.client_lite_alternatives.append(tmp)

	#def createAlternatives

	def isMirrorInSourceslist(self):

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

	#def isMirrorInSourceslist					

	def isIncompatibleMeta(self,meta):

		for item in self.flavour_list:
			if self.flavour_list[item]["pkg"]==meta:
				if self.flavour_list[item]["incompatible"]:
					return True
				else:
					return False

	#def isIncompatibleMeta		
	
	def installMeta(self,meta,mirrorRespository=None):

		self.thread_ret=-1
		
		music_meta=False
		cmd_base='lliurex-preseed --update; apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y '
		
		if self.needHwe():
			cmd_base=cmd_base+'xserver-xorg-video-dummy-hwe-18.04 '

		cmd=cmd_base+meta

		if meta=="lliurex-meta-infantil":
			self.addRecursosRepository()
		elif meta=="lliurex-meta-music":
			music_meta=True
			self.addMusicRepository()		

		log_msg="-New flavours to install:"+meta
		self.log(log_msg)
		
		p=subprocess.Popen([cmd],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)	
		output,perror=p.communicate()

		if len(output)>0:
			if type(output) is bytes:
				output=output.decode()
		if len(perror)>0:
			if type(perror) is bytes:
				perror=perror.decode()		

		self.thread_ret=p.returncode
		self.flavour_error=perror

		if music_meta:
			self.removeMusicRepository()

		if self.thread_ret==0:
			log_msg="Installation of new flavour OK"
			self.log(log_msg)
			if mirrorRespository:
				self.writeMirrorRepository()
		else:
			log_msg="Error during installation of new flavours. " + self.flavour_error 
			self.log(log_msg)	

	# def InstallMeta	

	def needHwe(self):

		cmd='dpkg -l | grep "hwe" | grep "^i[i]"'
		p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
		output=p.communicate()[0]

		if len(output)>0:
			return True
		else:
			return False
	
	#def needHwe
	
	def addRecursosRepository(self):

		cmdInfantil=["sudo","/usr/bin/add-apt-repository", "deb http://lliurex.net/focal focal preschool"]
		x=subprocess.Popen((cmdInfantil),stdin=subprocess.PIPE,stdout=subprocess.PIPE)
		log_msg="Adding repository recursos"
		self.log(log_msg)
		x.communicate(b"\n")[0]

	#def addRecursosRepository

	def addMusicRepository(self):
		
		lxRepos=["deb http://ppa.launchpad.net/kxstudio-debian/libs/ubuntu focal main"]

		cmdMusica=["sudo","/usr/bin/add-apt-repository"]

		for repo in lxRepos:
			log_msg="Adding repository "+repo
			self.log(log_msg)
			cmdAux=cmdMusica+[repo]
			x=subprocess.Popen((cmdAux),stdin=subprocess.PIPE,stdout=subprocess.PIPE)
			x.communicate(b"\n")[0]

	#def addMusicRepository	

	def removeMusicRepository(self):

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

	 #def removeMusicRepository		

	def writeMirrorRepository(self):

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

	#def writeMirrorRepository

	def getNumberPackages(self,meta):

		cmd="LANG=C LANGUAGE=en apt-get update; apt-get install --simulate %s"%meta
		psimulate = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
		rawoutputpsimulate = psimulate.stdout.readlines()
		rawpackagestoinstall = [ aux.decode().strip() for aux in rawoutputpsimulate if aux.decode().startswith('Inst') ]
		r = [ aux.replace('Inst ','') for aux in rawpackagestoinstall ]
		for allinfo in r :
			self.numberPackages.append(allinfo.split(' ')[0])

		self.initialNumberPackages=copy.deepcopy(self.numberPackages)

	#def getNumberPackages

	def isAptRunning(self):

		locks_info=self.dpkgUnlocker.isDpkgLocked()
		if locks_info==3:
			return True
		else:
			return False

	#def isAptRunning

	def checkProgressInstallation(self):

		for i in range(len(self.numberPackages)-1,-1,-1):
			is_installed=self.isInstalled(self.numberPackages[i])
			if is_installed:
				self.numberPackages.pop(i)

		self.progressInstallation=len(self.initialNumberPackages)-len(self.numberPackages)
	
	#def checkProgressInstallation
	
	def log(self,log_msg):
		log_file="/var/log/lliurex-flavour-selector.log"
		f=open(log_file,"a+")
		f.write(log_msg + '\n')
		f.close()
		
	# def log		

from . import Core