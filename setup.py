#!/usr/bin/env python3
#
# $Id: setup.py,v 1.32 2010/10/17 15:47:21 ghantoos Exp $
#
#    Copyright (C) 2008-2009  Ignace Mouzannar (ghantoos) <ghantoos@ghantoos.org>
#
#    This file is part of lshell
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from distutils.core import setup
from edupals.i18n import poinstaller
import sys
import os

if __name__ == '__main__':
	
	pinstaller_legacy = poinstaller.PoInstaller('translations/lliurex-flavours-selector-legacy','lliurex-flavours-selector-legacy','')
	pinstaller_legacy.build()
	polist_legacy = pinstaller_legacy.setup_install()
	pinstaller = poinstaller.PoInstaller('translations/lliurex-flavours-selector','lliurex-flavours-selector','')
	pinstaller.build()
	polist = pinstaller.setup_install()
	listdir_banners_legacy=map(lambda x:os.path.join('lliurex-flavours-selector-legacy','data-files','banners',x),os.listdir('lliurex-flavours-selector-legacy/data-files/banners'))
	listdir_supportedflavours_legacy=map(lambda x:os.path.join('lliurex-flavours-selector-legacy','data-files','supported-flavours',x),os.listdir('lliurex-flavours-selector-legacy/data-files/supported-flavours'))
	listdir_banners=map(lambda x:os.path.join('lliurex-flavours-selector','data-files','banners',x),os.listdir('lliurex-flavours-selector/data-files/banners'))
	listdir_supportedflavours=map(lambda x:os.path.join('lliurex-flavours-selector','data-files','supported-flavours',x),os.listdir('lliurex-flavours-selector/data-files/supported-flavours'))

	setup(name='zero-lliurex-flavours',
		version='0.1',
		description='LliureX Flavours Selector',
		long_description="""""",
		author='Lliurex Team',
		author_email='juapesai@hotmail.com',
		maintainer='Juan Ramon Pelegrina',
		maintainer_email='juapesai@hotmail.com',
		keywords=['software','server','sites'],
		url='http://www.lliurex.net',
		license='GPL',
		platforms='UNIX',
		packages = ['lliurexflavourselectorlegacy','lliurexflavourselector'],
		package_dir = {'lliurexflavourselectorlegacy':'lliurex-flavours-selector-legacy/python3-lliurexflavourselector','lliurexflavourselector':'lliurex-flavours-selector/python3-lliurexflavourselector'},
		package_data = {'lliurexflavourselectorlegacy':['rsrc/*'],'lliurexflavourselector':['rsrc/*']},
		data_files = [('sbin',['lliurex-flavours-selector-legacy/lliurex-flavours-selector-legacy','lliurex-flavours-selector/lliurex-flavours-selector']),
			      ('share/lliurex-flavours-selector-legacy/banners',listdir_banners_legacy), ('share/lliurex-flavours-selector/banners',listdir_banners),
   			      ('share/lliurex-flavours-selector-legacy/supported-flavours',listdir_supportedflavours_legacy),('share/lliurex-flavours-selector/supported-flavours',listdir_supportedflavours),
   			      ] + polist_legacy + polist ,
		classifiers=[
			'Development Status :: 4 - Beta',
			'Environment :: Console'
			'Intended Audience :: End Users',
			'License :: OSI Approved :: GNU General Public License v3',
			'Operating System :: POSIX',
			'Programming Language :: Python',
			'Topic :: Software',
			'Topic :: Install apps',
			],
	)
	pinstaller.clean() 
