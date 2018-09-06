# -*- coding: utf-8 -*-

###########################################################
# それぞれのスループットのデータからbaudrateによる比較を行い、スループットとエラー率をそれぞれ棒グラフと折れ線グラフにまとめる。
# analyze_throuputで生成したテキストを参照するので、事前にanalyze_throuputを実行しておくこと。
###########################################################

import re
import matplotlib.pyplot as plt
from matplotlib import cm
import os

base_dir = '/Users/ashija/Documents/通信方法比較/'

# for ack_way in ['block_ack', 'each_ack']:
for ack_way in ['block_ack']:
  for shift_way in ['FET']:
#     for (num, comm_way), delay_way in zip(enumerate(['i2c']),['']):
    for (num, comm_way), delay_way in zip(enumerate(['SPI', 'i2c', 'uart']),['continuousnodelay', '', '', ]):
#     for (num, comm_way), delay_way in zip(enumerate(['SPI','i2c']),['continuousnodelay','']):

      # グラフ描画領域を作成
      fig1 = plt.figure(figsize=(10, 10))
      fig2 = plt.figure(figsize=(10, 10))
      plt.rcParams["font.size"] = 14
      error_graph = fig1.add_subplot(1,1,1)
      throuput_graph = fig2.add_subplot(1,1,1)
      error_graph.grid(which='major',color='gray',linestyle='--')
      error_graph.grid(which='minor',color='gray',linestyle='dotted')
      throuput_graph.grid(which='major',color='gray',linestyle='--')
  #         throuput_graph.grid(which='minor',color='gray',linestyle='dotted')
    #   plt.yscale('log')
      width = 0.2
      throuput_graph.set_xlabel('Baudrate[kbaud(kHz)]')
      throuput_graph.set_ylabel('Throuput[kbps]')
      error_graph.set_xlabel('Baudrate[kbaud(kHz)]')
      error_graph.set_ylabel('Error Rate[%]')

      send_bytes_array = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]
      for graph_num, send_bytes in enumerate(send_bytes_array):
        throuput_array = []
        error_rate_array = []
        spdhz_array_for_draw = []
        if comm_way == 'i2c':
          speed_hz_arr = range(10000, 78001, 1000)
        elif comm_way == 'SPI':
          speed_hz_arr = range(10000, 5000001, 1000)
        elif comm_way == 'uart':
          speed_hz_arr = range(10000, 1060001, 1000)

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

#         speed_hz_arr = [10000, 14400, 19200, 28800, 38400, 57600, 100000, 115200]
        for speed_hz in speed_hz_arr:
          # スループット平均値と誤り率を得る
          val_found  = False
          for record in records:
            elms = re.split(':|\t', record)
            if speed_hz == int(elms[0]) and send_bytes == int(elms[1]):
              thput_bps = float(elms[2])
              error_rate = float(elms[8])
              val_found = True
          if val_found == False:
            throuput_array.append('#')
            error_rate_array.append('#')
            spdhz_array_for_draw.append('#')
            continue
          # グラフ描画用に値を保存
          throuput_array.append((thput_bps * (1-error_rate)) / 1000)
          error_rate_array.append(error_rate*100)
          spdhz_array_for_draw.append(speed_hz)

        # グラフを描画
        throuput_arr_draw = []
        error_rate_arr_draw = []
        spdhz_arr_draw = []
        is_labeled = False
        is_continuous =True
        print('start plot {} : {}'.format(comm_way, send_bytes))
        for throuput, error_rate, spdhz in zip(throuput_array, error_rate_array, spdhz_array_for_draw):
          if throuput != '#':
            throuput_arr_draw.append(throuput)
            error_rate_arr_draw.append(error_rate)
            spdhz_arr_draw.append(spdhz)
          else:
            print('kugiri')
            if len(throuput_arr_draw) > 0:
              if is_labeled == False:
                error_graph.plot([i/1000 for i in spdhz_arr_draw], error_rate_arr_draw, linewidth = 2, color=cm.tab10(float(graph_num)/len(send_bytes_array)), label=str(send_bytes))
                throuput_graph.plot([i/1000 for i in spdhz_arr_draw], throuput_arr_draw, linewidth = 2, color=cm.tab10(float(graph_num)/len(send_bytes_array)), label=str(send_bytes))
                is_labeled = True
              else:
                error_graph.plot([i/1000 for i in spdhz_arr_draw], error_rate_arr_draw, linewidth = 2, color=cm.tab10(float(graph_num)/len(send_bytes_array)))
                throuput_graph.plot([i/1000 for i in spdhz_arr_draw], throuput_arr_draw, linewidth = 2, color=cm.tab10(float(graph_num)/len(send_bytes_array)))
