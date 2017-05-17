# -*- coding: utf8 -*-
"""
apk自动打包命令行工具

@liyan
"""

import argparse
import codecs, os
from subprocess import Popen, PIPE

import time #计算命令执行时长
import logging
import ConfigParser

class CommandUtil(object):

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
		(cost, out, err) = CommandUtil.excute(cmd)
		if len(err) > 0:
			logging.error('excute[%s]: %s' %(cmd, err))
			return
		cmd = 'git -C %s rev-list --count HEAD' % git_dir
		(cost, out, err) = CommandUtil.excute(cmd)
		return out.strip('\n')

	@staticmethod
	def svn_ver(svn_dir):
		"""pull the latest content and get version
		git revision cmd: git rev-list --count HEAD
		"""
		cmd = 'svn up %s' % svn_dir
		(cost, out, err) = CommandUtil.excute(cmd)
		if len(err) > 0:
			logging.error('excute[%s]: %s' %(cmd, err))
			return
		cmd = 'svn info %s -rHEAD | grep "Last Changed Rev" | cut -d" " -f4' % svn_dir
		(cost, out, err) = CommandUtil.excute(cmd)
		return out.strip('\n')

def build_project_sdkagent(src, project, name, dist, library):
	"""给svn中最新的适配代码打包
	"""
	# -l --library    : Directory of an Android library to add
	logging.info( (src, project, name, library) )
	sa_dir = os.path.join(src, project)
	# os.chdir(sa_dir)
	logging.info('===== [%s] Build Start: %s ' % (project, os.getcwd()) )
	start_point = time.time()

	revision = CommandUtil.svn_ver(sa_dir)
	print 'build %s@r%s' % (sa_dir, revision)

	print 'create android project ... '
	cmd = 'android update project -p %s -n MainActivity -t android-21'%sa_dir
	if library:
		print CommandUtil.excute('cp ant.properties %s'%sa_dir)
		print CommandUtil.excute('rm %s/project.properties'%sa_dir)
		cmd = 'android update project -l ../%s -p %s -n MainActivity -t android-21' % (library, sa_dir)
		# f = open('project.properties', 'w') #'r', 'w' or 'a'
		# f.write(project_properties)
		# f.close
	 # -t --target     : Target ID to set for the project.
	 # android-21 Name: Android 5.0.1
	 # android-22 Name: Android 5.1.1
	(cost, out, err) = CommandUtil.excute(cmd)
	if len(err) > 0: 
		status = '[failed]'
		print status, cmd , err
	else:
		status = '[ok]'
		print status, cmd

	print 'build android project ... '
	cmd = 'ant -f %s/build.xml clean debug'%sa_dir
	(cost, out, err) = CommandUtil.excute(cmd)
	if len(err) > 0: 
		status = '[failed]'
		print status, cmd , err
	else:
		status = '[ok]'
		print status, cmd

	if '[ok]' == status and library:
		print CommandUtil.excute('cp %s/bin/MainActivity-debug.apk %s/%s-r%s.apk' % (sa_dir, dist, name, revision.strip('\n')) )
		if not os.path.exists( os.path.join(sa_dir,'plugin_task.xml') ):
			CommandUtil.excute('cp plugin_task.xml %s'% sa_dir)
		CommandUtil.excute('ant -f %s/plugin_task.xml'% sa_dir)

	logging.info('===== [%s] Build Over %s %s -r%s' % (project, time.time()-start_point, status, revision) )

