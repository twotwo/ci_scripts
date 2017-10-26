# -*- coding: utf-8 -*-
"""
Xcode打包工具类

Author: liyan
File: xcode_builder.py

Features:
1. read_version_from_project() 获取项目版本号
2. build_xcode_project() 给xcode 项目打 ipa 包
3. make_ota_link() 生成OTA下载链接
"""
from util import Command, PlistBuddy

def read_version_from_project():
	"""read get version command from a file,
	excute command to get local project's version
	"""
	try:
		# grep MyEditionId ../MyServiceDefine.h |cut -d "\\"" -f 2
		version_cmd = open('version_cmd').readline().strip()
		(cost, out, err) = Command.excute(version_cmd)
		if len(err) > 0:
			print version_cmd, '\nerr: ', err
		else: print '========== load project version:', out.strip('\n')
		return out.strip('\n')
	except: 
		return 'unknown'

def build_xcode_project(args):
	"""调用方法: python ~/apk-builder/xcode_builder.py -a ipa --ipa SDK_V5 -p FLGamePlatformDemo -s FLGamePlatformDemoRelease --clean
工作步骤：
	1. XCode项目打包
	2. 重命名ipa为 %(ipa_name)s_v%(code_ver)s_r%(repo_ver)s_b%(build_num)s.ipa
	例如： SDK_V5_v5.1.56_r168988_b62.jar
	3. create ota plist
	"""
	# 1. build xcode project and export ipa
	Command.xcodebuild_ipa(project=args.project+'.xcodeproj', 
							scheme=args.scheme,
	 						export=args.export, 
	 						is_clean=args.clean, dry_run=args.dry_run)
	print 'ipa file name:', args.ipa_name
	
	# 2. rename
	ipa_name = '%(ipa_name)s_v%(code_ver)s_r%(repo_ver)s_b%(build_num)s.ipa' % {
			'ipa_name': args.ipa_name,
			'code_ver': read_version_from_project(),
			'repo_ver': Command.svn_ver('..', do_update=False),
			'build_num': os.environ.get('BUILD_NUMBER')
		}
	rename_cmd = 'mv %(export_path)s/%(scheme_name)s.ipa %(export_path)s/%(ipa_name)s' % {
			'scheme_name': args.scheme,
			'export_path': args.export,
			'ipa_name': ipa_name
		}
	(cost, out, err) = Command.excute(rename_cmd, args.dry_run)
	if len(err) == 0: 
		logging.info('mission done for building [%s]'%ipa_name)
	else:
		logging.error('mission failed for building [%s]'%ipa_name)
	# 3. create ota plist
	# cp ipa to nginx root path
	rename_cmd = 'cp %(export_path)s/%(ipa_name)s %(root_path)s' % {
			'export_path': args.export,
			'ipa_name': ipa_name,
			'root_path': args.root_path
		}
	(cost, out, err) = Command.excute(rename_cmd, args.dry_run)

	plistBuddy = PlistBuddy(args.root_path, ipa_name)
	# create plist
	plistBuddy.create_ota_plist( os.path.join(args.ipa_url, ipa_name), os.path.join(args.ipa_url, 'icon.png'))
	# create update links to plist
	plistBuddy.update_index_html(args.ipa_name, args.ipa_url)

def make_ota_link():
	"""生成OTA下载链接
	"""

def main():
	import argparse
	parser = argparse.ArgumentParser(description='Xcode Builder.')
	parser.add_argument('-a', dest='action', type=str, default='ipa', choices=('test', 'lib', 'ipa'), 
											help='Action perform')
	parser.add_argument('--ipa', dest='ipa_name', type=str, default='',
											help='the IPA file name')
	parser.add_argument('--root', dest='root_path', type=str, default='.',
											help='put IPA here to make nginx find it')
	parser.add_argument('--url', dest='ipa_url', type=str, default='',
											help='the IPA download links, must be HTTPS!')
	parser.add_argument('-p', dest='project', type=str, default='Demo.xcodeproj',
											help='Xcode Project Folder Name')
	parser.add_argument('-s', dest='scheme', type=str, default='DemoRelease',
											help='Xcode Project Scheme')
	parser.add_argument('-e', dest='export', type=str, default='./build',
											help='Build IPA to this directory')
	parser.add_argument('--clean', dest='clean', action='store_false',
											help='Remove files in CONFIGURATION_BUILD_DIR & CONFIGURATION_TEMP_DIR')
	parser.set_defaults(clean=True)
	parser.add_argument('--dry-run', dest='dry_run', action='store_true',
											help='Dry Run Mode: do not excute time-consuming operation')
	parser.set_defaults(dry_run=False)

	args = parser.parse_args()

	if args.dry_run: print 'in dry-run mode'	

	if len(args.ipa_name) ==0: args.ipa_name = args.scheme

	if args.action == 'test':
		Command.xcodebuild_test(project=args.project+'.xcodeproj', scheme=args.scheme)
	elif args.action == 'lib':
		Command.xcodebuild_lib(project=args.project+'.xcodeproj', scheme=args.scheme, is_clean=True)
	elif args.action == 'ipa':
		build_xcode_project(args)

if __name__ == '__main__':
	import os, sys, logging
	config_file = os.path.join(sys.path[0],'logging.conf')
	try:
		logging.config.fileConfig( config_file )
	except Exception, ex:
		print 'Failed to load logging config file: ', config_file ,'\nCatch Exception: ', ex
		exit(-1)
	main()