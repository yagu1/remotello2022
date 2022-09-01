#!/usr/bin/env python
# -*- coding: utf-8 -*-
import tello		# import tello.py
import time		# for time.sleep() function
import cv2			# OpenCV
import struct
import redis
import numpy as np
import json
from sshtunnel import SSHTunnelForwarder

def writeRedis(r,a,n):
	"""Store given Numpy array 'a' in Redis under key 'n'"""
	h, w = a.shape[:2]
	shape = struct.pack('>II',h,w)

	encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]
	result, encimg = cv2.imencode('.jpg', a, encode_param)

	encoded = shape + encimg.tobytes()

	# Store encoded data in Redis
	r.set(n,encoded)
	return


# Main Function
def main():
	# Redis connection
	ssht = SSHTunnelForwarder(
        	("163.143.132.153", 22),
        	ssh_host_key=None,
        	ssh_username="uavdata",
        	ssh_password="0158423046",
        	ssh_pkey=None,
        	remote_bind_address=("localhost", 6379))
	ssht.start()
	r = redis.Redis(host='localhost', port=ssht.local_bind_port, db=0)

	# make instance as "drone" using Tello class
	drone = tello.Tello( command_timeout=.01 )

	current_time = time.time()	# current time
	pre_time = current_time		# for sending 'command' each 5 seconds

	time.sleep(0.5)		# wait for stable connection

	# make new OpenCV window for Tarckbar
	cv2.namedWindow("OpenCV Window")

	# empty function for Trackbar callback
	def nothing(x):
		pass

	# make Trackbar
	cv2.createTrackbar("Battery", "OpenCV Window", 50, 100, nothing)
	cv2.createTrackbar("Tof", "OpenCV Window", 50, 1000, nothing)
	cv2.createTrackbar("h", "OpenCV Window", 50, 1000, nothing)

	# loop until Ctrl+c pressed
	try:
		while True:
			cmd = r.get('command')

			if cmd != None:
				cmd = cmd.decode()
				if len(cmd) != 0:
					print(cmd)
					r.set('command', '')
					drone.send_command(cmd)

			# (A)get image
			frame = drone.read()	# get 1 frame
			if frame is None or frame.size == 0:		# correct data?
				continue

			# (B)processing
			#image = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)		# change OpenCV color plane
			image = frame
			#small_image = cv2.resize(image, dsize=(320,240) )	# change 1/3 size
			#small_image = cv2.resize(image, dsize=(480,360) )	# change 1/2 size

			# (X)show window
			cv2.imshow('OpenCV Window', image)

			# show tello info
			if drone.state is not None:
				cv2.setTrackbarPos("Battery", "OpenCV Window", drone.state["bat"])
				cv2.setTrackbarPos("Tof", "OpenCV Window", drone.state["tof"])
				cv2.setTrackbarPos("h", "OpenCV Window", drone.state["h"])

			# (Y)key input
			key = cv2.waitKey(1)
			if key == 27:					# 27 = ESC key), exit program
				break
			elif key == ord('m'):				# motor start
				drone.send_command('motoron')
			elif key == ord('o'):				# motor stop
				drone.send_command('motoroff')
			elif key == ord('t'):
				drone.takeoff()				# takeoff
			elif key == ord('l'):
				drone.land()					# land
			elif key == ord('w'):
				drone.move_forward(0.3)		# move forward
			elif key == ord('s'):
				drone.move_backward(0.3)		# move back
			elif key == ord('a'):
				drone.move_left(0.3)			# move left
			elif key == ord('d'):
				drone.move_right(0.3)			# move right
			elif key == ord('q'):
				drone.rotate_ccw(20)			# turn left
			elif key == ord('e'):
				drone.rotate_cw(20)			# turn right
			elif key == ord('r'):
				drone.move_up(0.3)			# move up
			elif key == ord('f'):
				drone.move_down(0.3)			# move down

			# (Y) write date to Redis
			writeRedis(r, frame, 'image')	# write image

			# write tello info and show
			if drone.state is not None:
				json_state = json.dumps( drone.state )
				#print(json_state)
				r.set('state', json_state)

			# (Z)send 'command' each 5 seconds
			current_time = time.time()	# current time
			if current_time - pre_time > 5.0 :	# 5 seconds passed?
				drone.send_command('command')	# send 'command'
				pre_time = current_time			# update previous time




	except( KeyboardInterrupt, SystemExit):    # detect Ctrl+c pressed
		print( "detect SIGINT." )

	# delete tello class
	del drone


if __name__ == "__main__":
	main()    # call Main Function
