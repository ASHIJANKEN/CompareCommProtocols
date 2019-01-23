# -*- coding: utf-8 -*-

###########################################################
# それぞれのスループットのデータから、send_bytes毎の最大baudrate探し出し、折れ線グラフにまとめる。
# analyze_throuputで生成したテキストを参照するので、事前にanalyze_throuputを実行しておくこと。
###########################################################

import re
import matplotlib.pyplot as plt
import os

base_dir = '/Users/ashija/Documents/通信方法比較/'

# for ack_way in ['block_ack', 'each_ack']:
for ack_way in ['block_ack']:
  for shift_way in ['FET']:
    for (num, comm_way), delay_way in zip(enumerate(['SPI', 'i2c', 'uart']),['continuousnodelay', '', '', ]):
#     for (num, comm_way), delay_way in zip(enumerate(['SPI']),['continuousnodelay']):
      # グラフ描画領域を作成
      fig1 = plt.figure(figsize=(10, 10))
      plt.rcParams["font.size"] = 14
      maxbaud_graph = fig1.add_subplot(1,1,1)
      maxbaud_graph.grid(which='major',color='gray',linestyle='--')
      maxbaud_graph.grid(which='minor',color='gray',linestyle='dotted')
    #   plt.yscale('log')
      width = 0.2
      maxbaud_graph.set_xlabel('Send Data[Byte]')
      maxbaud_graph.set_ylabel('Baudrate[kbaud]')

      send_bytes_arr = [2, 4 ,8, 16, 32, 64, 128, 256, 512, 1024]
      max_baud_array = [0] * len(send_bytes_arr)
#       sndbytes_array_for_baud_array = []
      for num, send_bytes in enumerate(send_bytes_arr):

        # スループットのデータを取得
        try:
          analyzed_data_dir = 'analyzed_data/' + comm_way.upper() + '/'
          folder_dir = delay_way + comm_way.upper() + '_throuput_' + ack_way + '(' + shift_way + ')/'
          throuput_file = delay_way + comm_way.upper() + '_throuput_' + ack_way + '(' + shift_way + ').txt'
          throuput_file_path = base_dir + analyzed_data_dir + folder_dir + throuput_file
          with open(throuput_file_path, mode = 'r', encoding = 'utf-8') as fh:
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

        if comm_way == 'i2c':
          speed_hz_arr = range(10000, 78001, 1000)
        elif comm_way == 'SPI':
          speed_hz_arr = range(10000, 5000001, 1000)
        elif comm_way == 'uart':
          speed_hz_arr = range(10000, 3000001, 1000)
#         speed_hz_arr = [10000, 14400, 19200, 28800, 38400, 57600, 100000, 115200]
        for speed_hz in speed_hz_arr:
          # スループット平均値と誤り率を得る
          val_found  = False
          for record in records:
            elms = re.split(':|\t', record)
            if speed_hz == int(elms[0]) and send_bytes == int(elms[1]):
              error_rate = float(elms[8])
              val_found = True
          if val_found == False:
            continue

          # send_bytesにおいて、max_baudが更新できるか確認する
          if error_rate == 0 and max_baud_array[num] < speed_hz:
            max_baud_array[num] = speed_hz

        print(max_baud_array[num])
        print(str(send_bytes) + 'bytes stage completed.')

      # グラフを描画
      maxbaud_graph.plot(send_bytes_arr, [i/1000 for i in max_baud_array], '-D', linewidth = 4, label=str(comm_way.upper()))

      # グラフ画像を保存
      maxbaud_graph.legend()
      maxbaud_graph.set_ylim(ymin = 0)
      maxbaud_graph.set_xlim(xmin=0)
      maxbaud_graph.set_title('Compare Maximum Baudrate(' + comm_way.upper() + ')')
      analyzed_data_dir = 'analyzed_data/'
      folder_dir = comm_way.upper() + '/compare_maxbaudrate_' + ack_way + '(' + shift_way + ')/'
      pdf_path = base_dir + analyzed_data_dir + folder_dir + 'pdf'
      png_path = base_dir + analyzed_data_dir + folder_dir + 'png'
      try:
        os.makedirs(pdf_path)
        os.makedirs(png_path)
      except FileExistsError:
        pass
      plt.savefig(pdf_path + '/' + 'compare_maxbaudrate(' + shift_way + ').pdf')
      plt.savefig(png_path + '/' + 'compare_maxbaudrate(' + shift_way + ').png')

      plt.close()

      print(ack_way + ' : Record image of ' + comm_way + ' ' + str(send_bytes))
