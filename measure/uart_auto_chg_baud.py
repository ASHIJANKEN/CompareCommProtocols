# -*- coding: utf-8 -*-
#####################################################
# python2.x系で走らせる事！
#####################################################

import sys
import subprocess
import time

#####################################################
# settings
#####################################################

one_byte_continuous = {'base_dir_FET':'/home/pi/workspace/UART_1byte_continuous(FET)/',
       'base_dir_TXB':'/home/pi/workspace/UART_1byte_continuous(TXB)/',
       'base_dir_reg_div':'/home/pi/workspace/UART_1byte_continuous(reg_div)/',
       'speed_hz': range(10000, 8000001, 1000),
       'file_name': 'uart_1byte_continuous.py',
       'ino_name': '1byte',
       }

throuput_block_ack_continuous = {'base_dir_FET':'/home/pi/workspace/UART_throuput_block_ack_continuous(FET)/',
       'base_dir_TXB':'/home/pi/workspace/UART_throuput_block_ack_continuous(TXB)/',
       'base_dir_reg_div':'/home/pi/workspace/UART_throuput_block_ack_continuous(reg_div)/',
       'speed_hz': range(10000, 3000001, 1000),
       'file_name': 'uart_throuput_block_ack_continuous.py',
       'ino_name': 'throuput',
       }

if __name__ == '__main__':
  try:
    run_settings = None
    # どのスクリプトを呼び出すか決定
    while True:
      print('Please set select script to run.')
      print('1...1_byte  2...throuput_block_ack')
      cmd = input('> ')
      if cmd[0] == '1':
        run_settings = one_byte_continuous
        break
      elif cmd[0] == '2':
        run_settings = throuput_block_ack_continuous
        break
      else:
        print('Oops! Wrong command.')

    # 結果の保存場所の指定
    while True:
      print('Please set select level_shift_way.')
      print('level_shift_way: 1...FET  2...TXB  3...reg_div')
      cmd = input('> ')
      if cmd[0] == '1':
        base_dir = run_settings['base_dir_FET']
        break
      elif cmd[0] == '2':
        base_dir = run_settings['base_dir_TXB']
        break
      elif cmd[0] == '3':
        base_dir = run_settings['base_dir_reg_div']
        break
      else:
        print('Oops! Wrong command.')

    for speed_hz in run_settings['speed_hz']:
      # Arduinoのスケッチを読み込み
      print('Start marging sketch...')
      code = ''
      with open(run_settings['ino_name'] + '_upper.txt', mode = 'r') as fh:
        code = code + fh.read()
      code = code[:-1] + str(speed_hz)
      with open(run_settings['ino_name'] + '_lower.txt', mode = 'r') as fh:
        code = code + fh.read()

      # Arduinoのスケッチを作成
      with open('src/sketch.ino', mode = 'w') as fh:
        fh.write(code)
      # アップロード
      print('uploading...')
      rts_proc = subprocess.Popen(['gpio', '-g', 'mode', '17', 'ALT5'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
      rts_proc.wait()
      up_proc = subprocess.Popen(['platformio', 'run'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
      for line in iter(up_proc.stdout.readline, b''):
        print(line)
      # 終わるまで待つ
      up_proc.wait()
      print('uploaded!')
      in_proc = subprocess.Popen(['gpio', '-g', 'mode', '17', 'IN'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
      in_proc.wait()
      time.sleep(2)

      # 実際の送受信スクリプトを実行
      print('execute experiment...')
      proc = subprocess.Popen(['python3', run_settings['file_name'], base_dir, str(speed_hz)])
      proc.wait()

    sys.exit(0)
  except KeyboardInterrupt:
    sys.exit(0)