def build_demos(args):
	"""sdk-agent适配各个渠道的demo，一锅出多个Android apk
	python apk_builder.py -s demo.ini -d /tmp/apk_builder/demo_dist -c demo
	"""
	
	config = ConfigParser.RawConfigParser(allow_no_value=True)
	config.read(args.src)
	demo_dir = config.get('base', 'base_dir')

	if not os.path.exists(demo_dir):
		os.makedirs(demo_dir)
	# 1 demo_reference + 15 channel plugins = 16
	if len( os.listdir(demo_dir) ) < 16:
		# checkout from svn
		cmd = 'svn co %s %s/demo_reference'%(config.get('base', 'svn_reference'), demo_dir) 
		print cmd + " [%d] %s %s" % CommandUtil.excute(cmd)
		cmd = 'svn ls %s'%config.get('base', 'svn_demo_base')
		(cost, out, err) = CommandUtil.excute(cmd)
		if len(err) > 0:
			print cmd, err
			return
		for project in out.split("\n"):
			cmd = 'svn co %s/%s %s/%s'%(config.get('base', 'svn_demo_base') , project, demo_dir, project) 
			print 'checking out... ', cmd
			CommandUtil.excute(cmd)

	dist = args.dest
	if not os.path.exists(dist):
		print CommandUtil.excute('mkdir -p %s' % (dist) )
	
	# build reference lib:
	build_project_sdkagent(demo_dir, 'demo_reference', 'plugin_base', dist, None)
	# check revision & replace new in plugins
	revision = CommandUtil.svn_ver( os.path.join(demo_dir, 'demo_reference') )
	base_jar = 'plugin_base-r%s.jar' % revision
	print '[%s] create plugin base lib. %s %s'%CommandUtil.excute('cp %s %s'% 
		(os.path.join(demo_dir, 'demo_reference/bin/classes.jar'), 
		os.path.join(demo_dir, base_jar) ) )
	plugin_dir = config.get('plugins', 'base_dir')
	for plugin in os.listdir(plugin_dir): 
		if plugin.find('plugin_') ==0: 
			if not os.path.exists( os.path.join(plugin_dir, plugin, 'libs', base_jar) ): 
				# rm libs/plugin_base-r*.jar
				print CommandUtil.excute( 'rm %s'%os.path.join(plugin_dir, plugin, 'libs/plugin_base-r*.jar') )
				# replaced with the newest one
				print CommandUtil.excute( 'cp %s %s'%(os.path.join(demo_dir, base_jar), os.path.join(plugin_dir, plugin, 'libs')) )

	for project in os.listdir(demo_dir):
		if project == 'demo_reference': continue
		if not os.path.isdir( os.path.join(demo_dir, project) ): continue
		name = project
		if len(project.split('_'))==4:
			name = project.split('_')[2]
			build_project_sdkagent(demo_dir, project, name, dist, 'demo_reference')
		else:
			print 'unknown project!'
			logging.error( 'unknown project[%s]!'%project  )


CHANNEL_LIST = 'az bd cp dj fl hw jl lx mz qh op uc vv xm yyb'
def init_apks_dir(args):
	"""初始化游戏渠道打包目录: xx_apk， 建议和sdk-u3d-plugins同级
	python apk_builder.py -s .. -c init
	"""
	base = args.src
	for channel in CHANNEL_LIST.split():
		if len(channel) == 0: continue
		apk_dir = os.path.join(base, channel+'_apk')
		if not os.path.exists(apk_dir):
			os.mkdir(apk_dir)
			print CommandUtil.excute('ln -s %s/apk_builder.py %s' % (os.path.abspath('.'), apk_dir) )
		os.chdir(apk_dir)
		print CommandUtil.excute('python apk_builder.py -c help')

def clean_project(args):
	"""清理母包
	"""
	plugin_dir = os.path.dirname(os.path.realpath('apk_builder.py'))
	app_dir = os.path.abspath(args.src)
	os.chdir(app_dir)

	# assets文件夹
	# libs 7 packages
	print CommandUtil.excute('rm ./libs/alipaySdk-*.jar')
	print CommandUtil.excute('rm ./libs/CommonChannel.jar')
	print CommandUtil.excute('rm ./libs/android-support-v4.jar')
	print CommandUtil.excute('rm ./libs/FL*.jar') #2 packages
	print CommandUtil.excute('rm ./libs/ok*.jar') #2 packages
	print CommandUtil.excute('rm ./libs/gson*.jar')
	# 手工剔除 AndroidManifest.xml 中的参数配置
	# 备份干净的 AndroidManifest.xml
	print CommandUtil.excute('mv AndroidManifest.xml AndroidManifest-org.xml')

	print CommandUtil.excute( 'cp %s/AndroidFLMobile_v2.keystore %s'%(plugin_dir, app_dir) )
	print CommandUtil.excute( 'cp %s/ant_%s.properties %s/ant.properties'%(plugin_dir, args.app, app_dir) )

def merge_manifest(project_dir, plugin_dir, package_name):
	"""合并 AndroidManifest.xml:
	1. 删除已经存在的AndroidManifest.xml
	2. 以干净的AndroidManifest-org.xml为蓝本，加入插件目录的AndroidManifest.xml中的内容，生成新的；
	3. 替换成需要的包名
	"""
	# enter clean project folder
	os.chdir(project_dir)
	# 1. rm old
	print CommandUtil.excute('rm AndroidManifest.xml')
	# 2. merge 
	print CommandUtil.excute('ant -f merge_task.xml -Dplugin_publish_dir=%s' % (plugin_dir) )
	print CommandUtil.excute('android update project -p . -n MainActivity -t android-21')
	# 3. replace package name
	print CommandUtil.excute('sed -i.bak s/package=\\".*\\"/package=\\"%s\\"/g AndroidManifest.xml'%package_name)
	print CommandUtil.excute('grep package AndroidManifest.xml')


