# -*- coding: utf-8 -*-
import sys
import smbus
import subprocess
import random
import time
import RPi.GPIO as GPIO

SLAVE_ADDRESS = 0x40
notice_pin = 4
max_data_length = 30

# GPIOのセットアップ
GPIO.setmode(GPIO.BCM)
GPIO.setup(notice_pin, GPIO.IN)

# I2Cバスにマスタとして接続
bus = smbus.SMBus(1)


def getdata(send_bytes):
  # send_bytesをwrite_i2c_block_dataで送信できるサイズに分割する
  send_blocks = [send_bytes[i: i + (max_data_length)] for i in range(0, len(send_bytes), max_data_length)]

  # Wait slave to be ready
  while GPIO.input(notice_pin) == GPIO.HIGH:
    pass

  ###############################################
  # 送受信・計測
  ###############################################
  start_time = time.time()
  err = 0
  for i, block in enumerate(send_blocks):
    # Add data length to the head of block
    block.insert(0, len(block))

    # Wait slave to be ready
    while GPIO.input(notice_pin) == GPIO.HIGH:
      pass

    # Send data
    # [cmd] 0:write 1:read
    bus.write_i2c_block_data(SLAVE_ADDRESS, 0, block)

    # Wait slave to prepare response data
    while GPIO.input(notice_pin) == GPIO.HIGH:
      pass

    # Receive data(result of previous transaction)
    result = bus.read_i2c_block_data(SLAVE_ADDRESS, 1, 1)
    # Check error
    if i != 0:
      err |= result[0]

  # Receive data(result of last transaction)
  result = bus.read_i2c_block_data(SLAVE_ADDRESS, 1, 1)
  # Check error
  err |= result[0]

  end_time = time.time()
  err = 0 if err == 0 else 1

  return end_time - start_time, err


if __name__ == '__main__':
  try:
    argvs = sys.argv
    data_dir = argvs[1]
    speed_hz = argvs[2]

    # 送信データをファイルから読み込む
    with open('send_bytes.txt', mode='r', encoding='utf-8') as fh:
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

      # 記録ファイルの生成
      file_path = data_dir + str(speed_hz) + 'Hz' + '_' + str(send_bytes) + 'bytes.txt'
      with open(file_path, mode = 'w', encoding='utf-8') as fh:
        pass

      # 送信データの作成
      send = send_bytes_pattern * (send_bytes // max_data_length)
      send += send_bytes_pattern[0:(send_bytes % max_data_length)]

      # 1,000回の試行
      for i in range(1000):

        # データの送信
        execution_time, err = getdata(send)

        print('[I2C throughput] {0}:{1}\t{2}\t{3}\t{4}'.format(i, send_bytes, speed_hz, execution_time, err))
        with open(file_path, mode='a', encoding='utf-8') as fh:
          fh.write('{0}:{1}\t{2}\n'.format(i, execution_time, err))

      # ログを消す
      subprocess.call(['clear'])
      print('[I2C throughput] Recorded : {0}\t{1}'.format(send_bytes, speed_hz))

    sys.exit(0)
  except KeyboardInterrupt:
    sys.exit(0)
