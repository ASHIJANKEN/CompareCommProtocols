# -*- coding: utf-8 -*-
#####################################################
# python2.x系で走らせる事！
#####################################################

import sys
import subprocess
import time
import signal

#####################################################
# settings
#####################################################

one_byte_continuous = {
  'base_dir_FET':'/home/pi/workspace/I2C_1byte_continuous(FET)/',
  'base_dir_MM':'/home/pi/workspace/I2C_1byte_continuous(MM)/',
  'base_dir_reg_div':'/home/pi/workspace/I2C_1byte_continuous(reg_div)/',
#   'speed_hz': range(10000, 78001, 1000),
  'speed_hz': range(10000, 300001, 1000),
  'file_name': 'i2c_1byte_continuous.py',
  'ino_name': '1byte',
}

throuput_block_ack_continuous = {'base_dir_FET':'/home/pi/workspace/I2C_throuput_block_ack_continuous(FET)/',
       'base_dir_MM':'/home/pi/workspace/I2C_throuput_block_ack_continuous(MM)/',
       'base_dir_reg_div':'/home/pi/workspace/I2C_throuput_block_ack_continuous(reg_div)/',
       'speed_hz': range(10000, 300001, 1000),
       'file_name': 'i2c_throuput_block_ack_continuous.py',
       'ino_name': 'throuput',
       }

proc_time_continuous = {'base_dir_FET':'/home/pi/workspace/I2C_proc_time_continuous(FET)/',
       'base_dir_MM':'/home/pi/workspace/I2C_proc_time_continuous(MM)/',
       'base_dir_reg_div':'/home/pi/workspace/I2C_proc_time_continuous(reg_div)/',
       'speed_hz': range(233000, 300001, 1000),
       'file_name': 'i2c_measure_proc_time_continuous.py',
       'ino_name': 'proc_time',
       }

if __name__ == '__main__':
  try:
    run_settings = None
    # どのスクリプトを呼び出すか決定
    while True:
      print('Please set select script to run.')
      print('1...1_byte  2...proc_time 3...throuput_block_ack')
      cmd = input('> ')
      if cmd[0] == '1':
        run_settings = one_byte_continuous
        break
      elif cmd[0] == '2':
        run_settings = proc_time_continuous
        break
      elif cmd[0] == '3':
        run_settings = throuput_block_ack_continuous
        break
      else:
        print('Oops! Wrong command.')

    # 結果の保存場所の指定
    while True:
      print('Please set select level_shift_way.')
      print('level_shift_way: 1...FET  2...MM  3...reg_div')
      cmd = input('> ')
      if cmd[0] == '1':
        base_dir = run_settings['base_dir_FET']
        break
      elif cmd[0] == '2':
        base_dir = run_settings['base_dir_MM']
        break
      elif cmd[0] == '3':
        base_dir = run_settings['base_dir_reg_div']
        break
      else:
        print('Oops! Wrong command.')

    for speed_hz in run_settings['speed_hz']:
      # 速度の変更
      baudrate = 'baudrate=' + str(speed_hz)
      subprocess.call(['sudo', 'modprobe', '-r', 'i2c_bcm2708'])
      subprocess.call(['sudo', 'modprobe', 'i2c_bcm2708', baudrate])

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
      up_proc = subprocess.Popen(['platformio', 'run'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
      for line in iter(up_proc.stdout.readline, b''):
        print(line)
      # 終わるまで待つ
      up_proc.wait()
      print('uploaded!')
      time.sleep(2)

      # 実際の送受信スクリプトを実行
      if run_settings == proc_time_continuous:
        print('execute experiment...')
        console = subprocess.Popen(["platformio serialports monitor -p /dev/ttyACM0 -b 9600"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        time.sleep(5)
        start_cmd_time = time.time()
        proc = subprocess.Popen(['python3', run_settings['file_name'], str(speed_hz)])

        # コンソールから結果を記録
        rcv_console = []
        for line in iter(console.stdout.readline, b''):
          if len(rcv_console) < 10002:
            if time.time() - start_cmd_time > 85:
              print("timeout!")
              break
            rcv_console.append(line)
          else:
            rcv_console.pop(0)
            rcv_console.pop(0)
            rcv_console = [i[:-2] for i in rcv_console]
            rcv_console = [i+'\n' for i in rcv_console]
            break
        console.send_signal(signal.SIGINT)
        console.terminate()
        proc.terminate()

        # ファイルに出力
        file_path = base_dir + str(speed_hz) + 'Hz_10000bytes_i2c_measure_proc_time.txt'
        with open(file_path, mode = 'a') as fh:
          for line in rcv_console:
            fh.write(line)

        time.sleep(3)

      else:
        print('execute experiment...')
        proc = subprocess.Popen(['python3', run_settings['file_name'], base_dir, str(speed_hz)])
        proc.wait()

    sys.exit(0)
  except KeyboardInterrupt:
    sys.exit(0)
