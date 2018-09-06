# -*- coding: utf-8 -*-

###########################################################
# それぞれの2delayのデータからbaudrateとレベルシフト方法による比較を行い、2delayの値と誤り率をそれぞれ折れ線グラフでまとめる。
# 通信方法ごとに、最小値と最大値と中央値で比較結果を出力する。
# analyze_DFで生成したテキストを参照するので、事前にanalyze_DFを実行しておくこと。
###########################################################

import re
import matplotlib.pyplot as plt
import os

base_dir = '/Users/ashija/Documents/通信方法比較/'

# for ack_way in ['block_ack', 'each_ack']:
for ack_way in ['block_ack']:
  comm_way_arr = ['SPI', 'i2c', 'uart']
#   comm_way_arr = ['uart']
  for (num, comm_way), delay_way in zip(enumerate(comm_way_arr), ['continuousnodelay', '', '', ]):
#   for (num, comm_way), delay_way in zip(enumerate(['SPI']),['continuousnodelay']):
    for send_bytes in [10000]:
      all_delay_array = {'max':[], 'min':[], 'med':[], 'avr':[]}
      all_error_rate_array = []
      all_rec_spdhz_array = []

      levelshift_arr = ['FET', 'reg_div']
      for shift_way in levelshift_arr:
        delay_min_array = []
        delay_max_array = []
        delay_med_array = []
        delay_avr_array = []
        error_rate_array = []
        rec_spdhz_array = []
        if comm_way == 'i2c':
          speed_hz_arr = list(set(list(range(10000, 300001, 1000)) + [10000, 14400, 19200, 28800, 38400, 57600]))
          speed_hz_arr.sort()
        elif comm_way == 'SPI':
          speed_hz_arr = list(set(list(range(10000, 5000001, 1000)) + [10000, 14400, 19200, 28800, 38400, 57600, 100000, 115200]))
          speed_hz_arr.sort()
        elif comm_way == 'uart':
          speed_hz_arr = list(set(list(range(10000, 8000001, 1000)) + [10000, 14400, 19200, 28800, 38400, 57600, 100000, 115200]))
          speed_hz_arr.sort()

        # 2delayのデータを取得
        try:
          analyzed_data_dir = 'analyzed_data/' + comm_way.upper() + '/'
          folder_dir = comm_way.upper() + '_2delay(' + shift_way + ')/'
          throuput_file = comm_way.upper() + '_2delay(' + shift_way + ').txt'
          throuput_file_path = base_dir + analyzed_data_dir + folder_dir + throuput_file
          with open(throuput_file_path, mode='r', encoding='utf-8') as fh:
            all_records = fh.readlines()
            all_records.pop(0)
            records = []
            for record in all_records:
              elms = re.split(':|\t', record)
              if send_bytes == int(elms[1]):
                records.append(record)
        except IOError:
          print(throuput_file_path + ' cannot be opened.')
          continue

        for speed_hz in speed_hz_arr:
          # 2Dと誤り率を得る
          for record in records:
            elms = re.split(':|\t', record)
            if speed_hz == int(elms[0]) and send_bytes == int(elms[1]):
              # グラフ描画用に値を保存
              delay_avr_array.append(float(elms[2]))
              delay_med_array.append(float(elms[3]))
              delay_max_array.append(float(elms[5]))
              delay_min_array.append(float(elms[6]))
              error_rate_array.append(float(elms[8]) * 100)
              rec_spdhz_array.append(speed_hz / 1000)
              break

        # レベルシフト回路ごとにデータを配列に格納
        all_delay_array['max'].append(delay_max_array)
        all_delay_array['med'].append(delay_med_array)
        all_delay_array['avr'].append(delay_avr_array)
        all_delay_array['min'].append(delay_min_array)
        all_error_rate_array.append(error_rate_array)
        all_rec_spdhz_array.append(rec_spdhz_array)

      # レベルシフト回路ごとに比較するためのグラフを出力
      error_fig = plt.figure(figsize=(10, 5))
      plt.rcParams["font.size"] = 14
      error_graph = error_fig.add_subplot(1, 1, 1)
      error_graph.grid(which='major', color='gray', linestyle='--')
      error_graph.grid(which='minor', color='gray', linestyle='dotted')
      error_graph.set_xlabel('Baudrate[kbaud(kHz)]')
      error_graph.set_ylabel('Error Rate[%]')
      delay_graph = []
      delay_fig = []
      for i in range(4):
        delay_fig.append(plt.figure(figsize=(10, 5)))
        delay_graph.append(delay_fig[i].add_subplot(1, 1, 1))
        delay_graph[i].grid(which='major', color='gray', linestyle='--')
        delay_graph[i].grid(which='minor', color='gray', linestyle='dotted')
        delay_graph[i].set_xlabel('Baudrate[kbaud(kHz)]')
        delay_graph[i].set_ylabel('2Delay[ms]')

      # グラフを描画
      for i, shift_way in enumerate(levelshift_arr):
#         error_graph.plot(all_rec_spdhz_array[i], all_error_rate_array[i], '-D', markersize=4, linewidth = 2, label=comm_way.upper())
        error_graph.plot(all_rec_spdhz_array[i], all_error_rate_array[i], linewidth=2, label=shift_way)
        for j, val in enumerate(['max', 'min', 'med', 'avr']):
#           delay_graph[j].plot(all_rec_spdhz_array[i], all_delay_array[val][i], '-D', markersize=4, linewidth = 2, label=comm_way.upper())
          delay_graph[j].plot(all_rec_spdhz_array[i], all_delay_array[val][i], linewidth=2, label=shift_way)

      # グラフ画像を保存
      error_graph.legend()
      error_graph.set_ylim(ymin=0, ymax=100)
      error_graph.set_xlim(xmin=0)
      error_graph.set_title('Compare Error Rate')
      analyzed_data_dir = 'analyzed_data/'
      folder_dir = comm_way.upper() + '/' + 'compare_levelshift_2delay/'
      pdf_path = base_dir + analyzed_data_dir + folder_dir + 'pdf'
      png_path = base_dir + analyzed_data_dir + folder_dir + 'png'
      try:
        os.makedirs(pdf_path)
        os.makedirs(png_path)
      except FileExistsError:
        pass
      error_fig.savefig(pdf_path + '/' + 'compare_error_rate.pdf')
      error_fig.savefig(png_path + '/' + 'compare_error_rate.png')
      for i, val in enumerate(['Maximum', 'Minimum', 'Median', 'Average']):
        delay_graph[i].legend()
        delay_graph[i].set_ylim(ymin=0)
        delay_graph[i].set_xlim(xmin=0)
        delay_graph[i].set_title('Compare 2Delay(' + val + ')')
        delay_fig[i].savefig(pdf_path + '/' + 'compare_' + val.lower() + '_2delay.pdf')
        delay_fig[i].savefig(png_path + '/' + 'compare_' + val.lower() + '_2delay.png')

      plt.close()

print('Done.')
