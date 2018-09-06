# -*- coding: utf-8 -*-
import time
import sys
import serial
import random

def getdata(send_bytes, max_speed_hz):
  result = []
  with serial.Serial('/dev/ttyS0',max_speed_hz,timeout=100) as ser:
    start_time = time.time()
    ser.write(bytearray(send_bytes))
    result.append(ser.read(len(send_bytes)))
    end_time = time.time()
    ser.close()

  return int.from_bytes(result[0], 'big'), end_time - start_time

if __name__ == '__main__':
  try:
    # 結果の保存場所の指定
    while True:
      print('Please set select level_shift_way.')
      print('level_shift_way: 1...FET  2...TXB  3...reg_div')
      cmd = input('> ')
      cmd = cmd.split(' ')
      if cmd[0] == '1':
        base_dir = 'UART_1byte(FET)/'
        break
      elif cmd[0] == '2':
        base_dir = 'UART_1byte(TXB)/'
        break
      elif cmd[0] == '3':
        base_dir = 'UART_1byte(reg_div)/'
        break
      else:
        print('Oops! Wrong command.')

    for speed_hz in [14400, 19200, 28800, 38400, 57600, 100000, 115200]:
      # Arduinoのスピードをセットさせる．
      while True:
        print("Next speed is {}. Please set serial speed of Arduino and type 'start'.".format(speed_hz))
        print("If you want to skip this speed, please type 'skip'.")
        cmd = input('> ')
        if cmd == 'start':
          break
        if cmd == 'skip':
          break
        else:
          print("Oops! Wrong command.")
      if cmd == 'skip':
        continue

      for send_bytes in [10000]:

        # 記録ファイルの生成
        file_name = base_dir + str(speed_hz) + 'Hz' + '_' + str(send_bytes) + 'bytes_uart_1byte.txt'
        with open(file_name, mode = 'w', encoding = 'utf-8') as fh:
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

          print('{0}:{1}\t{2}\t{3}\t{4}'.format(i, send_bytes, speed_hz, execution_time, err))
          with open(file_name, mode = 'a', encoding = 'utf-8') as fh:
            fh.write('{0}:{1}\t{2}\n'.format(i, execution_time, err))

    sys.exit(0)
  except KeyboardInterrupt:
    sys.exit(0)
