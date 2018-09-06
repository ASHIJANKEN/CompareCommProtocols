# -*- coding: utf-8 -*-

###########################################################
# analyze_delay_fluctuation
# 1byte送受信の生データから、2Dの値を算出してヒストグラムに出力する。
# 1byte送受信時の2Dの平均値、中央値、最頻値、最大値、最小値、誤り率、ゆらぎ、分散、標準偏差を速度ごとにまとめてテキストに出力する。
# i2cの場合、analyzeP_i2cで生成したテキストを参照するので、事前にanalyzeP_i2cを実行しておくこと。
###########################################################

import re
import numpy as np
import matplotlib.pyplot as plt
from statistics import mode, StatisticsError
import os

base_dir = '/Users/ashija/Documents/通信方法比較/'

# for comm_way in ['SPI']:
# for comm_way in ['SPI', 'i2c', 'uart']:
for comm_way in ['i2c']:
#   for shift_way in ['FET', 'TXB', 'MM', 'reg_div']:
  for shift_way in ['reg_div']:
    if (comm_way == 'SPI' or comm_way == 'uart') and shift_way == 'MM':
      continue
    if comm_way == 'i2c' and shift_way == 'TXB':
      continue

    # 記録ファイルの生成
    try:
      analyzed_data_dir = 'analyzed_data/' + comm_way.upper() + '/'
      record_dir = comm_way.upper() + '_2delay(' + shift_way + ')/'
      record_file = comm_way.upper() + '_2delay(' + shift_way + ').txt'
      record_file_path = base_dir + analyzed_data_dir + record_dir + record_file
      with open(record_file_path, mode = 'w', encoding = 'utf-8') as fh:
        # ファイルに項目名を追加
        fh.write('speed_hz[hz]\tsend_bytes[byte]\taverage_2Delay[ms]\tmedian_2Delay[ms]\tmode_2Delay[ms]\tmax_2Delay[ms]\tmin_2Delay[ms]\tfluctuation[ms]\terror_rate\tvariance[ms^2]\tstandard deviation[ms]\n')
    except IOError:
      print('Cannot find directory : ' + base_dir + analyzed_data_dir + record_dir[:-1])
      continue

    if comm_way == 'i2c':
      speed_hz_arr = list(set(list(range(10000, 300001, 1000)) + [10000, 14400, 19200, 28800, 38400, 57600]))
      speed_hz_arr.sort()
    elif comm_way == 'SPI':
      speed_hz_arr = list(set(list(range(10000, 5000001, 1000)) + [10000, 14400, 19200, 28800, 38400, 57600, 60000, 65000, 70000, 75000, 80000, 85000, 90000, 95000, 100000, 105000, 110000, 115200, 120000, 125000, 130000, 250000, 500000, 750000, 781250, 789062, 791015, 791503, 791991, 792968, 796875, 800781, 801269, 801279, 801280, 801281, 801282, 801283, 801284, 801289, 801330, 801391, 801513, 801757, 802734, 804687, 812500, 875000, 1000000, 10000000, 100000000]))
      speed_hz_arr.sort()
    elif comm_way == 'uart':
      speed_hz_arr = list(set(list(range(10000, 8000001, 1000)) + [10000, 14400, 19200, 28800, 38400, 57600, 100000, 115200]))
      speed_hz_arr.sort()
    for speed_hz in speed_hz_arr:
      send_bytes = 10000
      # データファイルのレコードを配列として読み取る
      try:
        fetch_data_dir = 'fetched_data/' + comm_way.upper() + '/'
        one_byte_dir = comm_way.upper() + '_1byte(' + shift_way + ')/'
        one_byte_file = str(speed_hz) + 'Hz_' + str(send_bytes) + 'bytes_' + comm_way + '_1byte.txt'
        one_byte_file_path = base_dir + fetch_data_dir + one_byte_dir + one_byte_file
        with open(one_byte_file_path, mode = 'r', encoding = 'utf-8') as fh:
          records = fh.readlines()
      except IOError:
        print(one_byte_file_path + ' cannot be opened.')
        continue

      # i2cの場合delayからproc_timeを引かなければならないので、そのデータの取得
      if comm_way == 'i2c':
        p_dir = comm_way.upper() + '_P(' + shift_way + ')/'
        p_file = comm_way.upper() + '_P(' + shift_way + ').txt'
        p_file_path = base_dir + analyzed_data_dir + p_dir + p_file
        with open(p_file_path, mode = 'r', encoding = 'utf-8') as fh:
          P_records = fh.readlines()
          # ヘッダーの除去
          P_records.pop(0)
          found = False
          for P_record in P_records:
            P_record = P_record.split('\t')
            if P_record[0] == str(speed_hz):
              proc_time = float(P_record[6]) / 1000000
              found = True
              break
          if found == False:
            print('There is no data for {}[Hz]'.format(speed_hz))
            continue

      # ディレイの配列とエラーの配列を得る
      throuput_arr = []
      err_arr = []
      for record in records:
        elms = re.split(':|\t', record)
        if comm_way =='i2c':
          throuput_arr.append((float(elms[1]) - proc_time) * 1000)
        else:
          throuput_arr.append(float(elms[1]) * 1000)
        err_arr.append(int(elms[2]))

      # いろんな値を計算する
      avr_delay = np.mean(throuput_arr)
      median_delay = np.median(throuput_arr)
      try:
        mode_delay = mode(throuput_arr)
      except StatisticsError:
        mode_delay = -1
        print('------------------------- StatisticsError occured! -------------------------')
      max_delay = max(throuput_arr)
      min_delay = min(throuput_arr)
      error_rate = np.mean(err_arr)
      fluctuation = max(throuput_arr) - avr_delay
      variance = np.var(throuput_arr)
      std = np.std(throuput_arr)

      # ファイルに記録
      with open(record_file_path, mode = 'a', encoding = 'utf-8') as fh:
        fh.write('{0}\t{1}\t{2}\t {3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t{10}\n'.format(speed_hz, send_bytes, avr_delay, median_delay, mode_delay, max_delay, min_delay, fluctuation, error_rate, variance, std))
      print('{0} : Recorded {1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t{10}\t{11}'.format(record_file_path, speed_hz, send_bytes, avr_delay, median_delay, mode_delay, max_delay, min_delay, fluctuation, error_rate, variance, std))

      # ヒストグラムを作成、pngで保存
      fig2 = plt.figure()
      plt.rcParams["font.size"] = 14
      ax = fig2.add_subplot(1,1,1)
      ax.grid(which='major',color='gray',linestyle='--')
      ax.grid(which='minor',color='gray',linestyle='dotted')
      ax.hist(throuput_arr, bins=100, ec='black')
      ax.set_xlim(xmin = 0)
      # x軸の範囲を固定したいなら以下のコメントを外す
      # ax.set_xlim(xmax =  9)
      plt.title(comm_way.upper() + ' ' + str(speed_hz) + 'Hz')
      plt.yscale('log')
      ax.set_xlabel('2Delay[ms]')
      ax.set_ylabel('Freq')
      pdf_folder_path = base_dir + analyzed_data_dir + comm_way.upper() + '_2delay(' + shift_way + ')/pdf'
      png_folder_path = base_dir + analyzed_data_dir + comm_way.upper() + '_2delay(' + shift_way + ')/png'
      try:
        os.mkdir(png_folder_path)
        os.mkdir(pdf_folder_path)
      except FileExistsError:
        pass
      plt.savefig(pdf_folder_path + '/' + str(speed_hz) + 'Hz.pdf')
      plt.savefig(png_folder_path + '/' + str(speed_hz) + 'Hz.png')
      plt.close()

