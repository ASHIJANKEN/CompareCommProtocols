# -*- coding: utf-8 -*-

import time
import sys
import serial
import subprocess
import random

max_data_length = 64

def getdata(send_bytes, max_speed_hz):
  # send_bytesを送信できるサイズに分割する
  send_blocks = [send_bytes[i: i+max_data_length] for i in range(0, len(send_bytes), max_data_length)]

  ###############################################
  # 送受信・計測
  ###############################################
  result = []
  with serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=max_speed_hz,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=100,
  ) as ser:
    start_time = time.time()
    for i, block in enumerate(send_blocks):
      # #送信するbyte数を先頭に付加する(1byte)
      # l = len(block)
      # block.insert(0, (l & 0xFF))
      ser.write(bytearray(block))
      # 送信リクエスト
      result.extend(ser.read(1))
    end_time = time.time()

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
    data_dir = argvs[1]
    speed_hz = int(argvs[2])

    # 送信データをファイルから読み込む
    with open('send_bytes.txt', mode = 'r', encoding = 'utf-8') as fh:
      elms = fh.readlines()

    # 末尾改行文字を除去
    elms = [i.rstrip() for i in elms]
    # 要素をintへ変換
    elms = [int(i) for i in elms]
    # send_bytes_patternの長さをmax_data_lengthにする
    l = len(elms)
    send_bytes_pattern = elms * (max_data_length // l)
    send_bytes_pattern += elms[0:(max_data_length % l)]

    for send_bytes in [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]:
      #記録ファイルの生成
      file_path = data_dir + str(speed_hz) + 'Hz' + '_' + str(send_bytes) + 'bytes.txt'
      with open(file_path, mode = 'w', encoding = 'utf-8') as fh:
        pass

      # 送信データの作成
      send = send_bytes_pattern * (send_bytes // len(send_bytes_pattern))
      send = send + send_bytes_pattern[0:(send_bytes % len(send_bytes_pattern))]

      # 1,000回の試行
      for i in range(1000):

        # データの送信
        execution_time, err = getdata(send, speed_hz)

        print('[UART throughput] {0}:{1}\t{2}\t{3}\t{4}'.format(i, send_bytes, speed_hz, execution_time, err))
        with open(file_path, mode = 'a', encoding = 'utf-8') as fh:
          fh.write('{0}:{1}\t{2}\n'.format(i, execution_time, err))
        if execution_time > 100:
          print("timeout!")
          sys.exit(0)

      # ログを消す
      proc = subprocess.Popen(['clear'])
      proc.wait()
      print('[UART throughput] Recorded : {0}\t{1}'.format(send_bytes, speed_hz))

    sys.exit(0)
  except KeyboardInterrupt:
    sys.exit(0)

