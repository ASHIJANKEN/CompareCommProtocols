# -*- coding: utf-8 -*-
import time
import sys
import spidev

CE = 0
spi = spidev.SpiDev()
spi.open(0,CE)
spi.mode = 0b01
max_data_length = 4094

def getdata(send_bytes, delay):
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
    time.sleep(delay)
    result = spi.xfer2([0])

    # 送受信誤りがあるかどうかを確認する
    err |= result[-1]
  end_time = time.time()

  err = 0 if err == 0 else 1

  return end_time - start_time, err

if __name__ == '__main__':
  try:
    # 結果の保存場所の指定
    while True:
      print('Please set select level_shift_way.')
      print('level_shift_way: 1...FET  2...TXB  3...reg_div')
      cmd = input('> ')
      cmd = cmd.split(' ')
      if cmd[0] == '1':
        base_dir = 'delaySPI_throuput_block_ack(FET)/'
        break
      elif cmd[0] == '2':
        base_dir = 'delaySPI_throuput_block_ack(TXB)/'
        break
      elif cmd[0] == '3':
        base_dir = 'delaySPI_throuput_block_ack(reg_div)/'
        break
      else:
        print('Oops! Wrong command.')

    # 送信データをファイルから読み込む
    with open('send_bytes.txt', mode = 'r', encoding = 'utf-8') as fh:
      default_send_bytes = fh.readlines()
      # 末尾改行文字を除去
      default_send_bytes = [i.rstrip() for i in default_send_bytes]
      # 要素をintへ変換
      default_send_bytes = [int(i) for i in default_send_bytes]
      # default_send_bytesの長さをmax_data_lengthにする
      leng = len(default_send_bytes)
      default_send_bytes = default_send_bytes * (max_data_length // leng)
      default_send_bytes = default_send_bytes + default_send_bytes[0:(max_data_length % leng)]

    for speed_hz in [14400, 19200, 28800, 38400, 57600, 100000, 115200]:
      spi.max_speed_hz = speed_hz

      for send_bytes in [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096]:
        for delay in [0.1, 0.01]:
          # 記録ファイルの生成
          file_name = base_dir + str(speed_hz) + 'Hz' + '_' + str(send_bytes) + 'bytes_' + str(delay) + '_SPI_throuput.txt'
          with open(file_name, mode = 'w', encoding = 'utf-8') as fh:
            pass

          # 送信データの作成
          send = default_send_bytes * (send_bytes // max_data_length)
          send = send + default_send_bytes[0:(send_bytes % max_data_length)]

          # 1,000回の試行
          for i in range(1000):
            # データの送信
            execution_time, err = getdata(send, delay)

            print('{0}:{1}\t{2}\t{3}\t{4}\t{5}'.format(i, send_bytes, speed_hz, delay, execution_time, err))
            with open(file_name, mode = 'a', encoding = 'utf-8') as fh:
              fh.write('{0}:{1}\t{2}\n'.format(i, execution_time, err))

    spi.close()
    sys.exit(0)
  except KeyboardInterrupt:
    spi.close()
    sys.exit(0)
