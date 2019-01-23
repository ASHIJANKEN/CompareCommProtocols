# -*- coding: utf-8 -*-

###########################################################
# それぞれの最大のスループットのデータから比較を行い、スループットとエラー率をそれぞれ棒グラフと折れ線グラフにまとめる。
# analyze_throuputで生成したテキストを参照するので、事前にanalyze_throuputを実行しておくこと。
###########################################################

import re
import numpy as np
import matplotlib.pyplot as plt
import os

base_dir = '/Users/ashija/Documents/通信方法比較/'

for ack_way in ['block_ack']:
  for shift_way in ['FET']:

    for send_bytes in [512, 1024]:
      # グラフ描画領域を作成
      fig2 = plt.figure(figsize=(8, 8))
      plt.rcParams["font.size"] = 14
      throuput_graph = fig2.add_subplot(1,1,1)
      throuput_graph.grid(which='major',color='gray',linestyle='--')
      throuput_graph.grid(which='minor',color='gray',linestyle='dotted')
    #   plt.yscale('log')
      width = 0.2
      throuput_graph.set_xlabel('Error Rate[%]')
      throuput_graph.set_ylabel('Throuput[kbps]')

      for num, (comm_way, delay_way) in enumerate(zip(['SPI', 'i2c', 'uart'], ['continuousnodelay', '', ''])):
#       for num, (comm_way, delay_way) in enumerate(zip(['SPI', 'i2c'], ['continuousnodelay', ''])):
        # 通信速度を設定
        if comm_way == 'SPI':
          speed_hz = 801000
        elif comm_way == 'i2c':
          speed_hz = 78000
        elif comm_way == 'uart':
          speed_hz = 1059322

        throuput_array = []
        error_rate_list = [0]
        for error_rate in error_rate_list:
          # スループットのデータを取得
          try:
            analyzed_data_dir = 'analyzed_data/' + comm_way.upper() + '/'
            folder_dir = delay_way + comm_way.upper() + '_throuput_' + ack_way + '(' + shift_way + ')/'
            throuput_file = delay_way + comm_way.upper() + '_throuput_' + ack_way + '(' + shift_way + ').txt'
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
#             print('fetch {} : {} : {} / {} : {}'.format(comm_way, speed_hz, send_bytes, int(elms[0]), int(elms[1])))
            if speed_hz == int(elms[0]) and send_bytes == int(elms[1]):
              print(float(elms[2]))
              thput_bps = float(elms[2])
              error_rate = float(elms[8])
              val_found = True
              break
          if val_found == False:
            continue
          # グラフ描画用に値を保存
          throuput_array.append((thput_bps * (1-error_rate)) / 1000)

        # グラフを描画
        if num == 0:
          left = np.arange(len(throuput_array))
#         print(len(throuput_array))
        throuput_graph.bar(left[:len(throuput_array)]+width*num, throuput_array, align='center', width=width, label=comm_way.upper())

      # グラフ画像を保存
      plt.xticks(left + width, [str(i) for i in error_rate_list])
      throuput_graph.legend()
      throuput_graph.set_title('When RPi sending ' + str(send_bytes) + ' bytes to Arduino')
      analyzed_data_dir = 'analyzed_data/'
      folder_dir = 'compare_max_throuput(' + shift_way + ')/'
      pdf_folder_path = base_dir + analyzed_data_dir + folder_dir + 'pdf'
      png_folder_path = base_dir + analyzed_data_dir + folder_dir + 'png'
      try:
        os.makedirs(png_folder_path)
        os.makedirs(pdf_folder_path)
      except FileExistsError:
        pass

      fig2.savefig(pdf_folder_path + '/' + str(send_bytes) + 'bytes_compare_throuput(' + shift_way + ').pdf')
      fig2.savefig(png_folder_path + '/' + str(send_bytes) + 'bytes_compare_throuput(' + shift_way + ').png')
      plt.close()

      print(ack_way + ' : Record image of ' + str(send_bytes))
