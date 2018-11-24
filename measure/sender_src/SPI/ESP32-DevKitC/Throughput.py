# -*- coding: utf-8 -*-
import time
import sys
import subprocess
import spidev
import random
import time
import RPi.GPIO as GPIO

handshake_pin = 16
max_data_length = 4070;

# SPIのセットアップ
CE = 0
spi = spidev.SpiDev()
spi.open(0,CE)
spi.mode = 0b01

# GPIOのセットアップ
GPIO.setmode(GPIO.BCM)
GPIO.setup(handshake_pin, GPIO.IN)

def getdata(send_bytes):
  # send_bytesをxfer2で送信できるサイズに分割する
  send_blocks = [send_bytes[i: i+max_data_length] for i in range(0, len(send_bytes), max_data_length)]

  ###############################################
  # 送受信・計測
  ###############################################
  # Wait for slave to be ready
  while GPIO.input(handshake_pin) == 0:
    pass

  err = 0
  start_time = time.time()

  for block in send_blocks:
    # ESP32との通信では末尾1~8bytesがうまく送信されないため、末尾にダミーデータを付加(8bytes)
    block += [0, 0, 0, 0, 0, 0, 0, 0]
    # 送信するbyte数を先頭に付加する(2byte)
    l = len(block)
    block.insert(0, (l & 0xFF))
    block.insert(0, ((l >> 0x8) & 0xFF))

    # Wait for slave to be ready
    while GPIO.input(handshake_pin) == 0:
      pass

    # 送信
    spi.xfer2(block)

    # Wait for slave to be ready
    while GPIO.input(handshake_pin) == 0:
      pass

    # 受信
    result = spi.xfer2([0, 1, 0, 0, 0, 0, 0, 0])
    # 送受信誤りがあるかどうかを確認する
    err |= result[0]
  end_time = time.time()
  err = 0 if err == 0 else 1

  return end_time - start_time, err

if __name__ == '__main__':
  try:
    argvs = sys.argv
    data_dir = argvs[1]
    spi.max_speed_hz = int(argvs[2])
    speed_hz = int(argvs[2])

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

    for send_bytes in [16, 32, 64, 128, 256, 512, 1024]:
      # 記録ファイルの生成
      file_path = data_dir + str(speed_hz) + 'Hz' + '_' + str(send_bytes) + 'bytes.txt'
      with open(file_path, mode = 'w', encoding = 'utf-8') as fh:
        pass

      # 送信データの作成
      send = send_bytes_pattern * (send_bytes // max_data_length)
      send += send_bytes_pattern[0:(send_bytes % max_data_length)]

      # 1,000回の試行
      for i in range(1000):
        # データの送信
        execution_time, err = getdata(send)

        print('[SPI throughput] {0}:{1}\t{2}\t{3}\t{4}'.format(i, send_bytes, speed_hz, execution_time, err))
        with open(file_path, mode = 'a', encoding = 'utf-8') as fh:
          fh.write('{0}:{1}\t{2}\n'.format(i, execution_time, err))

      # ログを消す
      proc = subprocess.Popen(['clear'])
      proc.wait()
      print('[SPI throughput] Recorded : {0}\t{1}'.format(send_bytes, speed_hz))

    spi.close()
    sys.exit(0)
  except KeyboardInterrupt:
    spi.close()
    sys.exit(0)
