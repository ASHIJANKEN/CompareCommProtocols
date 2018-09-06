# -*- coding: utf-8 -*-

###########################################################
# ack_wayの観点から比較を行い、スループットとエラー率をそれぞれ棒グラフと折れ線グラフにまとめる。
# analyze_throuputで生成したテキストを参照するので、事前にanalyze_throuputを実行しておくこと。
###########################################################

import re
import numpy as np
import matplotlib.pyplot as plt
import os

base_dir = '/Users/ashija/Documents/通信方法比較/'

for comm_way in ['SPI', 'i2c', 'uart']:
  for shift_way in ['FET']:
    for send_bytes in [512, 1024, 2048, 4096]:
      # グラフ描画領域を作成
      fig1 = plt.figure(figsize=(8, 8))
      fig2 = plt.figure(figsize=(8, 8))
      plt.rcParams["font.size"] = 14
      error_graph = fig1.add_subplot(1,1,1)
      throuput_graph = fig2.add_subplot(1,1,1)
      error_graph.grid(which='major',color='gray',linestyle='--')
      error_graph.grid(which='minor',color='gray',linestyle='dotted')
      throuput_graph.grid(which='major',color='gray',linestyle='--')
      throuput_graph.grid(which='minor',color='gray',linestyle='dotted')
    #   plt.yscale('log')
      width = 0.2
      throuput_graph.set_xlabel('Baudrate[kbaud(kHz)]')
      throuput_graph.set_ylabel('Throuput[kbps]')
      error_graph.set_xlabel('Baudrate[kbaud(kHz)]')
      error_graph.set_ylabel('Error Rate[%]')

      all_throuput_array = []
      all_error_rate_array = []
      ack_way_array = ['block_ack', 'each_ack']
      for num, ack_way in enumerate(ack_way_array):
        throuput_array = []
        error_rate_array = []
        speed_hz_arr = [10000, 14400, 19200, 28800, 38400, 57600, 100000, 115200]
        for speed_hz in speed_hz_arr:
          # スループットのデータを取得
          try:
            analyzed_data_dir = 'analyzed_data/' + comm_way.upper() + '/'
            folder_dir = comm_way.upper() + '_throuput_' + ack_way + '(' + shift_way + ')/'
            throuput_file = comm_way.upper() + '_throuput_' + ack_way + '(' + shift_way + ').txt'
            throuput_file_path = base_dir + analyzed_data_dir + folder_dir + throuput_file
            with open(throuput_file_path, mode = 'r', encoding = 'utf-8') as fh:
              records = fh.readlines()
              records.pop(0)
          except IOError:
            print(throuput_file_path + ' cannot be opened.')
            continue

          # スループット平均値と誤り率を得る
          val_found  = False
          for record in records:
            elms = re.split(':|\t', record)
#             print('{}   {}'.format(int(elms[0]), int(elms[1])))
            if speed_hz == int(elms[0]) and send_bytes == int(elms[1]):
#               print("AAAA")
              thput_bps = float(elms[2])
              error_rate = float(elms[8])
              val_found = True
              break
          if val_found == False:
            print('val not found {} {} {} {}'.format(comm_way, ack_way, speed_hz, send_bytes))
            continue
          # グラフ描画用に値を保存
          throuput_array.append((thput_bps * (1-error_rate)) / 1000)
          error_rate_array.append(error_rate*100)

        # グラフデータを保存
        all_throuput_array.append(throuput_array)
        all_error_rate_array.append(error_rate_array)

      # グラフを描画
      ack_name = ['Block', 'Individual']
      minimum_num = min([len(i) for i in all_throuput_array])
      for num, (error_data, throuput_data) in enumerate(zip(all_error_rate_array, all_throuput_array)):
        error_graph.plot([i/1000 for i in speed_hz_arr][:minimum_num], error_data[:minimum_num], '-D', linewidth = 4, label=ack_name[num])
        if num == 0:
          left = np.arange(len(throuput_data))
        throuput_graph.bar(left[:minimum_num]+width*num, throuput_data[:minimum_num], align='center', width=width, label=ack_name[num])

      # グラフ画像を保存
      plt.xticks(left + width / 2, [str(i) for i in [j/1000 for j in speed_hz_arr]])
      error_graph.legend()
      throuput_graph.legend()
      error_graph.set_ylim(ymin = 0)
      error_graph.set_xlim(xmin=0)
      throuput_graph.set_title('When RPi sends ' + str(send_bytes) + ' bytes to Arduino\n' + comm_way.upper())
      error_graph.set_title('When RPi sends ' + str(send_bytes) + ' bytes to Arduino\n' + comm_way.upper())
      analyzed_data_dir = 'analyzed_data/' + comm_way.upper() + '/'
      folder_dir = 'compare_ack_way' + '(' + shift_way + ')/'
      pdf_path = base_dir + analyzed_data_dir + folder_dir + 'pdf'
      png_path = base_dir + analyzed_data_dir + folder_dir + 'png'
      try:
        os.mkdir(pdf_path)
        os.mkdir(png_path)
      except FileExistsError:
        pass
      fig1.savefig(pdf_path + '/' + comm_way.upper() + str(send_bytes) + 'bytes_compare_error_rate(' + shift_way + ').pdf')
      fig1.savefig(png_path + '/' + comm_way.upper() + str(send_bytes) + 'bytes_compare_error_rate(' + shift_way + ').png')
      fig2.savefig(pdf_path + '/' + comm_way.upper() + str(send_bytes) + 'bytes_compare_throuput(' + shift_way + ').pdf')
      fig2.savefig(png_path + '/' + comm_way.upper() + str(send_bytes) + 'bytes_compare_throuput(' + shift_way + ').png')
      plt.close()

      print(comm_way + ' : Record image of ' + str(send_bytes) + 'bytes')
