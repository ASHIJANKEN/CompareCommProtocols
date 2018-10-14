# -*- coding: utf-8 -*-

import time
import sys
import serial
import subprocess
import random

def getdata(send_bytes, max_speed_hz):
  result = []
  with serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=max_speed_hz,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1,
  ) as ser:
    start_time = time.time()
    ser.write(bytearray(send_bytes))
    result.append(ser.read(len(send_bytes)))
    end_time = time.time()
    ser.close()

  return int.from_bytes(result[0], 'big'), end_time - start_time

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

      # send_bytes回の試行
      for i in range(send_bytes):

        # データの送信
        result, execution_time = getdata([send[i]], speed_hz)

        # 受信データのエラーチェック
        err = 0 if result == send[i] else 1

        print('[UART delay] {0}:{1}\t{2}\t{3}\t{4}'.format(i, send_bytes, speed_hz, execution_time, err))
        with open(file_path, mode = 'a', encoding = 'utf-8') as fh:
          fh.write('{0}:{1}\t{2}\n'.format(i, execution_time, err))

      # ログを消す
      proc = subprocess.Popen(['clear'])
      proc.wait()
      print('[UART delay] Recorded : {0}\t{1}'.format(send_bytes, speed_hz))

    sys.exit(0)
  except KeyboardInterrupt:
    sys.exit(0)
