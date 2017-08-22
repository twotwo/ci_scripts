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
6. 合并图片工具： merge_img()

"""

import argparse
import codecs, os, sys, shutil
from subprocess import Popen, PIPE

import time #计算命令执行时长
import logging
import logging.config

import platform


class Command(object):
	# config command logger
	# reffer to http://wiki.li3huo.com/python_lib_logging#Logger_Objects
	logger = logging.getLogger('command')
	# create console handler and set level to debug
	ch = logging.StreamHandler()
	ch.setLevel(logging.DEBUG)
	# add formatter to ch
	ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
	# add ch to logger
	logger.addHandler(ch)

	@staticmethod
	def set_log_level(level):
		Command.logger.setLevel(level)

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
			Command.logger.warn('dry-run mode on[%s]'%cmd)
			return (0, cmd, '')
		else:
			Command.logger.debug(cmd)
		process = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
		out, err = process.communicate()
		if len(err) > 0:
			Command.logger.error('cmd=%s, err=%s' %(cmd, err))
		return (time.time()-start_point, out, err)

	@staticmethod
	def git_ver(git_dir):
		"""pull the latest content and get version
		git revision cmd: git rev-list --count HEAD
		"""
		cmd = 'git -C %s pull' % git_dir
		(cost, out, err) = Command.excute(cmd)
		if len(err) > 0:
			Command.logger.error('excute[%s]: %s' %(cmd, err))
		cmd = 'git -C %s rev-list --count HEAD' % git_dir
		(cost, out, err) = Command.excute(cmd)
		if len(err) > 0:
			Command.logger.error('excute[%s]: %s' %(cmd, err))
			return ''
		else:
			return out.strip('\n')

	@staticmethod
	def svn_ver(svn_dir):
		"""pull the latest content and get version
		svn info <path> | grep "Last Changed Rev" | cut -d" " -f4
		svn info --show-item last-changed-revision <path>
		"""
		cmd = 'svn up %s' % svn_dir
		(cost, out, err) = Command.excute(cmd)
		if len(err) > 0:
			Command.logger.error('excute[%s]: %s' %(cmd, err))
		cmd = 'svn info --show-item last-changed-revision %s' % svn_dir
		(cost, out, err) = Command.excute(cmd)
		if len(err) > 0:
			Command.logger.error('excute[%s]: %s' %(cmd, err))
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

		(cost, out, err) = Command.excute(test_cmd)


	@staticmethod
	def xcodebuild_lib(project, scheme, is_clean=False, is_xcpretty=True):
		"""xcode 编译 Libary & 编译Framework
		Xcode: Build Settings -> Math-O Type: Static Libary
		See Also: http://wiki.li3huo.com/xcodebuild#Build_Library
		"""
		if is_clean:
			(cost, out, err) = Command.excute('xcodebuild clean')

		build = 'Release'
		xcpretty = ''
		if is_xcpretty:
			xcpretty = ' | xcpretty'
		
		# 分别生成手机和模拟器的lib
		Command.logger.debug('分别生成手机和模拟器的lib...')
		for sdk, build_dir in (('iphoneos', 'arm'), ('iphonesimulator', 'x86')):
			build_cmd='xcodebuild build -project %(project_name)s -scheme %(scheme_name)s -configuration %(build_config)s only_active_arch=no defines_module=yes -sdk "%(sdk)s" CONFIGURATION_BUILD_DIR=build/%(build_dir)s%(xcpretty)s' % {
				'project_name': project, 
				'scheme_name': scheme,
				'build_config': build,
				'sdk': sdk,
				'build_dir': build_dir,
				'xcpretty': xcpretty
			}

			(cost, out, err) = Command.excute(build_cmd)

		# merge 2 lib as one
		Command.logger.debug('merge 2 lib as one...')
		merge_cmd='lipo -create build/arm/%(scheme_name)s.framework/%(scheme_name)s build/x86/%(scheme_name)s.framework/%(scheme_name)s -output build/merge_lib' % {
			'scheme_name': scheme
		}

		(cost, out, err) = Command.excute(merge_cmd)

		(cost, out, err) = Command.excute('mv build/merge_lib build/arm/%s.framework/%s' % (scheme, scheme) )

		(cost, out, err) = Command.excute('mv build/arm/%s.framework/ build/%s.framework' % (scheme, scheme) )

		Command.logger.debug('验证framework包含的框架集，应该是"armv7 i386 x86_64 arm64"')
		(cost, out, err) = Command.excute('lipo -info build/%s.framework/%s' % (scheme, scheme) )
		Command.logger.debug(out)

	@staticmethod
	def xcodebuild_ipa(project, scheme, export, is_clean=False, is_release=True, is_xcpretty=True):
		"""xcode 8.2+出ipa包的执行命令
		"""
		if is_clean:
			(cost, out, err) = Command.excute('xcodebuild clean')

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

		(cost, out, err) = Command.excute(archive_cmd)

		export_cmd='xcodebuild -exportArchive -archivePath %(archive_path)s -exportPath %(export_path)s -exportOptionsPlist package.plist%(xcpretty)s' % {
			'export_path': export,
			'archive_path': archive,
			'xcpretty': xcpretty
		}

		(cost, out, err) = Command.excute(export_cmd)

	@staticmethod
	def merge_img(src_img, width, caption, labels, font='/Library/Fonts/Songti.ttc', clean=True):
		"""Merge Iamges as one. Install ImageMagick(pip install ImageMagick) first.
		Refer to http://wiki.li3huo.com/ImageMagick
		Action Step: 
		1. resize to same width
		2. add label to img bottom
		3. 制作标题图片
		4. 水平拼图
		"""
		

		# params for convert 
		info = {
				'work_dir':'./tmp/%d'%os.getpid(), 
				'src_img':src_img, 
				'width':width, 
				'caption':caption,
				'font':font, }

		# create tmp dir
		if not os.path.exists('./tmp'): os.mkdir('./tmp')
		os.mkdir(info['work_dir'])

		# 1. resize to same width: w-[0-n].png
		cmd = 'convert -resize "%(width)s" "%(src_img)s" %(work_dir)s/w.png' % info
		(cost, out, err) = Command.excute(cmd)

		# 2. add label to img top: from w-[0-n].png to l-[0-n].png
		index = 0
		for label in labels:
			info['index']=index
			info['page']=index + 1
			info['label']=label
			cmd = '''height=30; width=%(width)s; \\
			convert -size ${width}x${height} xc:white %(work_dir)s/w-%(index)s.png -append \\
			-font "%(font)s" -pointsize 32 \\
			-background white -size x${height} -fill black label:%(page)s、 -gravity northwest -compose over -composite \\
			-background white -size x${height} -fill black label:"%(label)s" -gravity northeast -compose over -composite \\
			%(work_dir)s/l-%(index)s.png''' % info
			Command.excute(cmd)
			index = index +1

		# # 2. add label to img bottom: from w-[0-n].png to l-[0-n].png
		# index = 0
		# for label in labels:
		# 	info['index']=index
		# 	info['page']=index + 1
		# 	info['label']=label
		# 	cmd = '''height=30; width=%(width)s; \\
		# 	convert %(work_dir)s/w-%(index)s.png -size ${width}x${height} xc:white -append \\
		# 	-font "%(font)s" -pointsize 48 \\
		# 	-background white -size x${height} -fill black label:%(page)s -gravity southwest -compose over -composite \\
		# 	-background white -size x${height} -fill black label:"%(label)s" -gravity southeast -compose over -composite \\
		# 	%(work_dir)s/l-%(index)s.png''' % info
		# 	Command.excute(cmd)
		# 	index = index +1
		# 3. make caption
		cmd = 'convert -size %(width)sx60 -gravity Center -background white -fill dodgerblue -strokewidth 2 -stroke blue -undercolor lightblue -font "%(font)s" -density 56 -pointsize 28 caption:"%(caption)s" %(work_dir)s/caption.png' % info
		(cost, out, err) = Command.excute(cmd)

		# 4. append vertically
		cmd = 'convert -append %(work_dir)s/caption.png %(work_dir)s/l-[0-9].png %(work_dir)s/l-[1-9][0-9].png %(work_dir)s/caption.png vertical.png'% info #'convert -append caption.png l-[0-%d].png caption.png vertical.png' % (index -1)
		(cost, out, err) = Command.excute(cmd)

		if clean: shutil.rmtree(info['work_dir'])

class AgentBuilder(object):
	"""Android Agent 项目专用打包类
	"""
	logger = logging.getLogger('AgentBuilder')
	def __init__(self, ini_file, dry_run=False):
		self.dry_run = dry_run

		self.build_info = []
		self.logger = logging.getLogger('agentBuilder')

		import ConfigParser
		# config = ConfigParser.RawConfigParser(allow_no_value=True)
		config = ConfigParser.ConfigParser()
		config.read(ini_file)
		root_dir = config.get('base', 'root_dir')

		self.lib_base_dir = config.get('base', 'lib_base_dir', 0, {'root_dir': root_dir})
		self.channels_dir = config.get('base', 'channels_dir', 0, {'root_dir': root_dir})

		self.demo_dir = config.get('demo', 'demo_dir', 0, {'root_dir': root_dir})
		from datetime import date
		self.apk_dir = config.get('demo', 'apk_dir', 0, {'root_dir': root_dir, 'day':date.today().strftime('%m%d')})
		
		self.plugin_dir = config.get('plugins', 'plugin_dir', 0, {'root_dir': root_dir})

	def init(self):
		# init output dirs
		if os.path.exists(self.demo_dir):
			Command.excute('rm -rf %s' % self.demo_dir)
		os.makedirs(self.demo_dir)
		if not os.path.exists(self.apk_dir):
			os.makedirs(self.apk_dir)

	def build_baselib(self):
		# cp -R lib_base_dir demo_dir/lib_base
		Command.excute('cp -R %s %s/lib_base'%(self.lib_base_dir, self.demo_dir) )

		# android update & ant debug
		Command.excute('android update project -p %s/lib_base -n MainActivity -t android-21' % self.demo_dir)
		Command.excute('ant -f %s/lib_base/build.xml clean debug' % self.demo_dir)

		# cp demo_dir/lib_base/bin/classes.jar demo_dir/plugin_base-revision.jar
		revision = Command.svn_ver(self.lib_base_dir)
		base_jar = os.path.join(self.demo_dir, 'plugin_base-r%s.jar' % revision)
		from_jar = os.path.join(self.demo_dir, 'lib_base/bin/classes.jar')
		cmd = 'cp %s %s'% (from_jar, base_jar)
		(cost, out, err) = Command.excute(cmd)
		self.logger.info('Create plugin base lib.')

	def build_channel_apks(self, name):
		"""build channel apks to apk_dir
		name: all or channel name in project name
		"""
		# project name: FLSDK_channel_<channel>_combine
		for project in os.listdir(self.channels_dir):
			if not os.path.isdir( os.path.join(self.channels_dir, project) ):
				self.logger.warn('[%s] is not a directory!'%os.path.join(self.channels_dir, project))
				continue
			if project.find('.') == 0: continue

			# verify channel name
			if len(project.split('_'))!=4:
				print 'unknown project[%s]!'%project
				self.logger.error( 'unknown project[%s]!'%project )
				continue
			channel = project.split('_')[2]

			# 3.2 build all or certain channel
			if 'all' == name or channel == name:
				self.logger.info('build [%s] channel...'%channel)
				self.__build_lib_and_demoapk(project, channel, 'lib_base')
		
	def __build_lib_and_demoapk(self, project, channel, library):
		"""给svn中最新的适配代码打包，生成插件类库和demo apk
		project 	: project under demo;
		channel 	: channel name in project;
		library     : Directory of an Android library to add;
		"""
		status_jar = False # build status of lib
		status_apk = False # build status of apk
		code_dir = os.path.join(self.channels_dir, project)
		sa_dir = os.path.join(self.demo_dir, project)

		if os.path.exists(sa_dir) :
			Command.excute('rm -rf %s'%sa_dir )
		Command.excute('cp -R %s %s'%(code_dir, self.demo_dir), self.dry_run )

		game=os.environ.get('game')
		channel_ver = 'unknown'
		if os.path.exists( os.path.join(sa_dir,'SDKVersion.txt') ) :
			channel_ver = open(os.path.join(sa_dir,'SDKVersion.txt')).readline().strip()

		AgentBuilder.logger.info( 'demo_dir=%s, game=%s, channel=%s, ver=%s'%(self.demo_dir, game, channel, channel_ver) )
		
		# os.chdir(sa_dir)
		AgentBuilder.logger.info('===== [%s] Build Start: %s ' % (project, os.getcwd()) )

		revision = Command.svn_ver(code_dir)
		self.logger.info('build %s@r%s' % (sa_dir, revision))

		self.logger.info('create android project ... ')
		cmd = 'android update project -p %s -n MainActivity -t android-21'%sa_dir
		if library:
			(cost, out, err) = Command.excute('cp ant.properties %s'%sa_dir)
			(cost, out, err) = Command.excute('rm %s/project.properties'%sa_dir)
			cmd = 'android update project -l ../%s -p %s -n MainActivity -t android-21' % (library, sa_dir)
			# f = open('project.properties', 'w') #'r', 'w' or 'a'
			# f.write(project_properties)
			# f.close
		 # -t --target     : Target ID to set for the project.
		 # android-21 Name: Android 5.0.1
		 # android-22 Name: Android 5.1.1
		build='debug'
		if os.path.exists( os.path.join(sa_dir,'%s.properties'%game) ) :
			(cost, out, err) = Command.excute('mv %s %s'%(os.path.join(sa_dir,'%s.properties'%game), os.path.join(sa_dir,'ant.properties')))
			build='release'
		(cost, out, err) = Command.excute(cmd)
		if len(err) > 0: 
			status = '[failed]'
		else:
			status = '[ok]'

		self.logger.info('build android project ... ')
		cmd = 'ant -f %s/build.xml clean %s'%(sa_dir,build)
		(cost, out, err) = Command.excute(cmd, self.dry_run)
		if len(err) > 0: 
			status = '[failed]'
		else:
			status = '[ok]'

		if '[ok]' == status:
			# build apk, such as 360_c1.9.2_r168988_b62.apk
			version_info= 'c%s_r%s_b%s' % (channel_ver, revision, os.environ.get('BUILD_NUMBER'))
			(cost, out, err) = Command.excute('cp %(project_dir)s/bin/MainActivity-%(build_type)s.apk %(dist_dir)s/%(apk_name)s.apk' % {
				'project_dir': sa_dir,
				'dist_dir': self.apk_dir,
				'apk_name': channel+'\('+build+'\)_'+version_info,
				'build_type': build
				})
			if len(err) == 0: status_apk = True

			# build plugin lib ,such as plugin_360_c1.9.2_r168988_b62.jar
			if not os.path.exists( os.path.join(sa_dir,'plugin_task.xml') ):
				Command.excute('cp plugin_task.xml %s'% sa_dir) 
			(cost, out, err) = Command.excute('ant -f %s/plugin_task.xml -Drevision=%s -Dchannel=%s'% (sa_dir, version_info, channel ))
			if len(err) == 0: status_jar = True

		self.build_info.append('build [%s] jar: %s, apk: %s, revision: %s' % (channel, status_jar, status_apk, revision))


def test():
	if Command.isMacSystem(): 
		logging.info('launch on OS X!')
	if Command.isLinuxSystem(): logging.info('launch on Linux!')
	if Command.isWindowsSystem(): logging.info('launch on Windows!')

	try:
		logging.info('current dir git version = '+Command.git_ver("."))
	except Exception, ex:
		logging.error('Catch Exception: '+ ex)

	if len(sys.argv) >1:
		logging.debug('svn dir = %s, version = %s' % (sys.argv[1], Command.svn_ver(sys.argv[1])))
	else:
		logging.debug('pls add svn path')

if __name__ == '__main__':
	logging.config.fileConfig("./logging.conf")
	# logging.basicConfig(filename='./command.log', level=logging.INFO, format='%(asctime)s [%(name)s] %(levelname)s %(message)s')
	test()