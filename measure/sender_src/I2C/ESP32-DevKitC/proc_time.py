# -*- coding: utf-8 -*-
import sys
import smbus
import subprocess
import random
import time
import RPi.GPIO as GPIO

SLAVE_ADDRESS = 0x40
notice_pin = 4

# GPIOのセットアップ
GPIO.setmode(GPIO.BCM)
GPIO.setup(notice_pin, GPIO.IN)

# I2Cバスにマスタとして接続
bus = smbus.SMBus(1)


def getdata(send_bytes):
  # Wait slave to be ready
  while GPIO.input(notice_pin) == GPIO.HIGH:
    pass

  # [cmd] 0:write 1:read
  bus.write_i2c_block_data(SLAVE_ADDRESS, 0, send_bytes)
  start_proc_time = time.time()

  # Wait slave to prepare response data
  while GPIO.input(notice_pin) == GPIO.LOW:
    pass

  end_proc_time = time.time()
  result = bus.read_i2c_block_data(SLAVE_ADDRESS, 1, 1)

  return result[0], end_proc_time - start_proc_time


if __name__ == '__main__':
  try:
    argvs = sys.argv
    data_dir = argvs[1]
    speed_hz = argvs[2]

    for send_bytes in [10000]:

      # 記録ファイルの生成
      file_path = data_dir + str(speed_hz) + 'Hz' + '_' + str(send_bytes) + 'bytes.txt'
      with open(file_path, mode = 'w', encoding='utf-8') as fh:
        pass

      # 送信データの作成
      send = []
      for i in range(send_bytes):
        send.append(random.randint(0, 255))

      # send_bytes回の試行
      for i in range(send_bytes):

        # データの送信
        result, execution_time = getdata([send[i]])

        # 受信データのエラーチェック
        err = 0 if result == send[i] else 1

        print('[I2C proc_time] {0}:{1}\t{2}\t{3}\t{4}'.format(i, send_bytes, speed_hz, execution_time, err))
        with open(file_path, mode='a', encoding='utf-8') as fh:
          fh.write('{0}:{1}\t{2}\n'.format(i, execution_time, err))

      # ログを消す
      subprocess.call(['clear'])
      print('[I2C proc_time] Recorded : {0}\t{1}'.format(send_bytes, speed_hz))

    sys.exit(0)
  except KeyboardInterrupt:
    sys.exit(0)
