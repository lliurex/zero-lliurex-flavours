#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import subprocess
import configparser
import shutil
import copy
import threading
import urllib.request
import tempfile
import datetime

BASE_DIR="/usr/share/lliurex-flavours-selector/"
PACKAGE_NAME="zero-lliurex-flavours"

class FlavourSelectorManager:
	
	ERROR_PARTIAL_INSTALL=-1
	ERROR_INSTALL_INSTALL=-2
	ERROR_INTERNET_CONNECTION=-4
	ERROR_UNINSTALL_UNINSTALL=-5
	ERROR_PARTIAL_UNINSTALL=-6
	ERROR_PROCESS=-7
	ERROR_PROCESS_CONFLICTS=-8
	
	SUCCESS_INSTALL_PROCESS=1
	SUCCESS_UNINSTALL_PROCESS=7
	SUCCESS_PROCESS=9

	MSG_FEEDBACK_INTERNET=3
	MSG_FEEDBACK_INSTALL_REPOSITORIES=4
	MSG_FEEDBACK_INSTALL_RUN=5
	MSG_FEEDBACK_UNINSTALL_RUN=6
	MSG_WARNING_REMOVE_META=8
	MSG_FEEDBACK_AUTOREMOVE=10
	MSG_FEEDBACK_PROTECTION=11

	def __init__(self):

		self.supportedFlavours=os.path.join(BASE_DIR,"supported-flavours")
		self.banners=os.path.join(BASE_DIR,"banners")
		self.flavoursData=[]
		self.flavoursInfo={}
		self.flavourSelected=[]
		self.flavourSelectedToInstall=[]
		self.flavourSelectedToRemove=[]
		self.wantToRemove=[]
		self.firstConnection=False
		self.secondConnection=False
		self.urltocheck1="http://lliurex.net"
		self.urltocheck2="https://github.com/lliurex"
		self.pkgsInstalled=[]
		self.nonManagedPkg=0
		self.totalPackages=0
		self.runPkexec=True
		self.nonExpandedParent=[]
		self.allUnExpanded=True
		self.flavoursBase=["lliurex-meta-desktop","lliurex-meta-desktop-lite"]
		self._isRunPkexec()
		self._getSessionLang()
		self._clearCache()
				
	#def __init__

	def _isRunPkexec(self):

		if 'PKEXEC_UID' not in os.environ:
			self.runPkexec=False

	#def _isRunPkexec
	
	def _getSessionLang(self):

		tmpLang=os.environ["LANGUAGE"].split(":")

		if len(tmpLang)>0:
			self.sessiongLang=tmpLang[0]
		else:
			self.sessiongLang=os.environ["LANG"]


	#def _getSessionLang

	def loadFile(self,path):

		try:
			config = configparser.ConfigParser()
			config.optionxform=str
			config.read(path)
			if config.has_section("FLAVOUR"):
				info={}
				info["id"]=config.get("FLAVOUR","id")
				info["pkg"]=config.get("FLAVOUR","pkg")
				if 'ca' in self.sessiongLang:
					info["name"]=config.get("FLAVOUR","name[ca@valencia]")
				elif 'es' in self.sessiongLang:
					info["name"]=config.get("FLAVOUR","name[es]")
				else:
					info["name"]=config.get("FLAVOUR","name")

				info["type"]=config.get("FLAVOUR","type")
				if info["type"]=="child":
					info["installCmd"]=config.get("FLAVOUR","installCmd")
					info["removeCmd"]=config.get("FLAVOUR","removeCmd")
					info["parent"]=config.get("FLAVOUR","parent")
					try:
						info["conflicts"]=config.get("FLAVOUR","conflicts")
					except:
						info["conflicts"]=None
					try:
						test=config.get("FLAVOUR","remove")
						info["isManaged"]=False
					except:
						info["isManaged"]=True	
				else:
					info["installCmd"]=None
					info["removeCmd"]=None
					info["parent"]="root"
					info["conflicts"]=None
					info["isManaged"]=False
				if os.path.exists(os.path.join(self.banners,info["pkg"]+".png")):
					info["banner"]=os.path.join(self.banners,info["pkg"]+".png")
				else:
					info["banner"]=os.path.join(self.banners,"default.png")
				return info
				
		except Exception as e:
			return None

	#def loadFile

	def getSupportedFlavour(self):

		self.parentsWithMeta=[]

		for item in sorted(os.listdir(self.supportedFlavours)):
			if os.path.isfile(os.path.join(self.supportedFlavours,item)):
				tmpInfo=self.loadFile(os.path.join(self.supportedFlavours,item))
				if tmpInfo!=None:
					if tmpInfo["type"]=="child":
						status=self.isInstalled(tmpInfo["pkg"])
						baseAptCmd = "apt-cache policy %s "%tmpInfo["pkg"]
						p=subprocess.Popen([baseAptCmd],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)	
						output=p.communicate()[0]
						
						if type(output) is bytes:
							output=output.decode()

						if tmpInfo["pkg"] not in output:
							available=False
						else:	
							version=output.split("\n")[4]
							if version !='':
								available=True
							else:
								available=False
					else:
						available=True
						status=None
					
					if available:
						tmp={}
						tmp["pkgId"]=tmpInfo["id"]
						tmp["pkg"]=tmpInfo["pkg"]
						tmp["name"]=tmpInfo["name"]
						tmp["type"]=tmpInfo["type"]
						if tmp["type"]=="child":
							tmp["status"]=status
						else:
							tmp["status"]="available"
						tmp["banner"]=tmpInfo["banner"]
						tmp["showSpinner"]=False
						tmp["showAction"]=-1
						tmp["isExpanded"]=False
						tmp["isVisible"]=True
						tmp["flavourParent"]=tmpInfo["parent"]
						tmp["conflicts"]=tmpInfo["conflicts"]
						tmp["resultProcess"]=-1
						if tmp["type"]=="child":
							if tmp["pkg"] in self.flavoursBase:
								if status=="installed":
									tmp["isManaged"]=False
								else:
									tmp["isManaged"]=tmpInfo["isManaged"]
							else:
								tmp["isManaged"]=tmpInfo["isManaged"]
						else:
							tmp["isManaged"]=tmpInfo["isManaged"]
						if tmp["type"]=="child":
							if tmp["flavourParent"] not in self.parentsWithMeta:
								self.parentsWithMeta.append(tmp["flavourParent"])
							if status=="installed":
								tmp["isChecked"]=True
								tmp["showAction"]=0
								self.totalPackages+=1
								self.pkgsInstalled.append(tmp["pkg"])
							else:
								tmp["isChecked"]=False
								self.totalPackages+=1
								
						else:
							tmp["isChecked"]=False
						if tmp["pkg"] not in self.nonExpandedParent:
							self.nonExpandedParent.append(tmp["pkg"])
						self.flavoursData.append(tmp)
						if tmpInfo["type"]=="child":
							self.flavoursInfo[tmpInfo["pkg"]]={}
							self.flavoursInfo[tmpInfo["pkg"]]["installCmd"]=tmpInfo["installCmd"]
							self.flavoursInfo[tmpInfo["pkg"]]["removeCmd"]=tmpInfo["removeCmd"]
							self.flavoursInfo[tmpInfo["pkg"]]["banner"]=tmpInfo["banner"]
							if tmpInfo["conflicts"]!=None:
								self.flavoursInfo[tmpInfo["pkg"]]["conflicts"]=tmpInfo["conflicts"].split(",")
							else:
								self.flavoursInfo[tmpInfo["pkg"]]["conflicts"]=[]

		for item in self.flavoursData:
			if item["type"]=="parent":
				if item["pkg"] not in self.parentsWithMeta:
					item["isVisible"]=False
					if item["pkg"] in self.nonExpandedParent:
						self.nonExpandedParent.remove(item["pkg"])

		self.flavoursData=sorted(self.flavoursData,key=lambda k:k["pkgId"],reverse=False)

	#def getSupportedFlavour	
	
	def isInstalled(self,pkg):
		
		p=subprocess.Popen(["dpkg-query -W -f='${db:Status-Status}' %s"%pkg],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		output=p.communicate()[0]

		if type(output) is bytes:
			output=output.decode()
		
		if output=="installed":
			return "installed"
			
		return "available"
		
	#def isInstalled

	def manageExpansionList(self,action):

		if action=="expand":
			expand=True
		else:
			expand=False

		for item in self.flavoursData:
			tmp=[]
			tmp=[item["pkg"],"isExpanded",expand]
			self.onExpandedParent(tmp)

	#def manageExpansioList

	def onExpandedParent(self,info):

		tmpParam={}
		tmpParam[info[1]]=info[2]
		
		if info[1]=="isExpanded":
			if not info[2]:
				if info[0] not in self.nonExpandedParent:
					self.nonExpandedParent.append(info[0])
			else:
				if info[0] in self.nonExpandedParent:
					self.nonExpandedParent.remove(info[0])
					
		if len(self.nonExpandedParent)==len(self.flavoursData):
			self.allUnExpanded=True
		else:
			self.allUnExpanded=False

		self._updateFlavoursModel(tmpParam,info[0])			
	
	#def onExpandedParent

	def onCheckedPackages(self,pkg,isChecked):

		if not isChecked:
			if pkg in self.pkgsInstalled:
				if pkg not in self.wantToRemove:
					self.wantToRemove.append(pkg)
		else:
			if pkg in self.wantToRemove:
				self.wantToRemove.remove(pkg)

		self._managePkgSelected(pkg,isChecked)
		self._updateCheckedFlavours(pkg,isChecked)

		self._checkIncompatible(pkg,isChecked)
		
	def _checkIncompatible(self,pkg,isChecked):

		conflicts=self.flavoursInfo[pkg]["conflicts"]
		
		if len(conflicts)>0:
			if isChecked:
				for item in conflicts:
					self._managePkgSelected(item,False,True)
					self._updateCheckedFlavours(item,False)
			else:
				for item in conflicts:
					if item in self.pkgsInstalled:	
						self._managePkgSelected(item,True)
						if item not in self.wantToRemove:
							self._updateCheckedFlavours(item,True)			

	#def _checkIncompatible

	def _updateCheckedFlavours(self,pkg,isChecked):

		tmpParam={}
		showAction=-1
		tmpParam["isChecked"]=isChecked
		for item in self.flavoursData:
			if item["pkg"]==pkg:
				if item["status"]=="available":
					if isChecked:
						showAction=2
				else:
					if not isChecked:
						showAction=1
					else:
						showAction=0
				break
						
		tmpParam["showAction"]=showAction
		
		self._updateFlavoursModel(tmpParam,pkg)			
	
	#def _updateCheckedFlavours

	def _managePkgSelected(self,pkg,install,toConflict=False):

		if install:
			if pkg not in self.pkgsInstalled:
				if pkg not in self.flavourSelectedToInstall:
					self.flavourSelectedToInstall.append(pkg)
			else:
				abort=False
				if toConflict:
					if pkg in self.wantToRemove:
						abort=True
				if not abort:
					if pkg not in self.wantToRemove:
						if pkg in self.flavourSelectedToRemove:
							self.flavourSelectedToRemove.remove(pkg)
			
		else:
			if pkg in self.pkgsInstalled:
				if pkg not in self.flavourSelectedToRemove:
					self.flavourSelectedToRemove.append(pkg)
			else:
				if pkg in self.flavourSelectedToInstall:
					self.flavourSelectedToInstall.remove(pkg)
		
	#def _managePkgSelected

	def initLog(self,autoRemove):

		msgLog="------------------------------------------------------\n"+"LLIUREX-FLAVOURS-SELECTOR STARTING AT "+datetime.datetime.today().strftime("%d/%m/%y %H:%M:%S")+"\n------------------------------------------------------"
		self.log(msgLog)
		msgLog="- Installed flavours: %s"%str(self.pkgsInstalled)
		self.log(msgLog)
		msgLog="- Flavours selected to install: %s"%str(self.flavourSelectedToInstall)
		self.log(msgLog)
		msgLog="- Flavours selected to remove: %s"%str(self.flavourSelectedToRemove)
		self.log(msgLog)
		msgLog="- Launch autoremove: %s"%str(autoRemove)
		self.log(msgLog)

	#def initLog

	def checkInternetConnection(self):

		self.checkingUrl1_t=threading.Thread(target=self._checkingUrl1)
		self.checkingUrl2_t=threading.Thread(target=self._checkingUrl2)
		self.checkingUrl1_t.daemon=True
		self.checkingUrl2_t.daemon=True
		self.checkingUrl1_t.start()
		self.checkingUrl2_t.start()

	#def checkInternetConnection

	def _checkingUrl1(self):

		self.connection=self._checkConnection(self.urltocheck1)
		self.firstConnection=self.connection[0]

	#def _checkingUrl1	

	def _checkingUrl2(self):

		self.connection=self._checkConnection(self.urltocheck2)
		self.secondConnection=self.connection[0]

	#def _checkingUrl2

	def _checkConnection(self,url):
		
		result=[]
		try:
			res=urllib.request.urlopen(url)
			result.append(True)
			
		except Exception as e:
			result.append(False)
			result.append(str(e))
		
		msgLog="- Check Internet connection: %s - %s"%(url,str(result))
		self.log(msgLog)

		return result	

	#def _checkConnection

	def getResultCheckConnection(self):

 		self.endCheck=False
 		error=False
 		urlError=False
 		self.retConnection=[False,""]

 		if self.checkingUrl1_t.is_alive() and self.checkingUrl2_t.is_alive():
 			pass
 		else:
 			if not self.firstConnection and not self.secondConnection:
 				if self.checkingUrl1_t.is_alive() or self.checkingUrl2_t.is_alive():
 					pass
 				else:
 					self.endCheck=True
 			else:
 				self.endCheck=True

 		if self.endCheck:
 			if not self.firstConnection and not self.secondConnection:
 				error=True
 				msgError=FlavourSelectorManager.ERROR_INTERNET_CONNECTION
 				self.retConnection=[error,msgError]

	#def getResultCheckConnection

	def initInstallProcess(self):

		self.updateReposLaunched=False
		self.updateReposDone=False
		self.errorInConflicts=False

	#def initInstallProcess

	def initPkgInstallProcess(self,pkg):

		self.installAppLaunched=False
		self.installAppDone=False
		self.checkInstallLaunched=False
		self.checkInstallDone=False
		self._initAutoRemoveProcess()
		self.flavourSelected=self.flavourSelectedToInstall
		self._initProcessValues(pkg)

	#def initPkgInstallProcess

	def getUpdateReposCommand(self):

		command="apt-get update"
		length=len(command)

		if length>0:
			command=self._createProcessToken(command,"updaterepos")
		else:
			self.updateReposDone=True

		return command

	#def getUpdateReposCommand

	def getInstallCommand(self,pkg):

		command=""
		conflictDetected=False
		conflicts=self.flavoursInfo[pkg]["conflicts"]
		
		for item in conflicts:
			if item in self.pkgsInstalled:
				self.errorInConflicts=True
				conflictDetected=True
				break
				
		if not conflictDetected:
			command="DEBIAN_FRONTEND=noninteractive %s"%self.flavoursInfo[pkg]["installCmd"]
		
		length=len(command)

		if length>0:
			command=self._createProcessToken(command,"install")
		else:
			self.installAppDone=True

		return command

	#def getInstallCommand

	def checkInstall(self,pkg):

		self.feedBackCheck=[True,"",""]
		self.status=self.isInstalled(pkg)

		self._updateProcessModelInfo(pkg,'install',self.status)
		
		if self.status!="installed":
			msgCode=FlavourSelectorManager.ERROR_INSTALL_INSTALL
			typeMsg="Error"
			self.feedBackCheck=[False,msgCode,typeMsg]
		else:
			msgCode=FlavourSelectorManager.SUCCESS_INSTALL_PROCESS
			typeMsg="Ok"
			self.feedBackCheck=[True,msgCode,typeMsg]
		
		self.checkInstallDone=True
		msgLog="- Installation of %s. Result: %s"%(pkg,typeMsg)
		self.log(msgLog)

	#def checkInstall

	def isAllInstalled(self):

		pkgAvailable=0
		if self.totalPackages==len(self.pkgsInstalled):
			return [True,False]
		else:
			pkgAvailable=self.totalPackages-len(self.pkgsInstalled)
			if pkgAvailable==self.totalPackages:
				return [False,True]
			else:
				return [False,False]

	#def isAllInstalled

	def preUninstallProcess(self):

		self.disableMetaProtectionLaunched=False
		self.disableMetaProtectionDone=False
		self.enableMetaProtectionLaunched=False
		self.enableMetaProtectionDone=False
		self._initAutoRemoveProcess()

	#def preUninstallProcess

	def initUnInstallProcess(self,pkg):

		self.removePkgLaunched=False
		self.removePkgDone=False	
		self.checkRemoveLaunched=False
		self.checkRemoveDone=False
		self.flavourSelected=self.flavourSelectedToRemove
		self._initProcessValues(pkg)

	#def initUnInstallProcess

	def _initAutoRemoveProcess(self):

		self.autoRemoveLaunched=False
		self.autoRemoveDone=False

	#def _initAutoRemoveProcess

	def _initProcessValues(self,pkg):

		for item in self.flavoursData:
			if item["pkg"]==pkg:
				tmpParam={}
				tmpParam["resultProcess"]=-1
				if item["pkg"] in self.flavourSelected:
					tmpParam["showSpinner"]=True
					self._updateFlavoursModel(tmpParam,item["pkg"])

	#def _initProcessValues

	def getDisableProtectionCommand(self):

		command="dpkg-unlocker-cli disableprotection -u"
		length=len(command)

		if length>0:
			command=self._createProcessToken(command,"disablemetaprotection")
		else:
			self.disableMetaProtectionDone=True

		return command

	#def getDisableProtectionCommand

	def getUnInstallCommand(self,pkg):

		command=""
		command="DEBIAN_FRONTEND=noninteractive %s"%self.flavoursInfo[pkg]["removeCmd"]
		length=len(command)

		if length>0:
			command=self._createProcessToken(command,"uninstall")
		else:
			self.installAppDone=True

		return command

	#def getUnInstallCommand

	def checkRemove(self,pkg):

		self.feedBackCheck=[True,"",""]
		self.status=self.isInstalled(pkg)

		self._updateProcessModelInfo(pkg,'uninstall',self.status)
		
		if self.status!="available":
			msgCode=FlavourSelectorManager.ERROR_UNINSTALL_UNINSTALL
			typeMsg="Error"
			self.feedBackCheck=[False,msgCode,typeMsg]
		else:
			msgCode=FlavourSelectorManager.SUCCESS_UNINSTALL_PROCESS
			typeMsg="Ok"
			self.feedBackCheck=[True,msgCode,typeMsg]
		
		msgLog="- Uninstallation of %s. Result: %s"%(pkg,typeMsg)
		self.log(msgLog)

		self.checkRemoveDone=True

	#def checkRemove

	def getEnableProtectionCommand(self):

		command="dpkg-unlocker-cli enableprotection -u"
		length=len(command)

		if length>0:
			command=self._createProcessToken(command,"enablemetaprotection")
		else:
			self.enableMetaProtectionDone=True

		return command

	#def getEnableProtectionCommand

	def getAutoRemoveCommand(self):

		command="apt-get autoremove -y"
		length=len(command)

		if length>0:
			command=self._createProcessToken(command,"autoremove")
		else:
			self.enableMetaProtectionDone=True

		return command

	#def getAutoRemoveCommand

	def _updateProcessModelInfo(self,pkg,action,result):

		for item in self.flavoursInfo:
			if item==pkg and item in self.flavourSelected:
				tmpParam={}
				if action=="install":
					if result=="installed":
						if pkg not in self.pkgsInstalled:
							self.pkgsInstalled.append(pkg)
						tmpParam["showAction"]=0
						tmpParam["resultProcess"]=-1
						#tmpParam["banner"]="%s_OK"%self.flavoursInfo[pkg]["banner"]
					else:
						tmpParam["resultProcess"]=1
						tmpParam["showAction"]=-1
						tmpParam["isChecked"]=False
				elif action=="uninstall":
					if result=="available":
						if pkg in self.pkgsInstalled:
							self.pkgsInstalled.remove(pkg)
						tmpParam["resultProcess"]=0
						tmpParam["showAction"]=-1
						tmpParam["banner"]=self.flavoursInfo[pkg]["banner"]
					else:
						tmpParam["resultProcess"]=1
						tmpParam["showAction"]=0
						tmpParam["isChecked"]=True

				tmpParam["status"]=result
				tmpParam["showSpinner"]=False
				
				self._updateFlavoursModel(tmpParam,item)
	
	#def _updateProcessModelInfo

	def _updateFlavoursModel(self,param,pkg):

		for item in self.flavoursData:
			if item["pkg"]==pkg:
				for element in param:
					if item[element]!=param[element]:
						item[element]=param[element]
				break

	#def _updateFlavoursModel

	def _clearCache(self):

		clear=False
		versionFile="/root/.lliurex-flavours-selector.conf"
		cachePath1="/root/.cache/lliurex-flavours-selector"
		installedVersion=self.getPackageVersion()

		try:
			if not os.path.exists(versionFile):
				with open(versionFile,'w') as fd:
					fd.write(installedVersion)
					fd.close()

				clear=True

			else:
				with open(versionFile,'r') as fd:
					fileVersion=fd.readline()
					fd.close()

				if fileVersion!=installedVersion:
					with open(versionFile,'w') as fd:
						fd.write(installedVersion)
						fd.close()
					clear=True
			
			if clear:
				if os.path.exists(cachePath1):
					shutil.rmtree(cachePath1)
		except:
			pass

	#def _clearCache

	def getPackageVersion(self):

		packageVersionFile="/var/lib/zero-lliurex-flavours/version"
		pkgVersion=""

		if os.path.exists(packageVersionFile):
			with open(packageVersionFile,'r') as fd:
				pkgVersion=fd.readline()
				fd.close()

		return pkgVersion

	#def getPackageVersion

	def _createProcessToken(self,command,action):

		cmd=""
		
		if action=="updaterepos":
			self.tokenUpdaterepos=tempfile.mkstemp('_updaterepos')	
			removeTmp=' rm -f %s'%self.tokenUpdaterepos[1]	
		elif action=="install":
			self.tokenInstall=tempfile.mkstemp('_install')
			removeTmp=' rm -f %s'%self.tokenInstall[1]
		elif action=="disablemetaprotection":
			self.tokenDisableMetaProtection=tempfile.mkstemp('_disablemetaprotection')
			removeTmp=' rm -f %s'%self.tokenDisableMetaProtection[1]
		elif action=="uninstall":
			self.tokenUnInstall=tempfile.mkstemp('_uninstall')
			removeTmp=' rm -f %s'%self.tokenUnInstall[1]
		elif action=="enablemetaprotection":
			self.tokenEnableMetaProtection=tempfile.mkstemp('_enablemetaprotection')
			removeTmp=' rm -f %s'%self.tokenEnableMetaProtection[1]
		elif action=="autoremove":
			self.tokenAutoRemove=tempfile.mkstemp("_autoremove")
			removeTmp=' rm -f %s'%self.tokenAutoRemove[1]

		cmd='%s ;stty -echo;%s\n'%(command,removeTmp)
		if cmd.startswith(";"):
			cmd=cmd[1:]

		return cmd

	#def _createProcessToken

	def log(self,msgLog):

		logFile="/var/log/lliurex-flavours-selector.log"
		with open(logFile,"a+") as fd:
			fd.write("%s\n"%msgLog)

	#def log	

#class FlavourSelectorManager
