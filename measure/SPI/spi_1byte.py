# -*- coding: utf-8 -*-
import time
import sys
import subprocess
import spidev
import random

CE = 0
spi = spidev.SpiDev()
spi.open(0,CE)
spi.mode = 0b01

def getdata(send_bytes):
  # 受信用のダミーデータを加える
  send_bytes.append(0)

  # 送受信・計測
  start_time = time.time()
  result = spi.xfer2(send_bytes)
  end_time = time.time()

  return result[1], end_time - start_time

if __name__ == '__main__':
  try:
    argvs = sys.argv
    data_dir = argvs[1]
    spi.max_speed_hz = (int)argvs[2]

    for send_bytes in [10000]:
      # 記録ファイルの生成
      file_name = data_dir + str(speed_hz) + 'Hz' + '_' + str(send_bytes) + 'bytes.txt'
      with open(file_name, mode = 'w', encoding = 'utf-8') as fh:
        pass

      # 送信データの作成
      send = []
      for i in range(send_bytes):
        send.append(random.randint(0, 255))

      # send_bytes回の試行
      for i in range(send_bytes):
        # SPIレジスタのクリーンアップ
        getdata([0])

        # データの送信
        result, execution_time = getdata([send[i]])

        # 受信データのエラーチェック
        err = 0 if result == send[i] else 1

        print('{0}:{1}\t{2}\t{3}\t{4}'.format(i, send_bytes, speed_hz, execution_time, err))
        with open(file_name, mode = 'a', encoding = 'utf-8') as fh:
          fh.write('{0}:{1}\t{2}\n'.format(i, execution_time, err))

      print('Recorded : {0}\t{1}'.format(send_bytes, speed_hz))

    spi.close()
    sys.exit(0)
  except KeyboardInterrupt:
    spi.close()
    sys.exit(0)
