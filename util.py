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
			'build_config': build
		}

	@staticmethod
	def xcodebuild_test(project, scheme, is_clean=True, is_xcpretty=True, report='junit'):
		"""xcodebuild 执行单元测试
		report: 使用xcpretty, 生成 JUnit 风格的测试报告(build/reports/junit.xml)
		"""
		if is_clean:
			(cost, out, err) = Command.excute('xcodebuild clean')
			print err

		xcpretty = ''
		if is_xcpretty:
			xcpretty = ' | xcpretty'
		if report == 'junit':
			xcpretty = ' | xcpretty -r junit'

		test_cmd='xcodebuild test -project %(project_name)s -scheme %(scheme_name)s -destination "platform=iOS Simulator,name=iPhone SE"%(xcpretty)s' % {
			'project_name': project, 
			'scheme_name': scheme,
			'xcpretty': xcpretty
		}
		print test_cmd
		(cost, out, err) = Command.excute(test_cmd)
		print err

	@staticmethod
	def xcodebuild_lib(project, scheme, is_clean=False, is_xcpretty=True):
		"""xcode 编译 Libary & 编译Framework
		Xcode: Build Settings -> Math-O Type: Static Libary
		See Also: http://wiki.li3huo.com/xcodebuild#Build_Library
		"""
		if is_clean:
			(cost, out, err) = Command.excute('xcodebuild clean')
			print err

		build = 'Release'
		xcpretty = ''
		if is_xcpretty:
			xcpretty = ' | xcpretty'
		
		# 分别生成手机和模拟器的lib
		logging.debug('分别生成手机和模拟器的lib...')
		for sdk, build_dir in (('iphoneos', 'arm'), ('iphonesimulator', 'x86')):
			build_cmd='xcodebuild build -project %(project_name)s -scheme %(scheme_name)s -configuration %(build_config)s only_active_arch=no defines_module=yes -sdk "%(sdk)s" CONFIGURATION_BUILD_DIR=build/%(build_dir)s%(xcpretty)s' % {
				'project_name': project, 
				'scheme_name': scheme,
				'build_config': build,
				'sdk': sdk,
				'build_dir': build_dir,
				'xcpretty': xcpretty
			}
			print build_cmd
			(cost, out, err) = Command.excute(build_cmd)
			print err

		# merge 2 lib as one
		logging.debug('merge 2 lib as one...')
		merge_cmd='lipo -create build/arm/%(scheme_name)s.framework/%(scheme_name)s build/x86/%(scheme_name)s.framework/%(scheme_name)s -output build/merge_lib' % {
			'scheme_name': scheme
		}
		print merge_cmd
		(cost, out, err) = Command.excute(merge_cmd)
		print err

		(cost, out, err) = Command.excute('mv build/merge_lib build/arm/%s.framework/%s' % (scheme, scheme) )
		print err

		(cost, out, err) = Command.excute('mv build/arm/%s.framework/ build/%s.framework' % (scheme, scheme) )
		print err

		logging.debug('验证framework包含的框架集，应该是"armv7 i386 x86_64 arm64"')
		(cost, out, err) = Command.excute('lipo -info build/%s.framework/%s' % (scheme, scheme) )
		print out, err
		logging.debug(out)

	@staticmethod
	def xcodebuild_ipa(project, scheme, export, is_clean=False, is_release=True, is_xcpretty=True):
		"""xcode 8.2+出ipa包的执行命令
		"""
		if is_clean:
			(cost, out, err) = Command.excute('xcodebuild clean')
			print err

		build = 'Debug'
		if is_release:
			build = 'Release'

		xcpretty = ''
		if is_xcpretty:
			xcpretty = ' | xcpretty'
		
		archive='build/%s.xcarchive'%scheme
		
		archive_cmd='xcodebuild archive -project %(project_name)s -scheme %(scheme_name)s -configuration %(build_config)s -archivePath %(archive_path)s%(xcpretty)s' % {
			'project_name': project, 
			'scheme_name': scheme,
			'build_config': build,
			'archive_path': archive,
			'xcpretty': xcpretty
		}
		print archive_cmd
		(cost, out, err) = Command.excute(archive_cmd)
		print err

		export_cmd='xcodebuild -exportArchive -archivePath %(archive_path)s -exportPath %(export_path)s -exportOptionsPlist package.plist%(xcpretty)s' % {
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