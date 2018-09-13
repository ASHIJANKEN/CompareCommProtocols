# -*- coding: utf-8 -*-
import time
import sys
import serial
import RPi.GPIO as GPIO

max_data_length = 63
notice_pin = 18

# GPIOのセットアップ
GPIO.setmode(GPIO.BCM)
GPIO.setup(notice_pin, GPIO.OUT)

def getdata(send_bytes, max_speed_hz):
  # send_bytesをxfer2で送信できるサイズに分割する
  send_blocks = [send_bytes[i: i+max_data_length] for i in range(0, len(send_bytes), max_data_length)]

  ###############################################
  # 送受信・計測
  ###############################################
  result = []
  with serial.Serial('/dev/ttyS0',max_speed_hz,timeout=100) as ser:
    # 送信スタートの合図
    GPIO.output(notice_pin, True)
    start_time = time.time()
    for i, block in enumerate(send_blocks):
      # 送信するbyte数を先頭に付加する(1byte)
      l = len(block)
      block.insert(0, (l & 0xFF))
      ser.write(bytearray(block))
      # 送信リクエスト
      result.extend(ser.read(1))
    end_time = time.time()

    # 送信終了の合図
    GPIO.output(notice_pin, False)
    ser.close()

  # 送受信誤りがあるかどうかを確認する
  err = 0
  for i in result:
    if i != 0:
      err = 1
      break

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
        base_dir = 'UART_throuput_block_ack(FET)/'
        break
      elif cmd[0] == '2':
        base_dir = 'UART_throuput_block_ack(TXB)/'
        break
      elif cmd[0] == '3':
        base_dir = 'UART_throuput_block_ack(reg_div)/'
        break
      else:
        print('Oops! Wrong command.')

    # 送信データをファイルから読み込む
    with open('send_bytes.txt', mode = 'r', encoding = 'utf-8') as fh:
      elms = fh.readlines()
      # 末尾改行文字を除去
      elms = [i.rstrip() for i in elms]
      # 要素をintへ変換
      elms =[int(i) for i in elms]
      # default_send_bytesの長さをmax_data_lengthにする
      leng = len(elms)
      default_send_bytes = elms * (max_data_length // leng)
      default_send_bytes = default_send_bytes + elms[0:(max_data_length % leng)]

    for speed_hz in [14400, 19200, 28800, 38400, 57600, 100000, 115200]:
      # Arduinoのスピードをセットさせる．
      while True:
        print("Next speed is {}. Please set serial speed of Arduino and type 'start'.".format(speed_hz))
        cmd = input('> ')
        if cmd == 'start':
          break
        if cmd == 'skip':
          break
        else:
          print("Oops! Wrong command.")
      if cmd == 'skip':
        continue

      for send_bytes in [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096]:
        # 記録ファイルの生成
        file_name = base_dir + str(speed_hz) + 'Hz' + '_' + str(send_bytes) + 'bytes_uart_throuput.txt'
        with open(file_name, mode = 'w', encoding = 'utf-8') as fh:
          pass

        # 送信データの作成
        send = []
        send = default_send_bytes * (send_bytes // len(default_send_bytes))
        send = send + default_send_bytes[0:(send_bytes % len(default_send_bytes))]

        # 1,000回の試行
        for i in range(1000):

          # データの送信
          execution_time, err = getdata(send, speed_hz)

          print('{0}:{1}\t{2}\t{3}\t{4}'.format(i, send_bytes, speed_hz, execution_time, err))
          with open(file_name, mode = 'a', encoding = 'utf-8') as fh:
            fh.write('{0}:{1}\t{2}\n'.format(i, execution_time, err))

    sys.exit(0)
  except KeyboardInterrupt:
    sys.exit(0)
