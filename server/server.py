#!/usr/bin/env python
# -*- coding: utf-8 -*-
import tello		# tello.pyをインポート
import time			# time.sleepを使いたいので
import cv2			# OpenCVを使うため
import struct
import redis
import numpy as np

def writeRedis(r,a,n):
	"""Store given Numpy array 'a' in Redis under key 'n'"""
	h, w = a.shape[:2]
	shape = struct.pack('>II',h,w)
	
	encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]
	result, encimg = cv2.imencode('.jpg', a, encode_param)
	
	#encoded = shape + a.tobytes()
	encoded = shape + encimg.tobytes()

	# Store encoded data in Redis
	r.set(n,encoded)
	return


# メイン関数
def main():
	# Redis connection
	r = redis.Redis(host='os3-380-23015.vs.sakura.ne.jp', port=6379, db=0)

	# Telloクラスを使って，droneというインスタンス(実体)を作る
	drone = tello.Tello( command_timeout=.01 )  

	current_time = time.time()	# 現在時刻の保存変数
	pre_time = current_time		# 5秒ごとの'command'送信のための時刻変数

	time.sleep(0.5)		# 通信が安定するまでちょっと待つ
	
	#Ctrl+cが押されるまでループ
	try:
		while True:
			cmd = r.get('command')
			
			if cmd != None:
				cmd = cmd.decode()
				if len(cmd) != 0:
					print(cmd)
					r.set('command', '')
					drone.send_command(cmd)

			# (A)画像取得
			frame = drone.read()	# 映像を1フレーム取得
			if frame is None or frame.size == 0:	# 中身がおかしかったら無視
				continue 

			# (B)ここから画像処理
			#image = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)		# OpenCV用のカラー並びに変換する
			image = frame
			#small_image = cv2.resize(image, dsize=(320,240) )	# 画像サイズを1/3に変更
			#small_image = cv2.resize(image, dsize=(480,360) )	# 画像サイズを半分に変更

			# (X)ウィンドウに表示
			cv2.imshow('OpenCV Window', image)	# ウィンドウに表示するイメージを変えれば色々表示できる

			# (Y)OpenCVウィンドウでキー入力を1ms待つ
			key = cv2.waitKey(1)
			if key == 27:					# k が27(ESC)だったらwhileループを脱出，プログラム終了
				break
			elif key == ord('m'):				# モータ回転
				drone.send_command('motoron')
			elif key == ord('t'):
				drone.takeoff()				# 離陸
			elif key == ord('l'):
				drone.land()					# 着陸
			elif key == ord('w'):
				drone.move_forward(0.3)		# 前進
			elif key == ord('s'):
				drone.move_backward(0.3)		# 後進
			elif key == ord('a'):
				drone.move_left(0.3)			# 左移動
			elif key == ord('d'):
				drone.move_right(0.3)			# 右移動
			elif key == ord('q'):
				drone.rotate_ccw(20)			# 左旋回
			elif key == ord('e'):
				drone.rotate_cw(20)			# 右旋回
			elif key == ord('r'):
				drone.move_up(0.3)			# 上昇
			elif key == ord('f'):
				drone.move_down(0.3)			# 下降

			writeRedis(r, frame, 'image')

			# (Z)5秒おきに'command'を送って、死活チェックを通す
			current_time = time.time()	# 現在時刻を取得
			if current_time - pre_time > 5.0 :	# 前回時刻から5秒以上経過しているか？
				drone.send_command('command')	# 'command'送信
				pre_time = current_time			# 前回時刻を更新

	except( KeyboardInterrupt, SystemExit):    # Ctrl+cが押されたら離脱
		print( "SIGINTを検知" )

	# telloクラスを削除
	del drone


# "python main.py"として実行された時だけ動く様にするおまじない処理
if __name__ == "__main__":		# importされると"__main__"は入らないので，実行かimportかを判断できる．
	main()    # メイン関数を実行
