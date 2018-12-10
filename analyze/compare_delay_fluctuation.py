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
  error_graph.set_xlabel('Baudrate[kbaud(kHz)]')
  error_graph.set_ylabel('Error Rate[%]')
  delay_graph.grid(which='major',color='gray',linestyle='--')
  delay_graph.grid(which='minor',color='gray',linestyle='dotted')
  delay_graph.set_xlabel('Baudrate[kbaud(kHz)]')
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
    analyzed_delay_dir = '../analyzed_data/' + protocol + '/' + device + '/Delay/' + level_shift + '/'
    delay_file_path = analyzed_delay_dir + 'delay.txt'
    with open(delay_file_path, mode = 'r', encoding = 'utf-8') as fh:
      all_records = fh.readlines()
      all_records.pop(0)
      records = {}
      for record in all_records:
        elms = re.split(':|\t', record)
        if send_bytes == int(elms[1]):
          records[speed_hz] = elms
  except IOError:
    print(delay_file_path + ' cannot be opened.')
    continue

  for speed_hz in speed_hz_arr:
    # 2Dと誤り率を得る
    elms = records.get(speed_hz)
    if elms == None
      continue

    # グラフ描画用に値を保存
    delay_avr_array.append(float(elms[2]))
    delay_med_array.append(float(elms[3]))
    delay_max_array.append(float(elms[5]))
    delay_min_array.append(float(elms[6]))
    error_rate_array.append(float(elms[8]) * 100)
    rec_spdhz_array.append(speed_hz/1000)

  # グラフを描画
#         error_graph.plot(rec_spdhz_array, error_rate_array, '-D', markersize=4, linewidth = 2, label=comm_way.upper())
#         delay_graph.plot(rec_spdhz_array, delay_med_array, '-D', markersize=4, linewidth = 2, label='Median value[ms]')
#         delay_graph.plot(rec_spdhz_array, delay_max_array, '-D', markersize=4, linewidth = 2, label='Maximum value[ms]')
#         delay_graph.plot(rec_spdhz_array, delay_min_array, '-D', markersize=4, linewidth = 2, label='Minimum value[ms]')
  error_graph.plot(rec_spdhz_array, error_rate_array, linewidth = 2, label=comm_way.upper())
  delay_graph.plot(rec_spdhz_array, delay_avr_array, linewidth = 2, label='Avarage value[ms]')
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
  delay_graph.set_title('2Delay (' + comm_way.upper() + ')')
  error_graph.set_title('Error Rate (' + comm_way.upper() + ')')

  pdf_folder_path = analyzed_delay_dir + '/pdf'
  png_folder_path = analyzed_delay_dir + '/png'
  os.mkdir(png_folder_path, exist_ok = True)
  os.mkdir(pdf_folder_path, exist_ok = True)

  fig1.savefig(pdf_folder_path + '/compare_error_rate.pdf')
  fig1.savefig(png_folder_path + '/compare_error_rate.png')
  fig2.savefig(pdf_folder_path + '/compare_2delay.pdf')
  fig2.savefig(png_folder_path + '/compare_2delay.png')
  plt.close()

  print('Record image of ' + protocol)













  # comm_wayごとにデータを配列に格納
  all_delay_array['max'].append(delay_max_array)
  all_delay_array['med'].append(delay_med_array)
  all_delay_array['avr'].append(delay_avr_array)
  all_delay_array['min'].append(delay_min_array)
  all_error_rate_array.append(error_rate_array)
  all_rec_spdhz_array.append(rec_spdhz_array)

  # 通信方法ごとに比較するためのグラフを出力
  error_fig = plt.figure(figsize=(10, 5))
  plt.rcParams["font.size"] = 14
  error_graph = error_fig.add_subplot(1,1,1)
  error_graph.grid(which='major',color='gray',linestyle='--')
  error_graph.grid(which='minor',color='gray',linestyle='dotted')
  error_graph.set_xlabel('Baudrate[kbaud(kHz)]')
  error_graph.set_ylabel('Error Rate[%]')
  delay_graph = []
  delay_fig = []
  for i in range(4):
    delay_fig.append(plt.figure(figsize=(10, 5)))
    delay_graph.append(delay_fig[i].add_subplot(1,1,1))
    delay_graph[i].grid(which='major',color='gray',linestyle='--')
    delay_graph[i].grid(which='minor',color='gray',linestyle='dotted')
    delay_graph[i].set_xlabel('Baudrate[kbaud(kHz)]')
    delay_graph[i].set_ylabel('2Delay[ms]')

  # グラフを描画
  for i,comm_way in enumerate(comm_way_arr):
#         error_graph.plot(all_rec_spdhz_array[i], all_error_rate_array[i], '-D', markersize=4, linewidth = 2, label=comm_way.upper())
    error_graph.plot(all_rec_spdhz_array[i], all_error_rate_array[i], linewidth = 2, label=comm_way.upper())
    for j, val in enumerate(['max', 'min', 'med', 'avr']):
#           delay_graph[j].plot(all_rec_spdhz_array[i], all_delay_array[val][i], '-D', markersize=4, linewidth = 2, label=comm_way.upper())
      delay_graph[j].plot(all_rec_spdhz_array[i], all_delay_array[val][i], linewidth = 2, label=comm_way.upper())

  # グラフ画像を保存
  error_graph.legend()
  error_graph.set_ylim(ymin = 0, ymax = 100)
  error_graph.set_xlim(xmin=0)
  error_graph.set_title('Compare Error Rate')
  analyzed_delay_dir = 'analyzed_data/'
  folder_dir = 'compare_2delay(' + level_shift + ')/'
  pdf_path = base_dir + analyzed_delay_dir + folder_dir + 'pdf'
  png_path = base_dir + analyzed_delay_dir + folder_dir + 'png'
  try:
    os.makedirs(pdf_path)
    os.makedirs(png_path)
  except FileExistsError:
    pass
  error_fig.savefig(pdf_path + '/' + 'compare_error_rate(' + level_shift + ').pdf')
  error_fig.savefig(png_path + '/' + 'compare_error_rate(' + level_shift + ').png')
  for i, val in enumerate(['Maximum', 'Minimum', 'Median', 'Average']):
    delay_graph[i].legend()
    delay_graph[i].set_ylim(ymin = 0)
    delay_graph[i].set_xlim(xmin=0)
    delay_graph[i].set_title('Compare 2Delay(' + val + ')')
    delay_fig[i].savefig(pdf_path + '/' + 'compare_' + val.lower() + '_2delay(' + level_shift + ').pdf')
    delay_fig[i].savefig(png_path + '/' + 'compare_' + val.lower() + '_2delay(' + level_shift + ').png')

  plt.close()

  print('Done.')