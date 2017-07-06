# -*- coding: utf-8 -*-
"""
命令行工具类

Author: liyan
File: util.py

Features:
1. 本地命令执行： (cost, out, err) = Command.excute(cmd, dry_run=False)
2. 系统平台判断： Command.isXXXSystem()
3. 当前版本判断： Command.git_ver(dir)/Command.svn_ver(dir)
4. 基于android工具的出apk包的执行命令: Command.
5. xcode 8.2+出ipa包的执行命令： Command.xcodebuild_ipa(project, scheme, export)

"""

import argparse
import codecs, os, sys
from subprocess import Popen, PIPE

import time #计算命令执行时长
import logging

import platform


class Command(object):
	# config a log
	logging.basicConfig(filename='./excute.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
	logging.info('launch on %s'%platform.system())

	@staticmethod
	def isMacSystem():
		return 'Darwin' in platform.system()

	@staticmethod
	def isLinuxSystem():
		return 'Linux' in platform.system()

	@staticmethod
	def isWindowsSystem():
		return 'Windows' in platform.system()

	@staticmethod
	def excute(cmd, dry_run=False):
		start_point = time.time()
		if dry_run: 
			logging.warn('dry-run mode on[%s]'%cmd)
			return (0, cmd, '')
		else:
			logging.debug(cmd)
		process = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
		out, err = process.communicate()
		if len(err) > 0:
			logging.error('cmd=%s, err=%s' %(cmd, err))
		return (time.time()-start_point, out, err)

	@staticmethod
	def git_ver(git_dir):
		"""pull the latest content and get version
		git revision cmd: git rev-list --count HEAD
		"""
		cmd = 'git -C %s pull' % git_dir
		(cost, out, err) = Command.excute(cmd)
		if len(err) > 0:
			logging.error('excute[%s]: %s' %(cmd, err))
		cmd = 'git -C %s rev-list --count HEAD' % git_dir
		(cost, out, err) = Command.excute(cmd)
		if len(err) > 0:
			logging.error('excute[%s]: %s' %(cmd, err))
		if len(out) > 0:
			return out.strip('\n')
		else:
			return ''

	@staticmethod
	def svn_ver(svn_dir):
		"""pull the latest content and get version
		svn info <path> | grep "Last Changed Rev" | cut -d" " -f4
		svn info --show-item last-changed-revision <path>
		"""
		cmd = 'svn up %s' % svn_dir
		(cost, out, err) = Command.excute(cmd)
		if len(err) > 0:
			logging.error('excute[%s]: %s' %(cmd, err))
		cmd = 'svn info --show-item last-changed-revision %s' % svn_dir
		(cost, out, err) = Command.excute(cmd)
		if len(err) > 0:
			logging.error('excute[%s]: %s' %(cmd, err))
		if len(out) > 0:
			return out.strip()
		else:
			return ''

	@staticmethod
	def apk(project, target='android-21', is_release=True):
		"""基于android工具的出apk包的执行命令:
		project: 工程所在路径
		target: Target ID to set for the project
		"""
		build = 'debug'
		if is_release:
			build = 'release'
		update_project_cmd = 'android update project -l ../%s -p  %(project_dir)s -n MainActivity -t %(target_id)s' % {
			'project_dir': project, 
			'target_id': target
		}
		ant_cmd = 'ant -f %(project_dir)s/build.xml clean %(project_dir)s'% {
			'project_dir': project, 
			'build_config': build,
			'xcpretty': xcpretty
		}

	@staticmethod
	def xcodebuild_ipa(project, scheme, export, is_release=True, is_xcpretty=True):
		"""xcode 8.2+出ipa包的执行命令
		"""
		build = 'Debug'
		if is_release:
			build = 'Release'

		xcpretty = ''
		if is_xcpretty:
			xcpretty = '| xcpretty'
		
		archive='build/demo.xcarchive'
		
		archive_cmd='xcodebuild archive -project %(project_name)s -scheme %(scheme_name)s -configuration %(build_config)s -archivePath %(archive_path)s %(xcpretty)s' % {
			'project_name': project, 
			'scheme_name': scheme,
			'build_config': build,
			'archive_path': archive,
			'xcpretty': xcpretty
		}
		print archive_cmd
		(cost, out, err) = Command.excute(archive_cmd)
		print err

		export_cmd='xcodebuild -exportArchive -archivePath %(archive_path)s -exportPath %(export_path)s -exportOptionsPlist package.plist %(xcpretty)s' % {
			'export_path': export,
			'archive_path': archive,
			'xcpretty': xcpretty
		}
		print export_cmd
		(cost, out, err) = Command.excute(export_cmd)
		print err

def test():
	if Command.isMacSystem(): print 'launch on OS X!'
	if Command.isLinuxSystem(): print 'launch on Linux!'
	if Command.isWindowsSystem(): print 'launch on Windows!'

	try:
		print 'current dir git version =', Command.git_ver(".")
	except:
		pass

	if len(sys.argv) >1:
		print 'svn dir =', sys.argv[1], 'version =', Command.svn_ver(sys.argv[1])
	else:
		print 'add svn path'

if __name__ == '__main__':
	test()