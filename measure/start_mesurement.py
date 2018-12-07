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

device = ''
protocol = ''
exp_type = ''
level_shift = ''


def create_receiver_src():
  if protocol in ['SPI', 'Bluetooth', 'TCP']:
    return
  elif device == 'ESP32-DevKitC' and protocol == 'I2C':
    return
  else:
    with open(receiver_src_path, mode='r') as fh:
      code = fh.read()

    if protocol == 'I2C':
      split_pos = code.find('Wire.setClock(') + 14
      code = code[:split_pos] + str(speed_hz) + code[split_pos:]
    elif protocol == 'UART':
      if device == 'Arduino_UNO':
        split_pos = code.find('Serial.begin(') + 13
      elif device == 'ESP32-DevKitC':
        split_pos = code.find('.baud_rate = ') + 13
      code = code[:split_pos] + str(speed_hz) + code[split_pos:]
    receiver_src_extension = re.findall(r'\.[^\.]+$', receiver_src_name)[-1]

    if device == 'Arduino_UNO':
      with open(platformio_src_path + '/' + 'receiver_src' + receiver_src_extension, mode='w') as fh:
        fh.write(code)
    elif device == 'ESP32-DevKitC':
      with open(receiver_src_folder_path + 'main/' + receiver_src_name, mode='w') as fh:
        fh.write(code)


