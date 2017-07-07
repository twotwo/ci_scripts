# -*- coding: utf-8 -*-
"""
Xcode打包工具类

Author: liyan
File: xcode_builder.py

Features:
1. 获取项目版本号
2. 获取当前svn版本号
3. 重命名ipa为%(export_path)s/%(scheme_name)s_V%(version)s(%(build)s).ipa
"""

import argparse
from util import Command

def read_version():
	"""read get version command from a file,
	excute command to get version
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


def main():
	parser = argparse.ArgumentParser(description='Xcode Builder.')
	parser.add_argument('-a', dest='app', type=str, default='',
											help='the IPA file name')
	parser.add_argument('-p', dest='project', type=str, default='Demo.xcodeproj',
											help='Xcode Project Folder Name')
	parser.add_argument('-s', dest='scheme', type=str, default='DemoRelease',
											help='Xcode Project Scheme')
	parser.add_argument('-e', dest='export', type=str, default='./build',
											help='Build IPA to this directory')
	parser.add_argument('--dry-run', dest='dry_run', action='store_true',
											help='Dry Run Mode: do not excute time-consuming operation')
	parser.set_defaults(dry_run=False)

	args = parser.parse_args()

	if args.dry_run: print 'in dry-run mode'
	build = Command.svn_ver('..')
	version = read_version()

	if len(args.app) ==0: args.app = args.scheme

	print 'ipa file =', args.app, 'version =', version
	# xcodebuild -list
	Command.xcodebuild_ipa(project=args.project+'.xcodeproj', scheme=args.scheme, export=args.export)
	rename_cmd = 'mv %(export_path)s/%(scheme_name)s.ipa %(export_path)s/%(ipa_file)s_V%(version)s\\(%(build)s\\).ipa' % {
			'scheme_name': args.scheme,
			'export_path': args.export,
			'ipa_file': args.app,
			'version': version,
			'build': build
		}
	(cost, out, err) = Command.excute(rename_cmd)
	print err

if __name__ == '__main__':
	main()