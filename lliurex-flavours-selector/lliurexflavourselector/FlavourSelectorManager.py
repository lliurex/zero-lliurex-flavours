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
from concurrent.futures import ThreadPoolExecutor

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
	MSG_FEEDBACK_CONFIGURATION_CART=12

	def __init__(self):

		self.supportedFlavours=os.path.join(BASE_DIR,"supported-flavours")
		self.banners=os.path.join(BASE_DIR,"banners")
		self.flavoursData=[]
		self.flavoursMap={}
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
		self.flavoursBase=["lliurex-meta-desktop","lliurex-meta-gva"]
		self.tagsPath="/etc/lliurex-auto-upgrade/tags"
		self.tagsToRemove=[]
		self.flavourReferenceForTags="lliurex-meta-gva"
		self._isRunPkexec()
		self._getSessionLang()
		self._clearCache()
				
	#def __init__

	def _isRunPkexec(self):

		if 'PKEXEC_UID' not in os.environ:
			self.runPkexec=False

	#def _isRunPkexec
	
	def _getSessionLang(self):

		tmpLang=os.environ["LANGUAGE"]
		if tmpLang!="":
			tmpLang=tmpLang.split(":")
		if len(tmpLang)>0:
			self.sessionLang=tmpLang[0]
		else:
			self.sessionLang=os.environ["LANG"]

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
				if 'ca' in self.sessionLang:
					info["name"]=config.get("FLAVOUR","name[ca@valencia]",fallback=config.get("FLAVOUR","name"))
				elif 'es' in self.sessionLang:
					info["name"]=config.get("FLAVOUR","name[es]",fallback=config.get("FLAVOUR","name"))
				else:
					info["name"]=config.get("FLAVOUR","name")

				info["type"]=config.get("FLAVOUR","type")
				if info["type"]=="child":
					info["installCmd"]=config.get("FLAVOUR","installCmd")
					info["removeCmd"]=config.get("FLAVOUR","removeCmd")
					info["parent"]=config.get("FLAVOUR","parent")
					info["conflicts"]=config.get("FLAVOUR","conflicts",fallback=None)
					info["tags"]=config.get("FLAVOUR","tags",fallback=None)
					info["isManaged"]=not config.has_option("FLAVOUR","remove")
				else:
					info["installCmd"]=None
					info["removeCmd"]=None
					info["parent"]="root"
					info["conflicts"]=None
					info["isManaged"]=False

				banner_path=os.path.join(self.banners,f"{info['pkg']}.png")
				if os.path.exists(banner_path):
					info["banner"]=banner_path
				else:
					info["banner"]=os.path.join(self.banners,"default.png")
				return info
				
		except Exception as e:
			return None

	#def loadFile

	def getSupportedFlavour(self):

		self.parentsWithMeta=[]

		for item in sorted(os.listdir(self.supportedFlavours)):
			filePath=os.path.join(self.supportedFlavours,item)

			if not os.path.isfile(filePath):
				continue
			
			tmpInfo=self.loadFile(filePath)
			
			if tmpInfo is None:
				continue

			if tmpInfo["type"]=="child":
				status=self.isInstalled(tmpInfo["pkg"])
				baseAptCmd = f"apt-cache policy {tmpInfo['pkg']}"
				p=subprocess.Popen([baseAptCmd],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)	
				output=p.communicate()[0]
				result=subprocess.run(
					["apt-cache","policy",tmpInfo["pkg"]],
					stdout=subprocess.PIPE,
					stderr=subprocess.PIPE,
					text=True
					)
				
				output=result.stdout

				if tmpInfo["pkg"] not in output:
					available=False
				else:
					lines=output.split("\n")
					if len(lines)>4 and lines[4] !="":
						available=True
					else:
						available=False	
			else:
				available=True
				status=None
			
			if not available:
				continue
				
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
					tmp["isManaged"]=(status!="installed")
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
				self.flavoursInfo[tmpInfo["pkg"]]={
					"installCmd":tmpInfo["installCmd"],
					"removeCmd":tmpInfo["removeCmd"],
					"banner":tmpInfo["banner"],
					"conflicts":tmpInfo["conflicts"].split(",") if tmpInfo["conflicts"] else [],
					"tags":tmpInfo["tags"].split(",") if tmpInfo["tags"] else []
				}
					
		for item in self.flavoursData:
			if item["type"]=="parent":
				if item["pkg"] not in self.parentsWithMeta:
					item["isVisible"]=False
					if item["pkg"] in self.nonExpandedParent:
						self.nonExpandedParent.remove(item["pkg"])

		self.flavoursData=sorted(self.flavoursData,key=lambda k:k["pkgId"],reverse=False)
		self.flavoursMap = {item["pkg"]: item for item in self.flavoursData if "pkg" in item}

	#def getSupportedFlavour	
	
	def isInstalled(self,pkg):
		
		cmd=["dpkg-query", "-W","-f=${db:Status-Status}", pkg]
		result=subprocess.run(
			cmd,
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
			text=True
		)

		output=result.stdout

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
		
		if not conflicts:
			return

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

		showAction=-1
		item=self.flavoursMap.get(pkg)

		if item:
			if item["status"]=="available":
				showAction=2 if isChecked else -1
			else:
				showAction=0 if isChecked else 1
							
		tmpParam={
			"isChecked":isChecked,
			"showAction":showAction
		}
		
		self._updateFlavoursModel(tmpParam,pkg)			
	
	#def _updateCheckedFlavours

	def _managePkgSelected(self,pkg,install,toConflict=False):

		if install:
			if pkg not in self.pkgsInstalled:
				if pkg not in self.flavourSelectedToInstall:
					self.flavourSelectedToInstall.append(pkg)
				return
	
			if toConflict and pkg in wantToRemove:
				return
	
			if pkg not in self.wantToRemove and pkg in self.flavourSelectedToRemove:
				self.flavourSelectedToRemove.remove(pkg)

			return
			
		if pkg in self.pkgsInstalled:
			if pkg not in self.flavourSelectedToRemove:
				self.flavourSelectedToRemove.append(pkg)
		else:
			if pkg in self.flavourSelectedToInstall:
				self.flavourSelectedToInstall.remove(pkg)
		
	#def _managePkgSelected

	def initLog(self,autoRemove,cartConfiguration,selectedCart):

		msgLog=f"------------------------------------------------------\nLLIUREX-FLAVOURS-SELECTOR STARTING AT {datetime.datetime.today().strftime("%d/%m/%y %H:%M:%S")}\n------------------------------------------------------"
		self.log(msgLog)
		msgLog=f"- Installed flavours: {self.pkgsInstalled}"
		self.log(msgLog)
		msgLog=f"- Flavours selected to install: {self.flavourSelectedToInstall}"
		self.log(msgLog)
		msgLog=f"- Flavours selected to remove: {self.flavourSelectedToRemove}"
		self.log(msgLog)
		msgLog=f"- Launch autoremove: {autoRemove}"
		self.log(msgLog)
		if cartConfiguration:
			self.configureCart=cartConfiguration
			self.selectedCart=selectedCart
			msgLog=f"- Launch cart configuration: {cartConfiguration} - Selected cart: {selectedCart}"
			self.log(msgLog)

	#def initLog

	def checkInternetConnection(self):

		self.executor=ThreadPoolExecutor(max_workers=2)
		self.future1=self.executor.submit(self._checkConnection,self.urltocheck1)
		self.future2=self.executor.submit(self._checkConnection,self.urltocheck2)

	#def checkInternetConnection

	def _checkConnection(self,url):
		
		result=[]
		try:
			res=urllib.request.urlopen(url,timeout=10)
			result.append(True)
			
		except Exception as e:
			result.append(False)
			result.append(str(e))
		
		msgLog=f"- Check Internet connection: {url} - {result}"
		self.log(msgLog)

		return result	

	#def _checkConnection

	def getResultCheckConnection(self):

 		self.endCheck=False
 		self.retConnection=[False,""]

 		if not (self.future1.done() and not self.future2.done()):
 			self.firstConnection=self.future1.result() if self.future1.done() else [False]
 			self.secondConnection=self.future2.result() if self.future2.done() else [False]

 			if self.firstConnection[0] or self.secondConnection[0]:
 				self.endCheck=True
 			return

 		self.firstConnection=self.future1.result()
 		self.secondConnection=self.future2.result()
 		self.endCheck=True

 		if not self.firstConnection[0] and not self.secondConnection[0]:
 			self.retConnection=[True,FlavourSelectorManager.ERROR_INTERNET_CONNECTION]

 		self.executor.shutdown(wait=False)
 		
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
		self.configureCartLaunched=False
		self.configureCartDone=False
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
		length=0
		conflictDetected=False
		conflicts=self.flavoursInfo[pkg]["conflicts"]
		
		for item in conflicts:
			if item in self.pkgsInstalled:
				self.errorInConflicts=True
				conflictDetected=True
				break
				
		if not conflictDetected:
			command=f"DEBIAN_FRONTEND=noninteractive {self.flavoursInfo[pkg]["installCmd"]}"
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
		msgLog=f"- Installation of {pkg}. Result: {typeMsg}"
		self.log(msgLog)

	#def checkInstall

	def getConfigurationCartCommand(self):

		command=""
		length=0
		if self.configureCart and self.selectedCart>1 and self.isInstalled("lliurex-meta-wifi-alu"):
			command=f"lliurex-client-register-cli setcart {self.selectedCart} -u"
			length=len(command)

		if length>0:
			command=self._createProcessToken(command,"configureCart")
		else:
			self.configureCartDone=True

		return command

	#def getConfigurationCartCommand

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
		command=f"DEBIAN_FRONTEND=noninteractive {self.flavoursInfo[pkg]["removeCmd"]}"
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
			self._manageTags(pkg)
		
		msgLog=f"- Uninstallation of {pkg}. Result: {typeMsg}"
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


		if pkg not in self.flavoursInfo or pkg not in self.flavourSelected:
			return

		tmpParam={}

		if action=="install":
			if result=="installed":
				if pkg not in self.pkgsInstalled:
					self.pkgsInstalled.append(pkg)
				tmpParam["showAction"]=0
				tmpParam["resultProcess"]=-1
				if pkg in self.flavoursBase:
					tmpParam["isManaged"]=False
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
		
		self._updateFlavoursModel(tmpParam,pkg)
	
	#def _updateProcessModelInfo

	def _updateFlavoursModel(self,param,pkg):

		item=self.flavoursMap.get(pkg)
		
		if item:
			for element in param:
				if item[element]!=param[element]:
					item[element]=param[element]

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
			self.tokenUpdaterepos=self._getTempFile(action)	
			removeTmp=f' rm -f {self.tokenUpdaterepos}'
		elif action=="install":
			self.tokenInstall=self._getTempFile(action)
			removeTmp=f' rm -f {self.tokenInstall}'
		elif action=="configureCart":
			self.tokenConfigureCart=self._getTempFile(action)
			removeTmp=f' rm -f {self.tokenConfigureCart}'
		elif action=="disablemetaprotection":
			self.tokenDisableMetaProtection=self._getTempFile(action)
			removeTmp=f' rm -f {self.tokenDisableMetaProtection}'
		elif action=="uninstall":
			self.tokenUnInstall=self._getTempFile(action)
			removeTmp=f' rm -f {self.tokenUnInstall}'
		elif action=="enablemetaprotection":
			self.tokenEnableMetaProtection=self._getTempFile(action)
			removeTmp=f' rm -f {self.tokenEnableMetaProtection}'
		elif action=="autoremove":
			self.tokenAutoRemove=self._getTempFile(action)
			removeTmp=f' rm -f {self.tokenAutoRemove}'

		cmd=f'{command} ;stty -echo;{removeTmp}\n'
		if cmd.startswith(";"):
			cmd=cmd[1:]

		return cmd

	#def _createProcessToken

	def _getTempFile(self,action):

		suffixName=f"_{action}"
		tmpFile=tempfile.NamedTemporaryFile(suffix=suffixName,delete=False)
		tmpFile.close()

		return tmpFile.name

	#def _getTempFile

	def log(self,msgLog):

		logFile="/var/log/lliurex-flavours-selector.log"
		with open(logFile,"a+") as fd:
			fd.write(f"{msgLog}\n")

	#def log

	def _manageTags(self,pkg):

		if not os.path.exists(self.tagsPath):
			return
		
		for item in self.flavoursInfo[pkg]["tags"]:
			if item not in self.tagsToRemove:
				self.tagsToRemove.append(item)

	#def _manageTags

	def updateTags(self):

		if self.flavourReferenceForTags not in self.pkgsInstalled:
			return

		if not os.path.exists(self.tagsPath):
			return 

		for pkg in self.pkgsInstalled:
			for tag in self.flavoursInfo[pkg]["tags"]:
				tmpTag=os.path.join(self.tagsPath,tag)
				if not os.path.exists(tmpTag):
					cmd=f"touch {tmpTag}"
					with open(tmpTag,'a'):
						os.utime(tmpTag,None)

		for item in self.tagsToRemove:
			tmpTag=os.path.join(self.tagsPath,item)
			if os.path.exists(tmpTag):
				os.remove(tmpTag)

	#ef updateTags	

#class FlavourSelectorManager
