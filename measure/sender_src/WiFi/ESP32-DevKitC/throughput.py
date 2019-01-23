# -*- coding: utf-8 -*-

import time
import sys
import socket
import subprocess
import random

family_addr = socket.AF_INET
host = 'esp_server.local'
PORT = 3333
max_data_length = 512

def getdata(sock, send_bytes):
  # send_bytesを送信できるサイズに分割する
  send_blocks = [send_bytes[i: i+max_data_length] for i in range(0, len(send_bytes), max_data_length)]

  ###############################################
  # 送受信・計測
  ###############################################
  result = []
  start_time = time.time()
  # Send data
  for block in send_blocks:
    sock.sendall(bytes(bytearray(block)))

    # Receive data
    result.extend(sock.recv(1))
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

    # ESP32との接続
    sock = socket.socket(family_addr, socket.SOCK_STREAM)
    sock.connect((host, PORT))

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
        execution_time, err = getdata(sock, send)

        print('[TCP throughput] {0}:{1}\t{2}\t{3}\t{4}'.format(i, send_bytes, speed_hz, execution_time, err))
        with open(file_path, mode = 'a', encoding = 'utf-8') as fh:
          fh.write('{0}:{1}\t{2}\n'.format(i, execution_time, err))
        if execution_time > 100:
          print("timeout!")
          sys.exit(0)

      # ログを消す
      proc = subprocess.Popen(['clear'])
      proc.wait()
      print('[TCP throughput] Recorded : {0}\t{1}'.format(send_bytes, speed_hz))

    # ESP32との接続を切断
    sock.close()
    sys.exit(0)
  except KeyboardInterrupt:
    sock.close()
    sys.exit(0)
  except socket.error as msg:
    # print('Could not connect ESP32: ' + str(msg[0]) + ': ' + msg[1])
    sys.exit(1);