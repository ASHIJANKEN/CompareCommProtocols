# -*- coding: utf-8 -*-

###########################################################
# block_ack送受信の生データから、スループットとエラー率をそれぞれ棒グラフと折れ線グラフにまとめる。
# block_ack送受信時のスループットの平均値、中央値、最頻値、最大値、最小値、誤り率、ゆらぎ、分散、標準偏差を速度と送信byte数ごとにまとめてテキストに出力する。
# analyzeDFで生成したテキストを参照するので、事前にanalyzeDFを実行しておくこと。
###########################################################

import re
import numpy as np
import matplotlib.pyplot as plt
from statistics import mode, StatisticsError
import os

base_dir = '/Users/ashija/Documents/通信方法比較/'

# for comm_way, delay_way in zip(['SPI', 'SPI', 'SPI', 'SPI', 'i2c', 'uart'],['', 'continuousnodelay', 'delay', 'nodelay', '', '', ]):
# for comm_way, delay_way in zip(['SPI', 'i2c', 'uart'],['continuousnodelay', '', '', ]):
for comm_way, delay_way in zip(['SPI'],['continuousnodelay']):
# for comm_way, delay_way in zip(['uart'],['']):
#   if comm_way == 'SPI' and delay_way != '':
#     ack_way_arr = ['block_ack']
#   else:
#     ack_way_arr = ['block_ack', 'each_ack']
  ack_way_arr = ['block_ack']
#   ack_way_arr = ['block_ack', 'each_ack']
  for ack_way in ack_way_arr:
#     for shift_way in ['FET', 'TXB', 'MM', 'reg_div']:
    for shift_way in ['FET']:
      if (comm_way in ['SPI', 'uart']) and shift_way == 'MM':
        continue
      if comm_way in ['i2c'] and shift_way == 'TXB':
        continue

      # 記録ファイルの生成
      try:
        analyzed_data_dir = 'analyzed_data/' + comm_way.upper() + '/'
        throuput_dir = delay_way + comm_way.upper() + '_throuput_' + ack_way + '(' + shift_way + ')/'
        record_file = delay_way + comm_way.upper() + '_throuput_' + ack_way + '(' + shift_way + ').txt'
        record_file_path = base_dir + analyzed_data_dir + throuput_dir + record_file
        with open(record_file_path, mode = 'w', encoding = 'utf-8') as fh:
          # ファイルに項目名を追加
          fh.write('speed_hz[hz]\tsend_bytes[byte]\taverage_Throuput[bps]\tmedian_Throuput[bps]\tmode_Throuput[bps]\tmax_Throuput[bps]\tmin_Throuput[bps]\tfluctuation[bps]\terror_rate\tvariance[bps^2]\tstandard deviation[bps]\n')
      except IOError:
        print('Cannot find directory : ' + base_dir + analyzed_data_dir + throuput_dir[:-1])
        continue

      # グラフ描画領域を作成
      fig1 = plt.figure(figsize=(10, 10))
      fig2 = plt.figure(figsize=(12, 10))
      plt.rcParams["font.size"] = 10
      error_graph = fig1.add_subplot(1,1,1)
      throuput_graph = fig2.add_subplot(1,1,1)
      error_graph.grid(which='major',color='gray',linestyle='--')
      error_graph.grid(which='minor',color='gray',linestyle='dotted')
      throuput_graph.grid(which='major',color='gray',linestyle='--')
#       throuput_graph.grid(which='minor',color='gray',linestyle='dotted')
    #   plt.yscale('log')
      width = 0.2
      throuput_graph.set_xlabel('Baudrate[baud(Hz)]')
      throuput_graph.set_ylabel('Throuput[kbps]')
      error_graph.set_xlabel('Baudrate[baud(Hz)]')
      error_graph.set_ylabel('Error Rate[%]')

#       for num, send_bytes in enumerate([1024]):
      for num, send_bytes in enumerate([2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]):
        throuput_array = []
        error_rate_array = []
        spdhz_array_for_error_rate = []
