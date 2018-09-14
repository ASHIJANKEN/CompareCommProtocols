# -*- coding: utf-8 -*-
import time
import sys
import subprocess
import spidev

CE = 0
spi = spidev.SpiDev()
spi.open(0,CE)
spi.mode = 0b01
max_data_length = 4094
notice_pin = 18

def getdata(send_bytes):
  # send_bytesをxfer2で送信できるサイズに分割する
  send_blocks = [send_bytes[i: i+max_data_length] for i in range(0, len(send_bytes), max_data_length)]

  ###############################################
  # 送受信・計測
  ###############################################
  err = 0
  start_time = time.time()

  for block in send_blocks:
    # 送信するbyte数を先頭に付加する(2byte)
    l = len(block)
    block.insert(0, (l & 0xFF))
    block.insert(0, ((l >> 0x8) & 0xFF))

    # 送信
    spi.xfer2(block)
    # 受信
    result = spi.xfer2([0])

    # 送受信誤りがあるかどうかを確認する
    err |= result[-1]
  end_time = time.time()
  err = 0 if err == 0 else 1

  return end_time - start_time, err

if __name__ == '__main__':
  try:
    argvs = sys.argv
    data_dir = argvs[1]
    spi.max_speed_hz = (int)argvs[2]

    # 送信データをファイルから読み込む
    with open('send_bytes.txt', mode = 'r', encoding = 'utf-8') as fh:
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