def flash_receiver_src():
  attempt_time = 0

  while True:
    attempt_time += 1

    if device == 'Arduino_UNO':
      if device == 'UART':
        rts_proc = subprocess.Popen(['gpio', '-g', 'mode', '17', 'ALT5'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        rts_proc.wait()

        up_proc = subprocess.Popen(['platformio', 'run', '-e', device + '_' + protocol], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in iter(up_proc.stdout.readline, b''):
          print(line)
        # 終わるまで待つ
        status = up_proc.wait()

        in_proc = subprocess.Popen(['gpio', '-g', 'mode', '17', 'IN'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        in_proc.wait()

      else:
        up_proc = subprocess.Popen(['platformio', 'run', '-e', device + '_' + protocol], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in iter(up_proc.stdout.readline, b''):
          print(line)
        # 終わるまで待つ
        status = up_proc.wait()

    elif device == 'ESP32-DevKitC':
      if protocol in ['SPI', 'I2C']:
        if flash_receiver_src.flashed_once == True:
          return 0

      # Makefileのあるところまで移動
      os.chdir(receiver_src_folder_path)

      up_proc = subprocess.Popen(['make', '-j4', 'flash'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
      for line in iter(up_proc.stdout.readline, b''):
        print(line)
      # 終わるまで待つ
      status = up_proc.wait()


      # 元の場所へ戻る
      os.chdir(working_dir_path)

    else:
      pass

    if status != 0:
      print('[ERROR] Flash failed!')
      if attempt_time < 3:
        continue
      else:
        sys.exit(0)

    print('Successfully flashed!')
    flash_receiver_src.flashed_once = True
    break

  return status
flash_receiver_src.flashed_once = False # This is for settings of ESP32-DevKitC(SPI)


def measure_proc_time():
  if protocol == 'I2C' and device == 'Arduino_UNO':
    console = subprocess.Popen(['platformio serialports monitor -p /dev/ttyACM0 -b 9600'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    time.sleep(5)
    start_cmd_time = time.time()
    proc = subprocess.Popen(['python3', script_path, str(speed_hz)])

    # コンソールから結果を記録
    rcv_console = []
    for line in iter(console.stdout.readline, b''):
      if len(rcv_console) < 10002:
        if time.time() - start_cmd_time > 300:
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

  elif device == 'ESP32-DevKitC':
    if protocol == 'TCP':
      # Makefileのあるところまで移動
      os.chdir(receiver_src_folder_path)

      console = subprocess.Popen(['make monitor'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
      time.sleep(10)
      start_cmd_time = time.time()
      proc = subprocess.Popen(['python3', script_path, str(speed_hz)])

      # コンソールから結果を記録
      rcv_console = []
      for line in iter(console.stdout.readline, b''):
        if time.time() - start_cmd_time > 85:
          print('timeout!')
          break
        if line.startswith(protocol):
          elms = line.split()
          rcv_console.append(elms[2] + '\n')
          if elms[1] == '10000':
            break

      console.send_signal(signal.SIGINT)
      console.terminate()
      proc.terminate()

      # 元の場所へ戻る
      os.chdir(working_dir_path)

    else:
      proc = subprocess.Popen(['python3', script_path, data_dir_path, str(speed_hz)])
      proc.wait()
      return

  # ファイルに出力
  file_path = data_dir_path + str(speed_hz) + 'Hz_10000bytes.txt'
  with open(file_path, mode='a') as fh:
    for line in rcv_console:
      fh.write(line)

  time.sleep(2)


if __name__ == '__main__':
  try:
    # カレントディレクトリパスを取得
    working_dir_path = os.getcwd()

    with open(os.path.abspath('../configuration.json'), mode='r') as f:
      config = json.load(f)
    with open(os.path.abspath('path_config.json'), mode='r') as f:
      path_config = json.load(f)

    data_dir_path_base = os.path.abspath(path_config['measured_data_path'])
    sender_src_path = os.path.abspath(path_config['sender_src_path'])
    receiver_src_path = os.path.abspath(path_config['receiver_src_path'])
    platformio_src_path = os.path.abspath(path_config['PlatformIO_src_path'])

    # どのデバイスの実験を行うか決定
    while True:
      print('Select device to measure.')
      print('1:Arduino_UNO 2:ESP32-DevKitC')
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
      print('1:SPI 2:I2C 3:UART 4:Bluetooth 5:TCP')
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
      elif cmd == 4:
        protocol = 'Bluetooth'
        break
      elif cmd == 5:
        protocol = 'TCP'
        break
      else:
        print('Oops! Wrong command.')
        print('\n')

    # 何の実験を行うか決定
    if protocol in ['SPI', 'I2C', 'TCP']:
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
      # 無線通信では関係ないのでNone
      if protocol in ['Bluetooth', 'TCP']:
        level_shift = 'None'
        break

      print('Select way of level shifting.')
      print('1:level_shift(2N7000)  2:level_shift(MM)  3:voltage_divider  4:None')
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
    script_path = sender_src_path + '/' + protocol + '/' + device + '/' + config[exp_type][protocol]['script_name']

    # データ記録用フォルダを生成
    data_dir_path = data_dir_path_base + '/' + device + '/' + protocol + '/' + level_shift + '/' + exp_type + '/'
    try:
      os.makedirs(data_dir_path)
    except OSError as e:
      if e.errno != os.errno.EEXIST:
        raise

    # デバイスに書き込むソースコードのパスを取得
    receiver_src_name = config[exp_type][protocol]['receiver_src_name'][device]
    dirname_protocol = (exp_type[0].upper() + exp_type[1:]) if exp_type != 'proc_time' else 'ProcTime'
    receiver_src_folder_path = receiver_src_path + '/' + protocol + '/' + device + '/' + dirname_protocol + '/'
    receiver_src_path = receiver_src_folder_path + receiver_src_name

    #####################################################
    # 実験開始
    #####################################################

    for speed_hz in speed_hz_list:
      if protocol == 'I2C':
        # Raspberry PiのI2Cでの通信速度を変更
        baudrate = 'baudrate=' + str(speed_hz)
        subprocess.call(['sudo', 'modprobe', '-r', 'i2c_bcm2708'])
        subprocess.call(['sudo', 'modprobe', 'i2c_bcm2708', baudrate])

      # Arduinoなどに書き込むソースコードを作成(SPI除く)
      print('Creating source code to write...')
      create_receiver_src()

      # アップロード
      print('Flashing...')
      status = flash_receiver_src()
      time.sleep(1)

      if status != 0:
        sys.exit(0)

      time.sleep(1)

      # 実際の送受信スクリプトを実行
      print('Executing script for the experiment...')
      if exp_type == 'proc_time':
        measure_proc_time()

      else:
        proc = subprocess.Popen(['python3', script_path, data_dir_path, str(speed_hz)])
        proc.wait()

      # ログを消す
      subprocess.call(['clear'])

    sys.exit(0)
  except KeyboardInterrupt:
    sys.exit(0)
