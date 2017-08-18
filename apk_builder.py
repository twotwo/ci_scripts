# -*- coding: utf8 -*-
"""
apk自动打包命令行工具

Author: liyan
File: apk_builder.py

Features:
1. build_agent_demos(): build my multiple module project
2. 
"""

from util import Command

import argparse, logging
import os, ConfigParser

class AgentBuilder(object):
	def __init__(self, ini_file, dry_run=False):
		self.dry_run = dry_run

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

		print '[%s] create plugin base lib. %s %s'%Command.excute(cmd)

	def build_channel_apks(self, name):
		"""build channel apks to apk_dir
		name: all or channel name in project name
		"""
		# project name: FLSDK_channel_<channel>_combine
		for project in os.listdir(self.channels_dir):
			if not os.path.isdir( os.path.join(self.channels_dir, project) ): continue
			if project.find('.') == 0: continue

			# verify channel name
			if len(project.split('_'))!=4:
				print 'unknown project[%s]!'%project
				logging.error( 'unknown project[%s]!'%project )
				continue
			channel = project.split('_')[2]

			# 3.2 build all or certain channel
			if 'all' == name or channel == name:
				self.__build_lib_and_demoapk(project, channel, 'lib_base')
		
	def __build_lib_and_demoapk(self, project, channel, library):
		"""给svn中最新的适配代码打包，生成插件类库和demo apk
		project 	: project under demo;
		channel 	: channel name in project;
		library     : Directory of an Android library to add;
		"""
		code_dir = os.path.join(self.channels_dir, project)
		sa_dir = os.path.join(self.demo_dir, project)

		if os.path.exists(sa_dir) :
			Command.excute('rm -rf %s'%sa_dir )
		Command.excute('cp -R %s %s'%(code_dir, self.demo_dir), self.dry_run )


		game=os.environ.get('game')
		channel_ver = 'unknown'
		if os.path.exists( os.path.join(sa_dir,'SDKVersion.txt') ) :
			channel_ver = open(os.path.join(sa_dir,'SDKVersion.txt')).readline().strip()

		logging.info( 'demo_dir=%s, game=%s, channel=%s, ver=%s'%(self.demo_dir, game, channel, channel_ver) )
		
		# os.chdir(sa_dir)
		logging.info('===== [%s] Build Start: %s ' % (project, os.getcwd()) )

		revision = Command.svn_ver(code_dir)
		print 'build %s@r%s' % (sa_dir, revision)

		print 'create android project ... '
		cmd = 'android update project -p %s -n MainActivity -t android-21'%sa_dir
		if library:
			print Command.excute('cp ant.properties %s'%sa_dir)
			print Command.excute('rm %s/project.properties'%sa_dir)
			cmd = 'android update project -l ../%s -p %s -n MainActivity -t android-21' % (library, sa_dir)
			# f = open('project.properties', 'w') #'r', 'w' or 'a'
			# f.write(project_properties)
			# f.close
		 # -t --target     : Target ID to set for the project.
		 # android-21 Name: Android 5.0.1
		 # android-22 Name: Android 5.1.1
		build='debug'
		if os.path.exists( os.path.join(sa_dir,'%s.properties'%game) ) :
			print Command.excute('mv %s %s'%(os.path.join(sa_dir,'%s.properties'%game), os.path.join(sa_dir,'ant.properties')))
			build='release'
		(cost, out, err) = Command.excute(cmd)
		if len(err) > 0: 
			status = '[failed]'
			print status, cmd , err
		else:
			status = '[ok]'
			print status, cmd

		print 'build android project ... '
		cmd = 'ant -f %s/build.xml clean %s'%(sa_dir,build)
		(cost, out, err) = Command.excute(cmd, self.dry_run)
		if len(err) > 0: 
			status = '[failed]'
			print status, cmd , err
		else:
			status = '[ok]'
			print status, cmd

		if '[ok]' == status and library:
			# build apk, such as 360_c1.9.2_r168988_b62.apk
			version_info= 'c%s_r%s_b%s' % (channel_ver, revision, os.environ.get('BUILD_NUMBER'))
			(cost, out, err) = Command.excute('cp %(project_dir)s/bin/MainActivity-%(build_type)s.apk %(dist_dir)s/%(apk_name)s.apk' % {
				'project_dir': sa_dir,
				'dist_dir': self.apk_dir,
				'apk_name': channel+'\('+build+'\)_'+version_info,
				'build_type': build
				})
			if len(err) > 0: print err

			# build plugin lib ,such as plugin_360_c1.9.2_r168988_b62.jar
			if not os.path.exists( os.path.join(sa_dir,'plugin_task.xml') ):
				Command.excute('cp plugin_task.xml %s'% sa_dir) 
			Command.excute('ant -f %s/plugin_task.xml -Drevision=%s -Dchannel=%s'% (sa_dir, version_info, channel ))

		logging.info('===== [%s] Build Over %s -r%s' % (project, status, revision) )

def test():
	
	print 'pwd=%s' % os.getcwd()

def build_agent_demos(args):
	"""sdk-agent适配各个渠道的demo，一锅出多个Android apk和适配层类库
	python apk_builder.py -c demo -s demo.ini -ch tencent
	"""
	builder = AgentBuilder(args.src, args.dry_run)
	builder.init()
	
	builder.build_baselib()

	builder.build_channel_apks(args.channel)
		

def build_apk(args):
	"""clean project, add plugin -> build to apk : 
	python apk_builder.py -c apk -s ../games/qz20_exit -ch uc

- 渠道打包命名规则
应用名称_渠道编码-应用版本好-插件版本号.apk

应用举例：app_dir
插件举例：p23 - 对应的git revision
	"""


def main():
	parser = argparse.ArgumentParser(description='APK Builder.')
	parser.add_argument('-a', dest='app', type=str, default='qzgs',
											help='the apk name')
	parser.add_argument('-t', dest='target', type=str, default='android-21',
											help='Android Target ID. Default is android-21')
	parser.add_argument('-s', dest='src', type=str, default='.',
											help='read source code from this directory')
	parser.add_argument('-c', dest='cmd', type=str, default='help',
											help='Build command')
	parser.add_argument('-ch', dest='channel', type=str, default='all',
											help='Channel Name, all or a certain name')
	parser.add_argument('--dry-run', dest='dry_run', action='store_true',
											help='Dry Run Mode: do not excute time-consuming operation')
	parser.set_defaults(dry_run=False)
	# config a log
	logging.basicConfig(filename='./build.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

	args = parser.parse_args()

	if args.dry_run: print 'in dry-run mode'
		
	if 'demo' == args.cmd:
		build_agent_demos(args)
	elif 'apk' == args.cmd:
		build_apks(args)
	elif 'help' == args.cmd:
		parser.print_help()

	# test()

if __name__ == '__main__':
	main()