#         if comm_way == 'i2c':
#           speed_hz_arr = list(set(list(range(10000, 78001, 1000)) + [10000, 14400, 19200, 25237, 25256, 25265, 25270, 25271, 25275, 25312, 25331, 25335, 25340, 28800, 38400, 57600]))
#           speed_hz_arr.sort()
#         elif comm_way == 'SPI' and delay_way == 'nodelay' and ack_way == 'block_ack':
#           speed_hz_arr = [38400, 57600, 100000, 115200, 250000, 500000, 750000, 801282, 801283]
#         elif comm_way == 'SPI' and delay_way == 'delay' and ack_way == 'block_ack':
#           speed_hz_arr = [10000, 14400, 19200, 28800, 38400, 57600, 100000, 115200, 250000, 500000, 750000, 801282, 801283]
#         elif comm_way == 'SPI' and ack_way == 'each_ack':
#           speed_hz_arr = [10000, 14400, 19200, 28800, 38400, 57600, 60000, 65000, 70000, 75000, 80000, 85000, 90000, 95000, 100000, 105000, 110000, 115200, 120000, 125000, 130000]
#         elif comm_way == 'SPI':
#           speed_hz_arr = [10000, 14400, 19200, 28800, 38400, 57600, 100000, 115200, 250000, 500000, 750000, 801282, 801283, 1000000]
#           speed_hz_arr = list(set(list(range(10000, 5000001, 1000)) + [10000, 14400, 19200, 28800, 38400, 57600, 100000, 115200, 250000, 500000, 750000, 801282, 801283, 1000000]))
#           speed_hz_arr.sort()
#         elif comm_way == 'uart':
#           speed_hz_arr = list(set(list(range(10000, 3000001, 1000)) + [10000, 14400, 19200, 28800, 38400, 57600, 100000, 115200, 230400, 250000, 1000000, 1031250, 1046875, 1054687, 1058593, 1059081, 1059203, 1059264, 1059294, 1059309, 1059317, 1059321,1059322, 1059323, 2000000, 3000000]))
#           speed_hz_arr = [10000, 14400, 19200, 28800, 38400, 57600, 100000, 115200, 230400, 250000, 1000000, 1031250, 1046875, 1054687, 1058593, 1059081, 1059203, 1059264, 1059294, 1059309, 1059317, 1059321,1059322, 1059323, 2000000, 3000000]
#           speed_hz_arr.sort()
        if comm_way == 'i2c':
          speed_hz_arr = list(set(list(range(10000, 300001, 1000)) + [10000, 14400, 19200, 28800, 38400, 57600]))
          speed_hz_arr.sort()
        elif comm_way == 'SPI':
          speed_hz_arr = list(set(list(range(10000, 5000001, 1000)) + [10000, 14400, 19200, 28800, 38400, 57600, 100000, 115200]))
          speed_hz_arr.sort()
        elif comm_way == 'uart':
          speed_hz_arr = list(set(list(range(10000, 8000001, 1000)) + [10000, 14400, 19200, 28800, 38400, 57600, 100000, 115200]))
          speed_hz_arr.sort()
#           speed_hz_arr = range(250000, 300001, 1000)


        for speed_hz in speed_hz_arr:

          # 2Dの最小値を取得
          try:
            delay_dir = comm_way.upper() + '_2delay(' + shift_way + ')/'
            delay_file = comm_way.upper() + '_2delay(' + shift_way + ').txt'
            delay_file_path = base_dir + analyzed_data_dir + delay_dir + delay_file
            with open(delay_file_path, mode = 'r', encoding = 'utf-8') as fh:
              delays = fh.readlines()
              delays.pop(0)
              found = False
              for i in delays:
                i = i.split('\t')
                if int(i[0]) == speed_hz:
                  delay_sec = float(i[6]) / 1000
                  found = True
                  break
              if found == False:
                print(delay_file_path + " doesn't have data for {} Hz.".format(speed_hz))
                throuput_array.append(0)
                continue
          except IOError:
            print(delay_file_path + ' cannot be opened.')
            continue

          # スループットの生データを取得
          try:
            fetch_data_dir = 'fetched_data/' + comm_way.upper() + '/'
            folder_dir = delay_way + comm_way.upper() + '_throuput_' + ack_way + '(' + shift_way + ')/'
            if comm_way == 'SPI' and delay_way == 'delay' and ack_way == 'block_ack':
              raw_data_file = str(speed_hz) + 'Hz_' + str(send_bytes) + 'bytes_0_' + comm_way + '_throuput.txt'
            else:
              raw_data_file = str(speed_hz) + 'Hz_' + str(send_bytes) + 'bytes_' + comm_way + '_throuput.txt'
            raw_data_file_path = base_dir + fetch_data_dir + folder_dir + raw_data_file
            with open(raw_data_file_path, mode = 'r', encoding = 'utf-8') as fh:
              print(raw_data_file_path)
              records = fh.readlines()
              # recordsが1000なければスキップ(途中で通信が止まった際の実験結果を無視するため)
              if len(records) != 1000:
                print(raw_data_file_path + ' : ' + str(speed_hz) + 'Hz_' + str(send_bytes) + 'bytes experiment data set has not enough data.')
                throuput_array.append(0)
                continue

            # スループットの配列とエラーの配列を得る
            throuput_arr = []
            err_arr = []
            for i, record in enumerate(records):
              elms = re.split(':|\t|\s', record)
