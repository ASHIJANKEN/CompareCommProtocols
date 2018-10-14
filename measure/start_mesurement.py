# -*- coding: utf-8 -*-

#####################################################
# python2.x系、3.x系の両方が実行できる環境を用意し、
# python2.x系で実行してください。
#####################################################

import sys
import os
import subprocess
import time
import signal
import json
import re

if __name__ == '__main__':
  try:
    with open(os.path.abspath('../configuration.json'), mode='r') as f:
      config = json.load(f)
    with open(os.path.abspath('path_config.json'), mode='r') as f:
      path_config = json.load(f)

    data_dir_path_base = os.path.abspath(path_config['measured_data_path'])
    receiver_src_path = os.path.abspath(path_config['receiver_src_path'])
    platformio_src_path = os.path.abspath(path_config['PlatformIO_src_path'])
    device = ''
    protocol = ''
    exp_type = ''
    level_shift = ''

    # どのデバイスの実験を行うか決定
    while True:
      print('Select device to measure.')
      print('1: Arduino_UNO 2: ESP32-DevKitC')
      cmd = input('> ')
      if cmd == 1:
        device = 'Arduino_UNO'
        break
      elif cmd == 2:
        device = 'ESP32-DevKitC'
        break
      else:
        print('Oops! Wrong command.')
        print('\n')

    # どのデバイスの実験を行うか決定
    while True:
      print('Select protocol to measure.')
      print('1: SPI 2: I2C 3: UART')
      cmd = input('> ')
      if cmd == 1:
        protocol = 'SPI'
        break
      elif cmd == 2:
        protocol = 'I2C'
        break
      elif cmd == 3:
        protocol = 'UART'
        break
      else:
        print('Oops! Wrong command.')
        print('\n')

    # 何の実験を行うか決定
    if protocol == 'I2C':
      # I2Cの時はproc_timeを測れる
      while True:
        print('Select what you want to measure.')
        print('1...delay  2...throughput 3...proc_time')
        cmd = input('> ')
        if cmd == 1:
          exp_type = 'delay'
          break
        elif cmd == 2:
          exp_type = 'throughput'
          break
        elif cmd == 3:
          exp_type = 'proc_time'
          break
        else:
          print('Oops! Wrong command.')
          print('\n')
    else:
      # I2C以外の時はproc_timeを測る必要がないので選択肢から除外
      while True:
        print('Select what you want to measure.')
        print('1...delay  2...throughput')
        cmd = input('> ')
        if cmd == 1:
          exp_type = 'delay'
          break
        elif cmd == 2:
          exp_type = 'throughput'
          break
        else:
          print('Oops! Wrong command.')
          print('\n')

    # 何のレベルシフト方法を用いるか決定
    while True:
      print('Select way of level shifting.')
      print('1: level_shift(2N7000)  2: level_shift(MM)  3: voltage_divider  4: None')
      cmd = input('> ')
      if cmd == 1:
        level_shift = '2N7000'
        break
      elif cmd == 2:
        level_shift = 'MM'
        break
      elif cmd == 3:
        level_shift = 'voltage_divider'
        break
      elif cmd == 4:
        level_shift = 'None'
        break
      else:
        print('Oops! Wrong command.')
        print('\n')

    # 実験するボーレートを取得
    speed_hz_list = eval(config[exp_type][protocol]['speed_hz'])
    speed_hz_list.sort()

    # 実験スクリプトのパスを取得
    script_path = protocol + '/' + device + '/' + config[exp_type][protocol]['script_name']

    # データ記録用フォルダを生成
    data_dir_path = data_dir_path_base + '/' + device + '/' + protocol + '/' + level_shift + '/' + exp_type + '/'
    try:
      os.makedirs(data_dir_path)
    except OSError as e:
      if e.errno != os.errno.EEXIST:
        raise

    # デバイスに書き込むソースコードのパスを取得
    receiver_src_name = config[exp_type][protocol]['receiver_src_name'][device]
    receiver_src_path = receiver_src_path + '/' + protocol + '/' + device + '/' + exp_type[0].upper() + exp_type[1:] + '/' + receiver_src_name

    #####################################################
    # 実験開始
    #####################################################

    for speed_hz in speed_hz_list:
      if protocol == 'I2C':
        # Raspberry PiのI2Cでの通信速度を変更
        baudrate = 'baudrate=' + str(speed_hz)
        subprocess.call(['sudo', 'modprobe', '-r', 'i2c_bcm2708'])
        subprocess.call(['sudo', 'modprobe', 'i2c_bcm2708', baudrate])

      # Arduinoなどに書き込むソースコードを作成
      print('Creating source code to write...')
      with open(receiver_src_path, mode='r') as fh:
        code = fh.read()
      if protocol == 'SPI':
        pass
      elif protocol == 'I2C':
        split_pos = code.find('Wire.setClock(') + 14
        code = code[:split_pos] + str(speed_hz) + code[split_pos:]
      elif protocol == 'UART':
        split_pos = code.find('Serial.begin(') + 13
        code = code[:split_pos] + str(speed_hz) + code[split_pos:]
      receiver_src_extension = re.findall(r'\.[^\.]+$', receiver_src_name)[-1]
      with open(platformio_src_path + '/' + 'receiver_src' + receiver_src_extension, mode='w') as fh:
        fh.write(code)

      # アップロード
      print('Uploading...')
      if protocol == 'UART' and device == 'Arduino_UNO':
        rts_proc = subprocess.Popen(['gpio', '-g', 'mode', '17', 'ALT5'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        rts_proc.wait()

        up_proc = subprocess.Popen(['platformio', 'run', '-e', device + '_UART'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in iter(up_proc.stdout.readline, b''):
          print(line)
        # 終わるまで待つ
        status = up_proc.wait()

        in_proc = subprocess.Popen(['gpio', '-g', 'mode', '17', 'IN'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        in_proc.wait()

      else:
        up_proc = subprocess.Popen(['platformio', 'run', '-e', device], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in iter(up_proc.stdout.readline, b''):
          print(line)
        # 終わるまで待つ
        status = up_proc.wait()

      time.sleep(1)
      if status != 0:
        print('[ERROR] Upload failed!')
        sys.exit(0)

      print('Successfully uploaded!')
      time.sleep(1)

      # 実際の送受信スクリプトを実行
      if exp_type == 'proc_time':
        print('Executing script for the experiment...')
        console = subprocess.Popen(['platformio serialports monitor -p /dev/ttyACM0 -b 9600'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        time.sleep(5)
        start_cmd_time = time.time()
        proc = subprocess.Popen(['python3', script_path, str(speed_hz)])

        # コンソールから結果を記録
        rcv_console = []
        for line in iter(console.stdout.readline, b''):
          if len(rcv_console) < 10002:
            if time.time() - start_cmd_time > 85:
              print('timeout!')
              break
            rcv_console.append(line)
          else:
            rcv_console.pop(0)
            rcv_console.pop(0)
            rcv_console = [i[:-2] for i in rcv_console]
            rcv_console = [i + '\n' for i in rcv_console]
            break
        console.send_signal(signal.SIGINT)
        console.terminate()
        proc.terminate()

        # ファイルに出力
        file_path = data_dir_path + str(speed_hz) + 'Hz.txt'
        with open(file_path, mode='a') as fh:
          for line in rcv_console:
            fh.write(line)

        time.sleep(3)

      else:
        print('Executing script for the experiment...')
        proc = subprocess.Popen(['python3', script_path, data_dir_path, str(speed_hz)])
        proc.wait()

      # ログを消す
      subprocess.call(['clear'])

    sys.exit(0)
  except KeyboardInterrupt:
    sys.exit(0)
