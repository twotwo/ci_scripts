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
# FLSDK_channel_tencent_combine
# FLSDK_channel_anzhi_combine
# FLSDK_channel_coolpad_combine


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

def build_project(src, project, name, dist, library='CommonChannel'):
	# -l --library    : Directory of an Android library to add
	logging.info( (src, project, name, library) )
	os.chdir(src+'/'+project)
	logging.info('===== [%s] Build Start: %s ' % (project, os.getcwd()) )
	start_point = time.time()

	print excute('pwd')
	print 'working on '+os.getcwd()
	print excute('svn up')

	if library:
		print excute('cp ../ant.properties .')
		print excute('rm project.properties')
		excute('android update project -l ../%s -p . -n MainActivity -t android-21' % library)
		# f = open('project.properties', 'w') #'r', 'w' or 'a'
		# f.write(project_properties)
		# f.close
	 # -t --target     : Target ID to set for the project.
	 # android-21 Name: Android 5.0.1
	 # android-22 Name: Android 5.1.1
	excute('android update project -p . -n MainActivity -t android-21')
	
	(status, cmd, err, out) = excute('ant -f build.xml clean debug')
	print (status, cmd)

	(s, c, err, revision) = excute('svn info -rHEAD | grep "Last Changed Rev" | cut -d" " -f4')
	

	if '[ok]' == status:
		print excute('cp bin/MainActivity-debug.apk ../%s/%s-r%s.apk' % (dist, name, revision.strip('\n')) )

	logging.info('===== [%s] Build Over %s %s -r%s' % (project, time.time()-start_point, status, revision) )

def build_channels(args):
	for project in src_prjects.split("\n"):
		if len(project) == 0: continue
		name = project
		if len(project.split('_'))==4:
			name = project.split('_')[2]
			build_project(args.src, project, name, args.dest, args.lib)
		else:
			build_project(args.src, project, name, args.dest, None)

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
	print excute('grep FLGAMESDK AndroidManifest.xml')
	print excute('grep com.feiliu AndroidManifest.xml')
	print excute('grep FL_AGENT_PAYNOTIFY_URL AndroidManifest.xml')
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
	
	os.chdir('/private/tmp/qz11')
	print excute('echo start at `date`')

	# clean_project()
	merge_manifest('/private/tmp/qz11', '/tmp/combine/FLSDK_channel_UC_combine', 'com.fl.qzgs.uc.aligames')

def install_game_uc(args):
	game_apk = args.src
	package_name = 'com.fl.qzgs.uc.aligames'
	print excute('adb uninstall %s' % package_name)
	print excute('adb install %s' % game_apk)


def build_game(args):
	"""用干净游戏工程和渠道插件包进行打包: python apk_builder.py -s ../games/qz20_exit -d uc -c game
cp -R ../games/qz20_exit game
cp -Rvn ../plugins/plugin_qh/* game
android update project -p .
ant clean release
	"""
	start_point = time.time()

	game_dir = args.src
	channel = args.dest

	print excute('echo start at `date`')
	# copy a clean build project
	(status, cmd, err, out) = excute('cp -R %s game' % game_dir )
	print cmd
	logging.warn( (status, cmd, err, out) )

	# add plugins to project. do not overwrite exited file!
	excute('cp -Rvn ../plugins/plugin_%s/* game' % (channel) )
	os.chdir('./game')
	logging.info('===== [%s] Build Game Package: %s ' % (channel, os.getcwd()) )
	print excute('android update project -p .')
	(status, cmd, err, out) = excute('ant clean release')

	logging.info('===== [%s] Build Game Package Over %s %s' % (channel, time.time()-start_point, status) )
	print 'build %s cost %s ' % (channel, time.time()-start_point)
	print excute('android update project -p .')

def main():
	parser = argparse.ArgumentParser(description='APK Builder.')
	parser.add_argument('-a', dest='app', type=str, default='qzgs',
											help='the apk name')
	parser.add_argument('-s', dest='src', type=str, default='.',
											help='read source code from this directory.')
	parser.add_argument('-d', dest='dest', type=str, default='./dist',
											help='Build apk to this directory.')
	parser.add_argument('-c', dest='cmd', type=str, default='demo',
											help='Build demo apk.')
	parser.add_argument('-l', dest='lib', type=str, default='CommonChannel',
											help='Directory of an Android library to add')
	parser.add_argument('--show', dest='show', action='store_true')
	parser.add_argument('--not-show', dest='show', action='store_false')
	parser.set_defaults(show=True)
	# config a log
	logging.basicConfig(filename='./build.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

	args = parser.parse_args()

	# print "source : " + args.src
	# print "dest : " + args.dest
	# print "cmd : " + args.cmd
		
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
		print 'init build path [%s] for %s ...' % (os.getcwd(), args.app)

	# test()

if __name__ == '__main__':
	print 'Launching ...'
	main()
