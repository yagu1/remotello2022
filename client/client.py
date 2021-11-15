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

	# loop until you press ctrl+c
	try:
		while True:

			img = fromRedis(r,'image')
			#print(f"read image with shape {img.shape}")

			# show OpenCV image
			cv2.imshow('Image from Redis', img)

			# wait key-input 1ms on OpenCV window
			key = cv2.waitKey(1)
			if key == 27:			# 27 == ESC, exit
				break
			elif key == ord('m'):
				r.set('command','motoron')
			elif key == ord('t'):		# takeoff
				r.set('command','takeoff')
			elif key == ord('l'):		# land
				r.set('command','land')
			elif key == ord('w'):		# forward
				r.set('command','forward 50')
			elif key == ord('s'):		# back
				r.set('command','back 50')
			elif key == ord('a'):		# move left
				r.set('command','left 50')
			elif key == ord('d'):		# move right
				r.set('command','right 50')
			elif key == ord('q'):		# turn left
				r.set('command','ccw 20')
			elif key == ord('e'):		# turn right
				r.set('command','cw 20')
			elif key == ord('r'):		# move up
				r.set('command','up 30')
			elif key == ord('f'):		# move down
				r.set('command','down 30')


	except( KeyboardInterrupt, SystemExit):    # if Ctrl+c is pressed, quit program.
		print( "Detect SIGINT." )
