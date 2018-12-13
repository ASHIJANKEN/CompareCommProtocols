# -*- coding: utf-8 -*-

###########################################################
# 取得したデータからグラフを生成する。
# Python 3.xで実行すること!
###########################################################

import re
import matplotlib.pyplot as plt
import os
import subprocess
import json
import sys

def clear_log():
  proc = subprocess.Popen(['clear'])
  proc.wait()


if __name__ == '__main__':
  device = 'ESP32-DevKitC'
  level_shift = 'None'
  protocols = ['SPI', 'I2C', 'UART', 'Bluetooth', 'TCP']
  # protocols = ['SPI', 'I2C', 'UART', 'Bluetooth']
  # protocols = ['TCP']

  print('Are you sure to do start analyzing and generating graphs?')
  print('If it starts, old analyzed_data and graphs are immediately deleted and are overwritten by the program.')
  print('Type (yes / no)')
  while True:
    cmd = input('> ')
    if cmd == 'yes':
      break
    elif cmd == 'no':
      sys.exit(0)
      break
    else:
      print('Wrong word.')
      print('Type (yes / no)')

  print('Start analysis...')

  with open(os.path.abspath("../configuration.json"), mode = 'r') as f:
    config = json.load(f)

  # # proc_timeのデータを整理
  # # どのくらいゆらぐかをヒストグラムに出力
  # print('==================== [ Analyzing proc_time ] ====================')
  # # for protocol in ['SPI']:
  # for protocol in list(set(protocols) - set(['UART', 'Bluetooth'])):
  #   proc = subprocess.Popen(['python3', 'analyze_proc_time.py', device, protocol, level_shift])
  #   proc.wait()


  # clear_log()

  # # delayのデータを整理
  # # どのくらいゆらぐかをヒストグラムに出力
  # # 誤り率を折れ線グラフで出力
  # print('==================== [ Analyzing delay/fluctuation ] ====================')
  # for protocol in protocols:
  #   proc = subprocess.Popen(['python3', 'analyze_delay_fluctuation.py', device, protocol, level_shift])
  #   proc.wait()
  #   clear_log()

  # # throughputのデータを整理
  # # send_bytesごとの折れ線ブラフを出力
  # # 誤り率を折れ線グラフで出力
  # print('==================== [ Analyzing throughput ] ====================')
  # for protocol in protocols:
  #   proc = subprocess.Popen(['python3', 'analyze_throughput.py', device, protocol, level_shift])
  #   proc.wait()
  #   clear_log()

  # # delayの、ボーレートの変化による推移をグラフに出力
  # # 平均値や中央値などを基準に折れ線グラフに出力
  # # 誤り率を折れ線グラフで出力
  # print('==================== [ Comparing delay ] ====================')
  # for protocol in protocols:
  #   proc = subprocess.Popen(['python3', 'compare_delay_fluctuation.py', device, protocol, level_shift])
  #   proc.wait()
  # clear_log()

  # # プロトコルごとのdelayを比較
  # # ゆらぎをヒストグラムに出力して比較
  # # 平均値や中央値などの変化を折れ線グラフに出力して比較
  # # 誤り率を折れ線グラフで出力
  # print('==================== [ Comparing delay by protocol ] ====================')
  # proc = subprocess.Popen(['python3', 'compare_delay_fluctuation_by_protocol.py', device, level_shift])
  # proc.wait()

  # # clear_log()

  # # throughputの、ボーレートの変化による推移をグラフに出力
  # # send_bytesごとにthroughputを折れ線グラフで出力
  # # send_bytsごとの誤り率を折れ線グラフで出力
  # print('==================== [ Comparing throughput ] ====================')
  # for protocol in protocols:
  #   proc = subprocess.Popen(['python3', 'compare_throughput.py', device, protocol, level_shift])
  #   proc.wait()
  # clear_log()

  # プロトコルごとのthroughputを比較
  # send_bytesごとに、ボーレートの変化によるスループットの推移を棒グラフに出力して比較
  # # (ArduinoではI2CやUARTが断続的にしか通信できず、折れ線グラフが綺麗に出力できなかった。
  # # だからいくつかのボーレートをピックアップして、棒グラフで比較する形式をとった。ESPでは連続で取れているので、折れ線グラフ形式でいいと思う。)
  # # 誤り率も折れ線グラフで出力して比較
  print('==================== [ Comparing throughput by protocol (bar graph) ] ====================')
  proc = subprocess.Popen(['python3', 'compare_throughput_by_protocol_bar.py', device, level_shift])
  proc.wait()

  # プロトコルごとのthroughputを比較
  # send_bytesごとに、ボーレートの変化によるスループットの推移を折れ線グラフに出力して比較
  # # 誤り率も折れ線グラフで出力して比較
  print('==================== [ Comparing throughput by protocol (line graph) ] ====================')
  proc = subprocess.Popen(['python3', 'compare_throughput_by_protocol_line.py', device, level_shift])
  proc.wait()


  print('Done!')
