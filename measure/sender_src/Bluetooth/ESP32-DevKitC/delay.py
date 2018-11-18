# -*- coding: utf-8 -*-

import time
import sys
import bluetooth
import subprocess
import random

# このアドレスは各自書き換えてください。
server_address = '30:AE:A4:CA:EA:1E'

def getdata(socket, send_bytes, max_speed_hz):
  start_time = time.time()
  # Send data
  socket.send(bytes(bytearray(send_bytes)))

  # Receive data
  result = socket.recv(1)
  end_time = time.time()

  return result[0], end_time - start_time

if __name__ == '__main__':
  try:
    argvs = sys.argv
    base_dir = argvs[1]
    speed_hz = int(argvs[2])

    for send_bytes in [10000]:

      #記録ファイルの生成
      file_path = base_dir + str(speed_hz) + 'Hz' + '_' + str(send_bytes) + 'bytes.txt'
      with open(file_path, mode = 'w', encoding = 'utf-8') as fh:
        pass

      # 送信データの作成
      send = []
      for i in range(send_bytes):
        send.append(random.randint(0, 255))

      # Bluetoothサーバーと接続
      port = 1
      socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
      socket.connect((server_address,port))
      time.sleep(3)

      # send_bytes回の試行
      for i in range(send_bytes):

        # データの送信
        result, execution_time = getdata(socket, [send[i]], speed_hz)

        # 受信データのエラーチェック
        err = 0 if result == send[i] else 1

        print('[Bluetooth delay] {0}:{1}\t{2}\t{3}\t{4}'.format(i, send_bytes, speed_hz, execution_time, err))
        with open(file_path, mode = 'a', encoding = 'utf-8') as fh:
          fh.write('{0}:{1}\t{2}\n'.format(i, execution_time, err))

      # Bluetoothサーバーとの接続を切断
      socket.close()

      # ログを消す
      proc = subprocess.Popen(['clear'])
      proc.wait()
      print('[Bluetooth delay] Recorded : {0}\t{1}'.format(send_bytes, speed_hz))

    socket.close()
    sys.exit(0)
  except KeyboardInterrupt:
    socket.close()
    sys.exit(0)
  except bluetooth.BluetoothError:
    print('Bluetooth connection is closed.')
    socket.close()
    sys.exit(0)
