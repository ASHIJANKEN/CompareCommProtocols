# -*- coding: utf-8 -*-

###########################################################
# 取得したデータからグラフを生成する。
# Python 3.xで実行すること!
###########################################################

import re
import matplotlib.pyplot as plt
import os
import subprocess

def clear_log():
  proc = subprocess.Popen(['clear'])
  proc.wait()


if __name__ == '__main__':
  print('Are you sure to do start analyzing and generating graphs?')
  print('If it starts, old files are immediately deleted and are overwritten by the program.')
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

  with open(os.path.abspath("../configration.json"), mode = 'r') as f:
    config = json.load(f)

  # proc_timeのデータを整理、ヒストグラムを出力
  print('==================== [ Analyzing proc_time ] ====================')
  proc = subprocess.Popen(['python3', 'analyze_proc_time.py', device, protocol, level_shift])
  proc.wait()

  clear_log()

  # delayのデータを整理、グラフを出力
  print('==================== [ Analyzing delay/fluctuation ] ====================')
  proc = subprocess.Popen(['python3', 'analyze_delay_fluctuation.py', device, protocol, level_shift])
  proc.wait()

  clear_log()

  # throughputのデータを整理、グラフを出力
  print('==================== [ Analyzing throughput ] ====================')
  proc = subprocess.Popen(['python3', 'analyze_throughput.py', device, protocol, level_shift])
  proc.wait()

  clear_log()

  # delayを比較、グラフに出力
  print('==================== [ Comparing delay ] ====================')
  proc = subprocess.Popen(['python3', 'compare_delay_fluctuation.py', device, protocol, level_shift])
  proc.wait()