def test():
	
	# build_project_sdkagent('/tmp/combine', 'test_project', 'test', 'dist')
	# print CommandUtil.excute('svn info -rHEAD | grep "Last Changed Rev" | cut -d" " -f4')
	
	# os.chdir('/private/tmp/qz11')

	# clean_project()
	# merge_manifest('/private/tmp/qz11', '/tmp/combine/FLSDK_channel_UC_combine', 'com.fl.qzgs.uc.aligames')
	print 'pwd=%s' % os.getcwd()

def build_apk(args):
	"""clean project + plugin -> build to apk : python apk_builder.py -s ../games/qz20_exit -d uc -c game

- 渠道打包命名规则
应用名称_渠道编码-应用版本好-插件版本号.apk

应用举例：g20_exit/g20_noexit
插件举例：p23 - 对应的git revision
	"""
	start_point = time.time()
	apk_dir = os.getcwd()
	status = 'init'
	print CommandUtil.excute('echo start at `date`')
	game_dir = args.src
	channel = args.dest
	plugin_dir = os.path.dirname(os.path.realpath('apk_builder.py'))
	apk_name = 	channel +'-'+ os.path.basename(game_dir)

	revision = CommandUtil.git_ver(plugin_dir)
	
	# copy a clean build project
	(cost, out, err) = CommandUtil.excute('cp -R %s game' % game_dir, args.dry_run)

	(cost, out, err) = CommandUtil.excute('cp -Rv %s/plugin_%s/* game' % (plugin_dir, channel), args.dry_run)
	logging.warn( out )

	logging.info('===== [%s] Build Game Package: %s ' % (channel, os.getcwd()) )

	print CommandUtil.excute('android update project -p game -n %s -t %s' % (apk_name,args.target), args.dry_run)
	(cost, out, err) = CommandUtil.excute('ant -f game/build.xml clean release', args.dry_run)
	if len(err) > 0:
		status = 'failed'

	logging.info('===== [%s] Build Game Package Over %s %s' % (channel, time.time()-start_point, status) )
	print 'build %s cost %s ' % (channel, time.time()-start_point)
	
	apk_to = apk_name+'-p'+revision.strip('\n')+ '-release.apk'

	cmd_cp_apk = 'cp game/bin/%s %s'%(apk_name+'-release.apk', apk_to)
	(cost, out, err) = CommandUtil.excute(cmd_cp_apk, args.dry_run)
	# 在jenkins环境下
	jenkins_mv(apk_to, args.dry_run)

def jenkins_mv(apk_name, dry_run):
	"""
	"""
	if None == os.environ.get('WORKSPACE') or None == os.environ.get('BUILD_NUMBER'):
		return
	apk_to = os.path.join(os.environ.get('WORKSPACE'),'game_apks',os.environ.get('BUILD_NUMBER'))
	if not os.path.exists(apk_to):
		os.mkdir(apk_to)
	cmd_mv_apk = 'mv %s %s'%(apk_name, apk_to)
	print CommandUtil.excute(cmd_mv_apk, dry_run)

def main():
	parser = argparse.ArgumentParser(description='APK Builder.')
	parser.add_argument('-a', dest='app', type=str, default='qzgs',
											help='the apk name')
	parser.add_argument('-t', dest='target', type=str, default='android-21',
											help='Android Target ID. Default is android-21')
	parser.add_argument('-s', dest='src', type=str, default='.',
											help='read source code from this directory')
	parser.add_argument('-d', dest='dest', type=str, default='./dist',
											help='Build apk to this directory. Default is ./dist')
	parser.add_argument('-c', dest='cmd', type=str, default='help',
											help='Build command')
	parser.add_argument('-l', dest='lib', type=str, default='CommonChannel',
											help='Directory of an Android library to add')
	parser.add_argument('--dry-run', dest='dry_run', action='store_true',
											help='Dry Run Mode: do not excute time-consuming operation')
	parser.set_defaults(dry_run=False)
	# config a log
	logging.basicConfig(filename='./build.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

	args = parser.parse_args()

	# print "source : " + args.src
	# print "dest : " + args.dest
	# print "cmd : " + args.cmd
	if args.dry_run: print 'in dry-run mode'
		
	if 'demo' == args.cmd:
		build_demos(args)
	elif 'init' == args.cmd:
		init_apks_dir(args)
	elif 'clean' == args.cmd:
		clean_project(args)
	elif 'apk' == args.cmd:
		build_apk(args)
	elif 'help' == args.cmd:
		parser.print_help()

	# test()

if __name__ == '__main__':
	main()
