# -*- coding: utf-8 -*-

import time
import sys
import serial
import subprocess
import RPi.GPIO as GPIO

max_data_length = 63
notice_pin = 18

# GPIOのセットアップ
GPIO.setmode(GPIO.BCM)
GPIO.setup(notice_pin, GPIO.OUT)

def getdata(send_bytes, max_speed_hz):
  # send_bytesをxfer2で送信できるサイズに分割する
  send_blocks = [send_bytes[i: i+max_data_length] for i in range(0, len(send_bytes), max_data_length)]

  ###############################################
  # 送受信・計測
  ###############################################
  result = []
  with serial.Serial('/dev/ttyS0',max_speed_hz,timeout=100) as ser:
    # 送信スタートの合図
    GPIO.output(notice_pin, True)
    start_time = time.time()
    for i, block in enumerate(send_blocks):
      #送信するbyte数を先頭に付加する(1byte)
      l = len(block)
      block.insert(0, (l & 0xFF))
      ser.write(bytearray(block))
      # 送信リクエスト
      result.extend(ser.read(1))
    end_time = time.time()

    # 送信終了の合図
    GPIO.output(notice_pin, False)
    ser.close()

  # 送受信誤りがあるかどうかを確認する
  err = 0
  for i in result:
    if i != 0:
      err = 1
      break

  return end_time - start_time, err

if __name__ == '__main__':
  try:
    argvs = sys.argv
    base_dir = argvs[1]
    speed_hz = argvs[2]

    # 送信データをファイルから読み込む
    with open('send_bytes.txt', mode = 'r', encoding = 'utf-8') as fh:
      elms = fh.readlines()
      #末尾改行文字を除去
      elms = [i.rstrip() for i in elms]
      #要素をintへ変換
      elms =[int(i) for i in elms]
      #default_send_bytesの長さをmax_data_lengthにする
      leng = len(elms)
      default_send_bytes = elms * (max_data_length // leng)
      default_send_bytes = default_send_bytes + elms[0:(max_data_length % leng)]

#     for send_bytes in [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536]:
#     for send_bytes in [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096]:
    for send_bytes in [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]:
      #記録ファイルの生成
      file_name = base_dir + str(speed_hz) + 'Hz' + '_' + str(send_bytes) + 'bytes_uart_throuput.txt'
      with open(file_name, mode = 'w', encoding = 'utf-8') as fh:
        pass

      # 送信データの作成
      send = []
      send = default_send_bytes * (send_bytes // len(default_send_bytes))
      send = send + default_send_bytes[0:(send_bytes % len(default_send_bytes))]

      # 1k回の試行
      for i in range(1000):

        # データの送信
        execution_time, err = getdata(send, speed_hz)

        print('{0}:{1}\t{2}\t{3}\t{4}'.format(i, send_bytes, speed_hz, execution_time, err))
        with open(file_name, mode = 'a', encoding = 'utf-8') as fh:
          fh.write('{0}:{1}\t{2}\n'.format(i, execution_time, err))
        if execution_time > 100:
          print("timeout!")
          sys.exit(0)

      # ログを消す
      proc = subprocess.Popen(['clear'])
      proc.wait()
      print('Recorded : {0}\t{1}'.format(send_bytes, speed_hz))

    sys.exit(0)
  except KeyboardInterrupt:
    sys.exit(0)
