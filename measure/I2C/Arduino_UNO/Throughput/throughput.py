# -*- coding: utf-8 -*-

import sys
import smbus
import subprocess
import time

SLAVE_ADDRESS = 0x40
max_data_length = 31

# I2Cバスにマスタとして接続
bus = smbus.SMBus(1)


def getdata(send_bytes):
  # send_bytesをwrite_i2c_block_dataで送信できるサイズに分割する
  send_blocks = [send_bytes[i: i + max_data_length] for i in range(0, len(send_bytes), max_data_length)]

  ###############################################
  # 送受信・計測
  ###############################################
  start_time = time.time()

  err = 0
  for block in send_blocks:
    # 送受信
    bus.write_i2c_block_data(SLAVE_ADDRESS, 0, block)
    result = bus.read_i2c_block_data(SLAVE_ADDRESS, 1, 1)

    # 送受信誤りがあるかどうかを確認する
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
      send_bytes_pattern = fh.readlines()

    # 末尾改行文字を除去
    send_bytes_pattern = [i.rstrip() for i in send_bytes_pattern]
    # 要素をintへ変換
    send_bytes_pattern = [int(i) for i in send_bytes_pattern]
    # send_bytes_patternの長さをmax_data_lengthにする
    leng = len(send_bytes_pattern)
    send_bytes_pattern *= (max_data_length // leng)
    send_bytes_pattern += send_bytes_pattern[0:(max_data_length % leng)]

    for send_bytes in [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]:
      # 記録ファイルの生成
      file_path = data_dir + str(speed_hz) + 'Hz' + '_' + str(send_bytes) + 'bytes.txt'
      with open(file_path, mode='w', encoding='utf-8') as fh:
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
