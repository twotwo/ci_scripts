# -*- coding: utf-8 -*-
"""
图片合并加注释的工具类

Author: liyan
File: merge_img.py

Features:
1. 把多张图片合并为一张垂直依次排列的大图
2. 大图带标题，小图带编号和注释
3. 合并后的图片：vertical.png
"""

import argparse
from util import Command

def test():
	"""
	"""
	my_labels = 'first step; second step; third step; forth step'.split(';')
	try:
		print 'begin merge...'
		Command.merge_img(src_img='j_[1-4].jpg', width=300, caption='做一个测试', labels=my_labels, clean=False)
		print 'merge over.'
	except Exception, e: 
		print 'except:', e
		raise


def main():
	parser = argparse.ArgumentParser(description='Xcode Builder.')
	parser.add_argument('-a', dest='action', type=str, default='merge', choices=('test', 'merge'), 
											help='Action perform')
	parser.add_argument('-s', dest='src_img', type=str, default='i_[1-9].png i_[1-9][0-9].png',
											help='image patern')
	parser.add_argument('-w', dest='export', type=int, default=300,
											help='Width of the merge image')
	parser.add_argument('-c', dest='caption', type=str, default='标题： 这是一个测试',
											help='image caption')
	parser.add_argument('-l', dest='labels', type=str, default='l1;l2;l3;l4',
											help='label for eath image, split by ;')
	parser.add_argument('--clean', dest='clean', action='store_false',
											help='Remove working files')
	parser.set_defaults(clean=True)
	

	args = parser.parse_args()

	# test()
	index = 1
	for lable in args.labels.split(';'):
		print index, lable
		index = index + 1
	# python /opt/local/ide/git_storage/github/apk-builder/merge_img.py -s "j_[0-8].jpg" -c 金立礼包码展示逻辑 -l "未展开的悬浮球;展开的悬浮球（选择礼包）;礼包列表标签，抢“独家礼包”;获取成功：展示“独家礼包”详情;已获得的礼包列表（我的礼包）;礼包列表中直接复制激活码;礼包详情页;礼包详情页复制并返回游戏" --clean
	Command.merge_img(src_img=args.src_img, width=300, caption=args.caption, labels=args.labels.split(';'), clean=args.clean)
	


if __name__ == '__main__':
	main()