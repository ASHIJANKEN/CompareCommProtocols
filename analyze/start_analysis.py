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
import multiprocessing

def clear_log():
  proc = subprocess.Popen(['clear'])
  proc.wait()


def analyze_proc_time(device, protocol, level_shift):
    proc = subprocess.Popen(['python3', 'analyze_proc_time.py', device, protocol, level_shift])
    proc.wait()
    print("End analyze_proc_time: {}, {}, {}".format(device, protocol, level_shift))


def analyze_delay_fluctuation(device, protocol, level_shift):
    proc = subprocess.Popen(['python3', 'analyze_delay_fluctuation.py', device, protocol, level_shift])
    proc.wait()
    print("End analyze_delay_fluctuation: {}, {}, {}".format(device, protocol, level_shift))


def analyze_throughput(device, protocol, level_shift):
    proc = subprocess.Popen(['python3', 'analyze_throughput.py', device, protocol, level_shift])
    proc.wait()
    print("End analyze_throughput: {}, {}, {}".format(device, protocol, level_shift))


def compare_delay_fluctuation(device, protocol, level_shift):
    proc = subprocess.Popen(['python3', 'compare_delay_fluctuation.py', device, protocol, level_shift])
    proc.wait()
    print("End compare_delay_fluctuation: {}, {}, {}".format(device, protocol, level_shift))


def compare_throughput(device, protocol, level_shift):
    proc = subprocess.Popen(['python3', 'compare_throughput.py', device, protocol, level_shift])
    proc.wait()
    print("End compare_throughput: {}, {}, {}".format(device, protocol, level_shift))


def start_multithread(target_func, arg_tuple):
  thread_list = []
  for t in arg_tuple:
    thread = multiprocessing.Process(target = target_func, args = t)
    thread_list.append(thread)

  for thread in thread_list:
    thread.start()

  for thread in thread_list:
    thread.join()


if __name__ == '__main__':
  device = 'ESP32-DevKitC'
  level_shift = 'None'
  # device = 'Arduino_UNO'
  # level_shift = '2N7000'

  if device == 'Arduino_UNO':
    # protocols = ['SPI', 'I2C', 'UART']
    protocols = ['SPI']
  else:
    # protocols = ['SPI', 'I2C', 'UART', 'Bluetooth', 'WiFi']
    protocols = ['Bluetooth', 'WiFi']

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

  # # # proc_timeのデータを整理
  # # # どのくらいゆらぐかをヒストグラムに出力
  # print('==================== [ Analyzing proc_time ] ====================')
  # tuple_list = []
  # if device == 'Arduino_UNO':
  #   protocols_for_proc_time = list(set(protocols) - set(['UART', 'SPI']))
  # if device == 'ESP32-DevKitC':
  #   protocols_for_proc_time = list(set(protocols) - set(['UART', 'Bluetooth']))
  # for protocol in protocols_for_proc_time:
  #   tuple_list.append((device, protocol, level_shift))
  # start_multithread(analyze_proc_time, tuple_list)
  # clear_log()

  # # delayのデータを整理
  # # どのくらいゆらぐかをヒストグラムに出力
  # # 誤り率を折れ線グラフで出力
  # print('==================== [ Analyzing delay/fluctuation ] ====================')
  # tuple_list = []
  # for protocol in protocols:
  #   tuple_list.append((device, protocol, level_shift))
  # start_multithread(analyze_delay_fluctuation, tuple_list)
  # clear_log()

  # # throughputのデータを整理
  # # send_bytesごとの折れ線ブラフを出力
  # # 誤り率を折れ線グラフで出力
  # print('==================== [ Analyzing throughput ] ====================')
  # tuple_list = []
  # for protocol in protocols:
  #   tuple_list.append((device, protocol, level_shift))
  # start_multithread(analyze_throughput, tuple_list)

  # clear_log()

  # # delayの、ボーレートの変化による推移をグラフに出力
  # # 平均値や中央値などを基準に折れ線グラフに出力
  # # 誤り率を折れ線グラフで出力
  # print('==================== [ Comparing delay ] ====================')
  # tuple_list = []
  # for protocol in protocols:
  #   tuple_list.append((device, protocol, level_shift))
  # start_multithread(compare_delay_fluctuation, tuple_list)
  # clear_log()

  # # プロトコルごとのdelayを比較
  # # ゆらぎをヒストグラムに出力して比較
  # # 平均値や中央値などの変化を折れ線グラフに出力して比較
  # # 誤り率を折れ線グラフで出力
  # print('==================== [ Comparing delay by protocol ] ====================')
  # proc = subprocess.Popen(['python3', 'compare_delay_fluctuation_by_protocol.py', device, level_shift])
  # proc.wait()

  # clear_log()

  # throughputの、ボーレートの変化による推移をグラフに出力
  # send_bytesごとにthroughputを折れ線グラフで出力
  # send_bytsごとの誤り率を折れ線グラフで出力
  print('==================== [ Comparing throughput ] ====================')
  tuple_list = []
  for protocol in protocols:
    tuple_list.append((device, protocol, level_shift))
  start_multithread(compare_throughput, tuple_list)
  clear_log()

  # # プロトコルごとのthroughputを比較
  # # send_bytesごとに、ボーレートの変化によるスループットの推移を棒グラフに出力して比較
  # # (ArduinoではI2CやUARTが断続的にしか通信できず、折れ線グラフが綺麗に出力できなかった。
  # # だからいくつかのボーレートをピックアップして、棒グラフで比較する形式をとった。ESPでは連続で取れているので、折れ線グラフ形式でいいと思う。)
  # # 誤り率も折れ線グラフで出力して比較
  # print('==================== [ Comparing throughput by protocol (bar graph) ] ====================')
  # proc = subprocess.Popen(['python3', 'compare_throughput_by_protocol_bar.py', device, level_shift])
  # proc.wait()

  # # プロトコルごとのthroughputを比較
  # # send_bytesごとに、ボーレートの変化によるスループットの推移を折れ線グラフに出力して比較
  # # # 誤り率も折れ線グラフで出力して比較
  # print('==================== [ Comparing throughput by protocol (line graph) ] ====================')
  # proc = subprocess.Popen(['python3', 'compare_throughput_by_protocol_line.py', device, level_shift])
  # proc.wait()


  print('Done!')
