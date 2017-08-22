# -*- coding: utf-8 -*-
"""
apk自动打包命令行工具

Author: liyan
File: apk_builder.py

Features:
1. merge_plugin_and_build_apk(): merge my plugin to project and build to apk
2. build_agent_demos(): build my multiple module project use AgentBuilder class
"""

from util import Command, AgentBuilder

import argparse
import logging
import os, sys

def test():
	
	print 'pwd=%s' % os.getcwd()

def merge_plugin_and_build_apk(args):
	"""Excute Help: python apk_builder.py -c apk -s /data/game_apks/g103_3 -ch qh
-c command type, must be apk
-s read source code from this directory
-ch witch channel plugin merge to source
lftp -c 'open -e "pget -n 4 games/qzgs_201_08211523.rar" sdk:123456@172.16.100.120'
wget https://github.com/dryes/rarlinux/raw/master/rarlinux-5.2.1.tar.gz

操作逻辑说明： 
1. init: 初始化工程目录，删除存在的工程目录
2. copy: 复制项目代码到工程目录
3. clean: 清理工程目录中的默认插件代码
4. merge: 把指定插件拷贝到工程目录
5. update: 更新versionName和versionCode
6. build: 打包
7. save: 拷贝到指定目录

- 工作目录
1. sdk-u3d-plugins：根据apk_builder.py路径，从而确定plugins路径；
2. 工程目录(apk_dir, 执行ant release的目录)：当前执行命令的路径下的build_<plugin name>目录，即 os.getcwd()/build_<plugin name>


- 渠道打包命名规则
应用名称_渠道编码-应用目录名-插件版本号.apk

应用举例：g20_exit/g20_noexit
插件举例：p23 - 对应的git revision
	"""
	Command.set_log_level(logging.DEBUG)
	status = 'init'

	game_dir = args.src
	channel = args.channel

	apk_dir = os.path.join(os.getcwd(),'build_%s'%channel)
	plugin_dir = sys.path[0]
	logging.info( '[%s]plugin_dir = %s, apk_dir = %s' % (status, plugin_dir, apk_dir) ) 

	revision = Command.git_ver(plugin_dir)

	if len(revision) == 0:
		print 'revision missing'
		logging.warn('revision missing')

	if os.path.exists(apk_dir):
		print 'apk_dir exists, you should delete before build.'
		return

	apk_name = 	channel +'-'+ os.path.basename(game_dir)
	
	# 拷贝母包
	status = 'copy'
	(cost, out, err) = Command.excute('cp -R %s %s' % (game_dir, apk_dir), args.dry_run)
	logging.info( '[%s]from_dir = %s, to_dir = %s' % (status, game_dir, apk_dir) ) 

	# 母包初始化
	clean_and_init_project(apk_dir)
	# cp channel keystore & ant.properties
	keystore = os.path.join(plugin_dir,'keys.%s/%s.keystore'%(args.app,channel))
	ant_p = os.path.join(plugin_dir,'keys.%s/ant_%s.properties'%(args.app,channel))
	if os.path.exists(keystore) and os.path.exists(ant_p):
		(cost, out, err) = Command.excute('cp %s %s' % (keystore, apk_dir), args.dry_run)
		print Command.excute('cp %s %s/ant.properties' % (ant_p, apk_dir), args.dry_run)

	(cost, out, err) = Command.excute('cp -Rv %s/plugin_%s/* %s' % (plugin_dir, channel, apk_dir), args.dry_run)
	# change versionCode&versionName in AndroidManifest.xml
	cmd = '''sed -i.bak -r '{s/android:versionCode=\s*\"[0-9]{1,}\"/android:versionCode=\"%s\"/g;s/android:versionName=\s*\"[^"]+\"/android:versionName=\"%s\"/g}' %s/AndroidManifest.xml''' % (args.versioncode, args.versionname, apk_dir)
	(cost, out, err) = Command.excute(cmd)
	print cmd

	print Command.excute('android update project -p %s -n %s -t %s' % (apk_dir, apk_name, args.target), args.dry_run)
	(cost, out, err) = Command.excute('ant -f %s/build.xml clean release' % apk_dir, args.dry_run)
	status = 'build apk'
	logging.info('[%s] Build Game Package, channel=%s, err=%s' % (status, channel, err) )
	
	apk_save_to = apk_name+'-p'+revision+'-release_vc'+args.versioncode+ '.apk'

	status = 'cp to build dir'
	cmd_cp_apk = 'cp %s/bin/%s %s'%(apk_dir, apk_name+'-release.apk', apk_save_to)
	(cost, out, err) = Command.excute(cmd_cp_apk, args.dry_run)
	logging.info('[%s] Save Game Package, cmd=%s, err=%s' % (status, cmd_cp_apk, err) )

	status = 'mv to jenkins workspace'
	if None != os.environ.get('BUILD_NUMBER'):
		apk_mv_to = os.path.join(os.environ.get('WORKSPACE'),'game_apks',os.environ.get('BUILD_NUMBER'))
		if not os.path.exists(apk_mv_to):
			os.mkdir(apk_mv_to)
		cmd_mv_apk = 'mv %s %s'%(apk_save_to, apk_mv_to)
		(cost, out, err) = Command.excute(cmd_mv_apk, args.dry_run)
		logging.info('[%s] Move Game Package, cmd=%s, err=%s' % (status, cmd_mv_apk, err) )


