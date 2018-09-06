# -*- coding: utf-8 -*-
import sys
import smbus
import random
import time

SLAVE_ADDRESS = 0x40

# I2Cバスにマスタとして接続
bus = smbus.SMBus(1)

def getdata(send_bytes):
  start_time = time.time()
  bus.write_i2c_block_data(SLAVE_ADDRESS, 0, send_bytes)
  result = bus.read_i2c_block_data(SLAVE_ADDRESS,1,1)
  end_time = time.time()

  return result[0], end_time - start_time

if __name__ == '__main__':
  try:
    argvs = sys.argv
    base_dir = argvs[1]
    speed_hz = argvs[2]

    for send_bytes in [10000]:

      # 記録ファイルの生成
      file_name = base_dir + str(speed_hz) + 'Hz' + '_' + str(send_bytes) + 'bytes_i2c_1byte.txt'
      with open(file_name, mode = 'w', encoding = 'utf-8') as fh:
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

        print('{0}:{1}\t{2}\t{3}\t{4}'.format(i, send_bytes, speed_hz, execution_time, err))
        with open(file_name, mode = 'a', encoding = 'utf-8') as fh:
          fh.write('{0}:{1}\t{2}\n'.format(i, execution_time, err))

    sys.exit(0)
  except KeyboardInterrupt:
    sys.exit(0)