#               if is_labeled == False:
#                 error_graph.plot(spdhz_arr_draw, error_rate_arr_draw, linewidth = 2, color='blue', label='send_bytes=' + str(send_bytes) + '[byte]')
#                 throuput_graph.plot(spdhz_arr_draw, throuput_arr_draw, linewidth = 2, color='blue', label='send_bytes=' + str(send_bytes) + '[byte]')
#                 is_labeled = True
#               else:
#                 error_graph.plot(spdhz_arr_draw, error_rate_arr_draw, linewidth = 2, color='blue')
#                 throuput_graph.plot(spdhz_arr_draw, throuput_arr_draw, linewidth = 2, color='blue')
            is_continuous = False
            throuput_arr_draw = []
            error_rate_arr_draw = []
            spdhz_arr_draw = []
        if is_continuous == True:
          error_graph.plot([i/1000 for i in spdhz_arr_draw], error_rate_arr_draw, linewidth = 2, color=cm.tab10(float(graph_num)/len(send_bytes_array)), label=str(send_bytes))
          throuput_graph.plot([i/1000 for i in spdhz_arr_draw], throuput_arr_draw, linewidth = 2, color=cm.tab10(float(graph_num)/len(send_bytes_array)), label=str(send_bytes))
#           error_graph.plot(spdhz_arr_draw, error_rate_arr_draw, linewidth = 2, color='blue', label='send_bytes=' + str(send_bytes) + '[byte]')
#           throuput_graph.plot(spdhz_arr_draw, throuput_arr_draw, linewidth = 2, color='blue', label='send_bytes=' + str(send_bytes) + '[byte]')
        print('stop plot {} : {}'.format(comm_way, send_bytes))

      # グラフ画像を保存
      error_graph.legend(title='Send Data[byte]')
      throuput_graph.legend(title='Send Data[byte]')
      throuput_graph.set_xlim(xmin=0)
      error_graph.set_ylim(ymin = 0, ymax = 100)
      error_graph.set_xlim(xmin=0)
      throuput_graph.set_title('Compare Throuput(' + comm_way.upper() + ')')
      error_graph.set_title('Compare Error Rate(' + comm_way.upper() + ')')
      analyzed_data_dir = 'analyzed_data/'
      folder_dir = comm_way.upper() + '/' + delay_way + comm_way.upper() + '_throuput_' + ack_way + '(' + shift_way + ')/'
      pdf_path = base_dir + analyzed_data_dir + folder_dir + 'pdf'
      png_path = base_dir + analyzed_data_dir + folder_dir + 'png'
      try:
        os.mkdir(pdf_path)
        os.mkdir(png_path)
      except FileExistsError:
        pass
      fig1.savefig(pdf_path + '/' + 'compare_error_rate_by_baud_and_bytes(' + shift_way + ').pdf')
      fig1.savefig(png_path + '/' + 'compare_error_rate_by_baud_and_bytes(' + shift_way + ').png')
      fig2.savefig(pdf_path + '/' + 'compare_throuput_by_baud_and_bytes(' + shift_way + ').pdf')
      fig2.savefig(png_path + '/' + 'compare_throuput_by_buad_and_bytes(' + shift_way + ').png')
      plt.close()

      print(ack_way + ' : Record image of ' + str(send_bytes))
