# -*- coding: utf-8 -*-

###########################################################
# それぞれの2delayのデータからbaudrateによる比較を行い、2delayの値と誤り率をそれぞれ折れ線グラフでまとめる。最小値と最大値と中央値が出る。
# 同様にして、通信方法ごとの比較として３つのグラフを一つにまとめたものも出力する。最小値と最大値と中央値ごとに出力する。
# analyze_DFで生成したテキストを参照するので、事前にanalyze_DFを実行しておくこと。
###########################################################

import re
import matplotlib.pyplot as plt
import os
import sys
import json


if __name__ == '__main__':

  argvs = sys.argv
  device = argvs[1]
  protocol = argvs[2]
  level_shift = argvs[3]

  all_delay_array = {'max':[], 'min':[], 'med':[], 'avr':[]}
  all_error_rate_array = []
  all_rec_spdhz_array = []

  # グラフ描画領域を作成
  fig1 = plt.figure(figsize=(10, 5))
  fig2 = plt.figure(figsize=(10, 5))
  plt.rcParams["font.size"] = 14
  error_graph = fig1.add_subplot(1,1,1)
  delay_graph = fig2.add_subplot(1,1,1)
  error_graph.grid(which='major',color='gray',linestyle='--')
  error_graph.grid(which='minor',color='gray',linestyle='dotted')
  error_graph.set_xlabel('Baudrate[kbaud]')
  error_graph.set_ylabel('Error Rate[%]')
  delay_graph.grid(which='major',color='gray',linestyle='--')
  delay_graph.grid(which='minor',color='gray',linestyle='dotted')
  delay_graph.set_xlabel('Baudrate[kbaud]')
  delay_graph.set_ylabel('2Delay[ms]')

  delay_min_array = []
  delay_max_array = []
  delay_med_array = []
  delay_avr_array = []
  error_rate_array = []
  rec_spdhz_array = []

  # speed_hzの情報を取り出す
  with open(os.path.abspath('../configuration.json'), mode='r') as f:
    config = json.load(f)
  speed_hz_arr = eval(config['delay'][protocol]['speed_hz'])
  speed_hz_arr.sort()

  # 2delayのデータを取得
  try:
    analyzed_delay_dir = '../analyzed_data/' + protocol + '/' + device + '/delay/' + level_shift + '/'
    delay_file_path = analyzed_delay_dir + 'delay.txt'
    with open(os.path.abspath(delay_file_path), mode = 'r', encoding = 'utf-8') as fh:
      all_records = fh.readlines()
      all_records.pop(0)
      records = {}
      for record in all_records:
        elms = re.split(':|\t', record)

        if int(elms[1]) == 10000:
          records[int(elms[0])] = elms
  except IOError:
    print(delay_file_path + ' cannot be opened.')
    sys.exit(1)

  for speed_hz in speed_hz_arr:
    # 2Dと誤り率を得る
    elms = records.get(speed_hz)
    if elms == None:
      continue

    # グラフ描画用に値を保存
    delay_avr_array.append(float(elms[2]))
    delay_med_array.append(float(elms[3]))
    delay_max_array.append(float(elms[5]))
    delay_min_array.append(float(elms[6]))
    error_rate_array.append(float(elms[8]) * 100)
    rec_spdhz_array.append(speed_hz/1000)

  if protocol in ['WiFi', 'Bluetooth']:
    speed_hz_arr = list(set(list(range(10000, 3000001, 1000)) + [10000, 14400, 19200, 28800, 38400, 57600, 115200]))
    delay_avr_array = delay_avr_array * len(speed_hz_arr)
    delay_med_array = delay_med_array * len(speed_hz_arr)
    delay_max_array = delay_max_array * len(speed_hz_arr)
    delay_min_array = delay_min_array * len(speed_hz_arr)
    error_rate_array = error_rate_array * len(speed_hz_arr)
    rec_spdhz_array = [i/1000 for i in speed_hz_arr]

  # グラフを描画
#         error_graph.plot(rec_spdhz_array, error_rate_array, '-D', markersize=4, linewidth = 2, label=protocol)
#         delay_graph.plot(rec_spdhz_array, delay_med_array, '-D', markersize=4, linewidth = 2, label='Median value[ms]')
#         delay_graph.plot(rec_spdhz_array, delay_max_array, '-D', markersize=4, linewidth = 2, label='Maximum value[ms]')
#         delay_graph.plot(rec_spdhz_array, delay_min_array, '-D', markersize=4, linewidth = 2, label='Minimum value[ms]')
  error_graph.plot(rec_spdhz_array, error_rate_array, linewidth = 2, label=protocol)
  # delay_graph.plot(rec_spdhz_array, delay_avr_array, linewidth = 2, label='Avarage value[ms]')
  delay_graph.plot(rec_spdhz_array, delay_med_array, linewidth = 2, label='Median value[ms]')
  delay_graph.plot(rec_spdhz_array, delay_max_array, linewidth = 2, label='Maximum value[ms]')
  delay_graph.plot(rec_spdhz_array, delay_min_array, linewidth = 2, label='Minimum value[ms]')

  # グラフ画像を保存
  error_graph.legend()
  delay_graph.legend()
  error_graph.set_ylim(ymin = 0, ymax = 100)
  error_graph.set_xlim(xmin=0)
  delay_graph.set_ylim(ymin = 0)
  delay_graph.set_xlim(xmin=0)
  delay_graph.set_title('2Delay (' + protocol + ')')
  error_graph.set_title('Error Rate (' + protocol + ')')

  pdf_folder_path = analyzed_delay_dir + '/pdf'
  png_folder_path = analyzed_delay_dir + '/png'
  os.makedirs(png_folder_path, exist_ok = True)
  os.makedirs(pdf_folder_path, exist_ok = True)

  fig1.savefig(pdf_folder_path + '/compare_error_rate.pdf')
  fig1.savefig(png_folder_path + '/compare_error_rate.png')
  fig2.savefig(pdf_folder_path + '/compare_2delay.pdf')
  fig2.savefig(png_folder_path + '/compare_2delay.png')
  plt.close()

  print('Record image of ' + protocol)