def clean_and_init_project(app_dir = 'game'):
	"""母包初始化，拷贝到合成目录后：先清理特定渠道内容、再放入必要参数
	"""
	app_name='qzgs'

	plugin_dir = sys.path[0]

	# 清理
	# libs 7 packages
	Command.excute('rm %s/libs/alipaySdk-*.jar'%app_dir)
	Command.excute('rm -rf %s/libs/CommonChannel*.jar'%app_dir)
	Command.excute('rm %s/libs/plugin_base*.jar'%app_dir)
	Command.excute('rm %s/libs/plugin_feiliu*.jar'%app_dir)
	Command.excute('rm %s/libs/android-support-v4.jar'%app_dir)
	Command.excute('rm %s/libs/FL*.jar'%app_dir) #2 packages
	Command.excute('rm %s/libs/ok*.jar'%app_dir) #2 packages
	Command.excute('rm %s/libs/gson*.jar'%app_dir)
	Command.excute('rm %s/AndroidManifest.xml'%app_dir)

	# 添加
	keystore = os.path.join(plugin_dir,'keys.%s/AndroidFLMobile_v2.keystore'%app_name)
	ant_p = os.path.join(plugin_dir,'keys.%s/ant.properties'%app_name)
	Command.excute('cp %s %s' % (keystore, app_dir))
	Command.excute('cp %s %s' % (ant_p, app_dir))

def build_agent_demos(args):
	"""sdk-agent适配各个渠道的demo，一锅出多个Android apk和适配层类库
	python apk_builder.py -c demo -s demo.ini -ch tencent
	"""
	Command.set_log_level(logging.DEBUG)
	builder = AgentBuilder(args.src, args.dry_run)
	builder.init()
	
	builder.build_baselib()

	builder.build_channel_apks(args.channel)

	logging.info('==== Build %d channels ====\n'%len(builder.build_info)+'\n'.join(builder.build_info))

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
	parser.add_argument('-vn', dest='versionname', type=str, default='1.0.0', 
											help='Android manifest versionName')
	parser.add_argument('-vc', dest='versioncode', type=str, default='1', 
											help='Android manifest versionCode')
	parser.add_argument('--dry-run', dest='dry_run', action='store_true',
											help='Dry Run Mode: do not excute time-consuming operation')
	parser.set_defaults(dry_run=False)

	args = parser.parse_args()

	if args.dry_run: print 'in dry-run mode'
		
	if 'apk' == args.cmd:
		merge_plugin_and_build_apk(args)
	elif 'demo' == args.cmd:
		build_agent_demos(args)
	elif 'help' == args.cmd:
		parser.print_help()

	# test()

if __name__ == '__main__':
	logging.basicConfig(filename='./build.log', level=logging.INFO, format='%(asctime)s [%(name)s] %(levelname)s %(message)s')
	main()
