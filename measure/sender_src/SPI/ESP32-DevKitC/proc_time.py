# -*- coding: utf-8 -*-
import time
import sys
import subprocess
import spidev
import random
import RPi.GPIO as GPIO

handshake_pin = 16

# SPIのセットアップ
CE = 0
spi = spidev.SpiDev()
spi.open(0,CE)
spi.mode = 0b01

# GPIOのセットアップ
GPIO.setmode(GPIO.BCM)
GPIO.setup(handshake_pin, GPIO.IN)

def getdata(send_bytes):
  # Wait for slave to be ready
  while GPIO.input(handshake_pin) == 0:
    pass

  # 送信
  spi.xfer2(send_bytes + [0, 0, 0, 0, 0, 0, 0, 0])
  start_proc_time = time.time()

  # Wait for slave to be ready
  while GPIO.input(handshake_pin) == 0:
    pass

  # 受信
  end_proc_time = time.time()
  result = spi.xfer2([0, 0, 0, 0, 0, 0, 0, 0, 0])

  return result[0], end_proc_time - start_proc_time

if __name__ == '__main__':
  try:
    argvs = sys.argv
    data_dir = argvs[1]
    spi.max_speed_hz = int(argvs[2])

    for send_bytes in [10000]:

      # 記録ファイルの生成
      file_path = data_dir + str(spi.max_speed_hz) + 'Hz' + '_' + str(send_bytes) + 'bytes.txt'
      with open(file_path, mode = 'w', encoding = 'utf-8') as fh:
        pass

      # 送信データの作成
      send = []
      for i in range(send_bytes):
        send.append(random.randint(0, 255))

      # send_bytes回の試行
      for i in range(send_bytes):

        # データの送信
        result, proc_time = getdata([send[i]])

        # 受信データのエラーチェック
        err = 0 if result == send[i] else 1

        print('[SPI proc_time] {0}:{1}\t{2}\t{3}\t{4}'.format(i, send_bytes, spi.max_speed_hz, execution_time, err))
        with open(file_path, mode = 'a', encoding = 'utf-8') as fh:
          fh.write('{0}:{1}\t{2}\n'.format(i, execution_time, err))

      # ログを消す
      proc = subprocess.Popen(['clear'])
      proc.wait()
      print('[SPI proc_time] Recorded : {0}\t{1}'.format(send_bytes, spi.max_speed_hz))

    spi.close()
    sys.exit(0)
  except KeyboardInterrupt:
    spi.close()
    sys.exit(0)