#               if i == 500:
#                 print(elms[1])
#                 print(delay_sec)
              exec_time = float(elms[1]) - delay_sec
              try:
                throuput = send_bytes * 8 / exec_time
              except ZeroDivisionError:
                continue
              throuput_arr.append(throuput)
              err_arr.append(int(elms[2]))

            # いろんな値を計算する
            avr_thput = np.mean(throuput_arr)
            median_thput = np.median(throuput_arr)
            try:
              mode_thput = mode(throuput_arr)
            except StatisticsError:
              mode_thput = -1
              print('------------------------- StatisticsError occured! -------------------------')
            max_thput = max(throuput_arr)
            min_thput = min(throuput_arr)
            error_rate = np.mean(err_arr)
            fluctuation = max(throuput_arr) - avr_thput
            variance = np.var(throuput_arr)
            std = np.std(throuput_arr)

            # グラフ描画用に値を保存
            throuput_array.append((avr_thput * (1-error_rate)) / 1000)
            error_rate_array.append(error_rate*100)
            spdhz_array_for_error_rate.append(speed_hz)

            # ファイルに記録
            with open(record_file_path, mode = 'a', encoding = 'utf-8') as fh:
              fh.write('{0}\t{1}\t{2}\t {3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t{10}\n'.format(speed_hz, send_bytes, avr_thput, median_thput, mode_thput, max_thput, min_thput, fluctuation, error_rate, variance, std))
            print('{0} : Recorded {1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t{10}\t{11}'.format(record_file_path, speed_hz, send_bytes, avr_thput, median_thput, mode_thput, max_thput, min_thput, fluctuation, error_rate, variance, std))

          except IOError:
            print(raw_data_file_path + ' cannot be opened.')
            throuput_array.append(0)
            continue

        print("spdhz_array_for_error_rate; {}".format(len(spdhz_array_for_error_rate)))
        print("error_rate_array; {}".format(len(error_rate_array)))
        print("throuput_array; {}".format(len(throuput_array)))
        print("speed_hz_arr; {}".format(len(speed_hz_arr)))


        # グラフを描画
        error_graph.plot(spdhz_array_for_error_rate, error_rate_array, '-D', markersize=4, linewidth = 2, label='send_bytes=' + str(send_bytes) + '[byte]')
        if num == 0:
          left = np.arange(len(throuput_array))
        throuput_graph.bar(left[:len(throuput_array)]+width*num, throuput_array, align='center', width=width, label='send_bytes=' + str(send_bytes) + '[byte]')

      # グラフ画像を保存
      plt.xticks(left + width, [str(i) for i in speed_hz_arr])
      error_graph.legend()
      throuput_graph.legend()
      error_graph.set_ylim(ymin = 0, ymax = 100)
      error_graph.set_xlim(xmin=0)
      analyzed_data_dir = 'analyzed_data/' + comm_way.upper() + '/'
      folder_dir = delay_way + comm_way.upper() + '_throuput_' + ack_way + '(' + shift_way + ')/'
      pdf_path = base_dir + analyzed_data_dir + folder_dir + 'pdf'
      png_path = base_dir + analyzed_data_dir + folder_dir + 'png'
      try:
        os.makedirs(pdf_path)
        os.makedirs(png_path)
      except FileExistsError:
        pass
      fig1.savefig(pdf_path + '/' + delay_way + comm_way.upper() + '_compare_error_rate(' + shift_way + ').pdf')
      fig1.savefig(png_path + '/' + delay_way + comm_way.upper() + '_compare_error_rate(' + shift_way + ').png')
      fig2.savefig(pdf_path + '/' + delay_way + comm_way.upper() + '_compare_throuput(' + shift_way + ').pdf')
      fig2.savefig(png_path + '/' + delay_way + comm_way.upper() + '_compare_throuput(' + shift_way + ').png')
      plt.close()
