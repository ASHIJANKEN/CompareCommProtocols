# -*- coding: utf-8 -*-

import time
import sys
import socket
import subprocess
import random

family_addr = socket.AF_INET
host = 'esp_server.local'
PORT = 3333

def getdata(sock, send_bytes, max_speed_hz):
  start_time = time.time()
  # Send data
  sock.sendall(bytes(bytearray(send_bytes)))

  # Receive data
  result = sock.recv(1)
  end_time = time.time()

  return result[0], end_time - start_time

if __name__ == '__main__':
  try:
    argvs = sys.argv
    speed_hz = int(argvs[1])

    for send_bytes in [10000]:

      # 送信データの作成
      send = []
      for i in range(send_bytes):
        send.append(random.randint(0, 255))

      # ESP32との接続
      sock = socket.socket(family_addr, socket.SOCK_STREAM)
      sock.connect((host, PORT))

      # send_bytes回の試行
      for i in range(send_bytes):

        # データの送信
        result, execution_time = getdata(sock, [send[i]], speed_hz)

        # 受信データのエラーチェック
        err = 0 if result == send[i] else 1

      # ESP32との接続を切断
      sock.close()

      proc.wait()

    sock.close()
    sys.exit(0)
  except KeyboardInterrupt:
    sock.close()
    sys.exit(0)
  except socket.error as msg:
    print('Could not connect ESP32: ' + str(msg[0]) + ': ' + msg[1])
    sys.exit(1);
