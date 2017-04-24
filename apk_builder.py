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

# project folders
src_prjects="""
CommonChannel
channel_360_combine
channel_UC_combine
channel_baidu_combine
channel_dangle_combine
channel_feiliu_combine
channel_huawei_combine
channel_jinli_combine
channel_lenovo_combine
channel_mz_combine
channel_oppo_combine
channel_vivo_combine
channel_xiaomi_combine
"""
# channel_tencent_combine
# channel_anzhi_combine
# channel_coolpad_combine

class CommandUtil(object):

	@staticmethod
	def excute(cmd, dry_run=False):
		start_point = time.time()
		process = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
		if dry_run: 
			logging.warn(cmd)
			return (0, cmd, '')
		else:
			logging.debug(cmd)
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


def excute(cmd):
	start_point = time.time()
	process = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
	out, err = process.communicate()
	# time.time()-start_point
	if len(err) > 0:
		logging.error('excute[%s]: %s\n%s' %(cmd, err, out))
		return ('[failed]', cmd, err, out)
	else:
		return ('[ok]', cmd, err, out)

def build_project_sdkagent(src, project, name, dist, library='CommonChannel'):
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
	# print excute('svn up')

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

	# (s, c, err, revision) = excute('svn info -rHEAD | grep "Last Changed Rev" | cut -d" " -f4')

	if '[ok]' == status and library:
		print CommandUtil.excute('cp %s/bin/MainActivity-debug.apk %s/%s-r%s.apk' % (sa_dir, dist, name, revision.strip('\n')) )

	logging.info('===== [%s] Build Over %s %s -r%s' % (project, time.time()-start_point, status, revision) )

def build_demos(args):
	"""sdk-agent适配各个渠道的demo，一锅出多个Android apk
	python apk_builder.py -s /tmp/apk_builder/demo -d /tmp/apk_builder/demo_dist -c demo
	"""
	dist = args.dest
	if not os.path.exists(dist):
		excute('mkdir -p %s' % (dist) )
	for project in src_prjects.split("\n"):
		if len(project) == 0: continue
		name = project
		if len(project.split('_'))==4:
			name = project.split('_')[2]
			build_project_sdkagent(args.src, project, name, dist, args.lib)
		else:
			build_project_sdkagent(args.src, project, name, dist, None)

CHANNEL_LIST = 'az bd cp dj fl hw jl lx mz qh op uc vv xx yyb'
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
			print excute('ln -s %s/apk_builder.py %s' % (os.path.abspath('.'), apk_dir) )
		os.chdir(apk_dir)
		(status, cmd, err, out) = excute('python apk_builder.py -c help')
		print status, out, err

def clean_project(dir):
	"""清理母包
	"""
	os.chdir(dir)

	# assets文件夹
	# libs 7 packages
	print excute('rm ./libs/alipaySdk-*.jar')
	print excute('rm ./libs/CommonChannel.jar')
	print excute('rm ./libs/android-support-v4.jar')
	print excute('rm ./libs/FL*.jar') #2 packages
	print excute('rm ./libs/ok*.jar') #2 packages
	print excute('rm ./libs/gson*.jar')
	# 手工剔除 AndroidManifest.xml 中的参数配置
	# 备份干净的 AndroidManifest.xml
	print excute('mv AndroidManifest.xml AndroidManifest-org.xml')
	print excute('cp AndroidFLMobile_v2.keystore')

	print excute('cp ../AndroidFLMobile_v2.keystore .')
	print excute('cp ../ant.properties .')

def merge_manifest(project_dir, plugin_dir, package_name):
	"""合并 AndroidManifest.xml:
	1. 删除已经存在的AndroidManifest.xml
	2. 以干净的AndroidManifest-org.xml为蓝本，加入插件目录的AndroidManifest.xml中的内容，生成新的；
	3. 替换成需要的包名
	"""
	# enter clean project folder
	os.chdir(project_dir)
	# 1. rm old
	print excute('rm AndroidManifest.xml')
	# 2. merge 
	print excute('ant -f merge_task.xml -Dplugin_publish_dir=%s' % (plugin_dir) )
	print excute('android update project -p . -n MainActivity -t android-21')
	# 3. replace package name
	print excute('sed -i.bak s/package=\\".*\\"/package=\\"%s\\"/g AndroidManifest.xml'%package_name)
	print excute('grep package AndroidManifest.xml')

