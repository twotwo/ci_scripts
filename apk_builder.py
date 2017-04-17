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
Channel_360_combine
Channel_UC_combine
Channel_anzhi_combine
Channel_baidu_combine
Channel_coolpad_combine
Channel_dangle_combine
Channel_feiliu_combine
Channel_huawei_combine
Channel_jinli_combine
Channel_lenovo_combine
Channel_mz_combine
Channel_oppo_combine
Channel_tencent_combine
Channel_vivo_combine
Channel_xiaomi_combine
"""


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

def build(args):
	for project in src_prjects.split("\n"):
		if len(project) == 0: continue
		name = project
		if len(project.split('_'))==4:
			name = project.split('_')[2]
			build_project(args.src, project, name, args.dest, args.lib)
		else:
			build_project(args.src, project, name, args.dest, None)
		
def test():
	os.chdir('/tmp/combine/test_project')
	# print excute('svn info -rHEAD | grep "Last Changed Rev" | cut -d" " -f4')
	build_project('/tmp/combine', 'test_project', 'test', 'dist')


def main():
	parser = argparse.ArgumentParser(description='APK Builder.')
	parser.add_argument('-s', dest='src', type=str, default='.',
											help='read source code from this directory.')
	parser.add_argument('-d', dest='dest', type=str, default='./dist',
											help='Build apk to this directory.')
	parser.add_argument('-c', dest='cmd', type=str, default='build',
											help='Build apk.')
	parser.add_argument('-l', dest='lib', type=str, default='CommonChannel',
											help='Directory of an Android library to add')
	parser.add_argument('--show', dest='show', action='store_true')
	parser.add_argument('--not-show', dest='show', action='store_false')
	parser.set_defaults(show=True)
	# config a log
	logging.basicConfig(filename='./build.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

	args = parser.parse_args()

	print "source : " + args.src
	print "dest : " + args.dest
	print "cmd : " + args.cmd

	# test()

	if 'build' == args.cmd:
		build(args)

if __name__ == '__main__':
	print 'Launching ...'
	main()