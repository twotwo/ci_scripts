# -*- coding: utf-8 -*-
"""
Xcode打包工具类

Author: liyan
File: xcode_builder.py

Features:
1. read_local_version() 获取项目版本号
2. build_xcode_project() 给xcode 项目打 ipa 包
3. make_ota_link() 生成OTA下载链接
"""
from util import Command

def read_local_version():
	"""read get version command from a file,
	excute command to get local project's version
	"""
	try:
		# grep MyEditionId ../MyServiceDefine.h |cut -d "\\"" -f 2
		version_cmd = open('version_cmd').readline().strip()
		(cost, out, err) = Command.excute(version_cmd)
		if len(err) > 0:
			print version_cmd, '\nerr: ', err
		return out.strip('\n')
	except: 
		return 'unknown'

def build_xcode_project(args):
	"""调用方法: python ~/apk-builder/xcode_builder.py -a ipa --ipa SDK_V5 -p FLGamePlatformDemo -s FLGamePlatformDemoRelease --clean
工作步骤：
	1. 获取项目版本号
	2. 获取当前svn版本号
	3. 打包
	4. 重命名ipa为%(export_path)s/%(scheme_name)s_V%(version)s(%(build)s).ipa
	"""
	version = read_local_version()
	print 'ipa file =', args.ipa, 'version =', version
	# xcodebuild -list
	Command.xcodebuild_ipa(project=args.project+'.xcodeproj', scheme=args.scheme, export=args.export, is_clean=args.clean, dry_run=args.dry_run)
	rename_cmd = 'mv %(export_path)s/%(scheme_name)s.ipa %(export_path)s/%(ipa_file)s_V%(version)s\\(%(build)s\\).ipa' % {
			'scheme_name': args.scheme,
			'export_path': args.export,
			'ipa_file': args.ipa,
			'version': version,
			'build': Command.svn_ver('..')
		}
	(cost, out, err) = Command.excute(rename_cmd, args.dry_run)
	print err
def make_ota_link():
	"""生成OTA下载链接
	"""

def main():
	import argparse
	parser = argparse.ArgumentParser(description='Xcode Builder.')
	parser.add_argument('-a', dest='action', type=str, default='ipa', choices=('test', 'lib', 'ipa'), 
											help='Action perform')
	parser.add_argument('--ipa', dest='ipa', type=str, default='',
											help='the IPA file name')
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

	if len(args.ipa) ==0: args.ipa = args.scheme

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