def add_plugin_uc(project_dir, lib_dir, plugin_dir):
	"""Merge UC Channel

	project_dir 打包项目路径
	lib_dir 接口框架路径
	plugin_dir 渠道插件路径

	"""
	# enter clean project folder
	if not os.access(project_dir,os.F_OK):
		os.mkdir(project_dir)

	os.chdir(project_dir)
	if not os.access('./assets',os.F_OK):
		os.mkdir('./assets')
	if not os.access('./libs',os.F_OK):
		os.mkdir('./libs')

	print excute('cp %s/AndroidManifest.xml .' % (plugin_dir) )
	# cp Assets
	print excute('cp -R %s/assets/ucgamesdk ./assets' % (plugin_dir) )

	# cp Libs
	print excute('cp %s/libs/alipay.jar ./libs' % (plugin_dir) )
	print excute('cp %s/libs/classes.jar ./libs' % (plugin_dir) )
	print excute('cp %s/libs/okhttp-*.jar ./libs' % (plugin_dir) )
	print excute('cp %s/libs/okio-*.jar ./libs' % (plugin_dir) )

	# CommonChannel lib
	print excute('cp %s/bin/classes.jar ./libs/commonchannel.jar' % (lib_dir) )

	# UC lib: jar cf uc_channel.jar com/flsdk/channel/*.class
	print excute('cd %s/bin/classes; jar cf uc_channel.jar com/flsdk/channel/*.class' % (plugin_dir) )
	print excute('cp %s/bin/classes/uc_channel.jar ./libs' % (plugin_dir) )

def test():
	
	# build_project('/tmp/combine', 'test_project', 'test', 'dist')
	# print excute('svn info -rHEAD | grep "Last Changed Rev" | cut -d" " -f4')
	
	# os.chdir('/private/tmp/qz11')
	# print excute('echo start at `date`')

	# clean_project()
	# merge_manifest('/private/tmp/qz11', '/tmp/combine/FLSDK_channel_UC_combine', 'com.fl.qzgs.uc.aligames')
	git_dir = '/tmp/sdk-u3d-plugins'
	print 'git version: %s@%s '% ( CommandUtil.git_ver(git_dir),git_dir )

def install_game_uc(args):
	game_apk = args.src
	package_name = 'com.fl.qzgs.uc.aligames'
	print excute('adb uninstall %s' % package_name)
	print excute('adb install %s' % game_apk)


def build_game_apk(args):
	"""用干净游戏工程和渠道插件包进行打包: python apk_builder.py -s ../games/qz20_exit -d uc -c game

- 游戏渠道打包命名规则
qzgs_渠道编码-游戏包ID-插件版本号.apk

游戏包举例：g20_exit/g20_noexit
插件版本：p34234 - 就是对应的svn revision
	"""
	start_point = time.time()
	apk_dir = os.getcwd()
	status = 'init'
	print excute('echo start at `date`')
	game_dir = args.src
	channel = args.dest
	plugin_dir = os.path.dirname(os.path.realpath('apk_builder.py'))
	apk_name = 	channel +'-'+ os.path.basename(game_dir)

	revision = CommandUtil.git_ver(plugin_dir)
	
	# copy a clean build project
	# (status, cmd, err, out) = excute('cp -R %s game' % game_dir )
	(cost, out, err) = CommandUtil.excute('cp -R %s game' % game_dir, args.dry_run)

	# (status, cmd, err, out) = excute( 'cp -Rv %s/plugin_%s/* game' % (plugin_dir, channel) )
	(cost, out, err) = CommandUtil.excute('cp -Rv %s/plugin_%s/* game' % (plugin_dir, channel), args.dry_run)
	logging.warn( out )

	logging.info('===== [%s] Build Game Package: %s ' % (channel, os.getcwd()) )
	# print excute('android update project -p . -n %s' % apk_name)
	# (status, cmd, err, out) = excute('ant clean release')
	print CommandUtil.excute('android update project -p game -n %s -t %s' % (apk_name,args.target), args.dry_run)
	(cost, out, err) = CommandUtil.excute('ant -f game/build.xml clean release', args.dry_run)
	if len(err) > 0:
		status = 'failed'

	logging.info('===== [%s] Build Game Package Over %s %s' % (channel, time.time()-start_point, status) )
	print 'build %s cost %s ' % (channel, time.time()-start_point)
	
	apk_to = apk_name+'-p'+revision.strip('\n')+ '-release.apk'
	# print excute('cp bin/%s ../%s'%(apk_name+'-release.apk', apk_to) )
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
											help='Android Target ID')
	parser.add_argument('-s', dest='src', type=str, default='.',
											help='read source code from this directory')
	parser.add_argument('-d', dest='dest', type=str, default='./dist',
											help='Build apk to this directory')
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
	print 'dry_run=%s' % args.dry_run
		
	if 'init' == args.cmd:
		init_apks_dir(args)
	elif 'clean' == args.cmd:
		clean_project(args)
	elif 'demo' == args.cmd:
		build_demos(args)
	elif 'game' == args.cmd:
		build_game_apk(args)
	elif 'install' == args.cmd:
		install_game_uc(args)
	elif 'plugin' == args.cmd:
		build_plugin_uc(args.dest)
	elif 'help' == args.cmd:
		# print 'init build path [%s] for %s ...' % (os.getcwd(), args.app)
		parser.print_help()

	# test()

if __name__ == '__main__':
	print 'Launching ...'
	main()
