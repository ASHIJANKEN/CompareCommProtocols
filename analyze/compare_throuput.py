# -*- coding: utf-8 -*-

###########################################################
# それぞれのスループットのデータから比較を行い、スループットとエラー率をそれぞれ棒グラフと折れ線グラフにまとめる。
# analyze_throuputで生成したテキストを参照するので、事前にanalyze_throuputを実行しておくこと。
###########################################################

import re
import numpy as np
import matplotlib.pyplot as plt
import os

base_dir = '/Users/ashija/Documents/通信方法比較/'

# for ack_way in ['block_ack', 'each_ack']:
for ack_way in ['block_ack']:
  for shift_way in ['FET']:
    for send_bytes in [512, 1024, 2048, 4096]:
      # グラフ描画領域を作成
      fig1 = plt.figure(figsize=(10, 10))
      fig2 = plt.figure(figsize=(10, 10))
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

#       for (num, comm_way), delay_way in zip(enumerate(['SPI', 'i2c', 'uart']),['continuousnodelay', '', '', ]):
      for num, comm_way in enumerate(['SPI', 'i2c', 'uart']):
        throuput_array = []
        error_rate_array = []
        spdhz_array_for_error_rate = []
#         if comm_way == 'i2c':
#           speed_hz_arr = range(10000, 74001, 1000)
#         elif comm_way == 'SPI':
#           speed_hz_arr = range(10000, 5000001, 1000)
#         elif comm_way == 'uart':
#           speed_hz_arr = range(10000, 3000001, 1000)
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

            # スループット平均値と誤り率を得る
            val_found  = False
            for record in records:
              elms = re.split(':|\t', record)
              if speed_hz == int(elms[0]) and send_bytes == int(elms[1]):
                thput_bps = float(elms[2])
                error_rate = float(elms[8])
                val_found = True
            if val_found == False:
              continue
            # グラフ描画用に値を保存
            throuput_array.append((thput_bps * (1-error_rate)) / 1000)
            error_rate_array.append(error_rate*100)
            spdhz_array_for_error_rate.append(speed_hz)
          except IOError:
            print(throuput_file_path + ' cannot be opened.')
            throuput_array.append(0)
            continue

        # グラフを描画
        error_graph.plot([i/1000 for i in spdhz_array_for_error_rate], error_rate_array, '-D', linewidth = 4, label=comm_way.upper())
        if num == 0:
          left = np.arange(len(throuput_array))
        print(len(throuput_array))
        throuput_graph.bar(left[:len(throuput_array)]+width*num, throuput_array, align='center', width=width, label=comm_way.upper())

      # グラフ画像を保存
      plt.xticks(left + width, [str(i) for i in [j/1000 for j in speed_hz_arr]])
      error_graph.legend()
      throuput_graph.legend()
      error_graph.set_xlim(xmin=0)
      throuput_graph.set_title('When RPi sends ' + str(send_bytes) + ' bytes to Arduino')
      error_graph.set_title('When RPi sends ' + str(send_bytes) + ' bytes to Arduino')
      analyzed_data_dir = 'analyzed_data/'
      folder_dir = 'compare_throuput_' + ack_way + '(' + shift_way + ')/'
      pdf_path = base_dir + analyzed_data_dir + folder_dir + 'pdf'
      png_path = base_dir + analyzed_data_dir + folder_dir + 'png'
      try:
        os.mkdir(pdf_path)
        os.mkdir(png_path)
      except FileExistsError:
        pass
      fig1.savefig(pdf_path + '/' + str(send_bytes) + 'bytes_compare_error_rate(' + shift_way + ').pdf')
      fig1.savefig(png_path + '/' + str(send_bytes) + 'bytes_compare_error_rate(' + shift_way + ').png')
      fig2.savefig(pdf_path + '/' + str(send_bytes) + 'bytes_compare_throuput(' + shift_way + ').pdf')
      fig2.savefig(png_path + '/' + str(send_bytes) + 'bytes_compare_throuput(' + shift_way + ').png')
      plt.close()

      print(ack_way + ' : Record image of ' + str(send_bytes))
