#!/usr/bin/env python3

import cv2
from time import sleep
import struct
import redis
import numpy as np

def fromRedis(hRedis,topic):
	"""Retrieve Numpy array from Redis key 'topic'"""
	encoded = hRedis.get(topic)
	h, w = struct.unpack('>II',encoded[:8])		# unpack

	# make numpy array
	a = np.frombuffer(encoded, dtype=np.uint8, offset=8)

	# decode jpeg to opencv image
	decimg = cv2.imdecode(a, flags=cv2.IMREAD_UNCHANGED).reshape(h,w,3)

	return decimg



if __name__ == '__main__':
	# Redis connection
	r = redis.Redis(host='os3-380-23015.vs.sakura.ne.jp', port=6379, db=0)

	cmd = ''

	#Ctrl+cが押されるまでループ
	# loop until you press ctrl+c
	try:
		while True:

			img = fromRedis(r,'image')
			#print(f"read image with shape {img.shape}")

			cv2.imshow('Image from Redis', img)

			# OpenCVウィンドウでキー入力を1ms待つ
			key = cv2.waitKey(1)
			if key == 27:					# key が27(ESC)だったらwhileループを脱出，プログラム終了
				break
			elif key == ord('m'):
				r.set('command','motoron')
			elif key == ord('t'):		# 離陸
				r.set('command','takeoff')
			elif key == ord('l'):		# 着陸
				r.set('command','land')
			elif key == ord('w'):		# 前進
				r.set('command','forward 50')
			elif key == ord('s'):		# 後進
				r.set('command','back 50')
			elif key == ord('a'):		# 左移動
				r.set('command','left 50')
			elif key == ord('d'):		# 右移動
				r.set('command','right 50')
			elif key == ord('q'):		# 左旋回
				r.set('command','ccw 20')
			elif key == ord('e'):		# 右旋回
				r.set('command','cw 20')
			elif key == ord('r'):		# 上昇
				r.set('command','up 30')
			elif key == ord('f'):		# 下降
				r.set('command','down 30')


	except( KeyboardInterrupt, SystemExit):    # Ctrl+cが押されたら離脱
		print( "SIGINTを検知" )
