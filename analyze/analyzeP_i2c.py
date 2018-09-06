# -*- coding: utf-8 -*-

###########################################################
# pの生データから、i2cのproc_timeの分布を通信速度ごとにヒストグラムにまとめて出力する。
# proc_timeの平均値、中央値、最頻値、最大値、最小値もまとめてテキストに出力する。
###########################################################

import numpy as np
import matplotlib.pyplot as plt
from statistics import mode, StatisticsError
import os

base_dir = '/Users/ashija/Documents/通信方法比較/'


# for comm_way in ['SPI', 'i2c', 'uart']:
for comm_way in ['i2c']:
#   for shift_way in ['FET', 'TXB', 'MM', 'reg_div']:
  for shift_way in ['reg_div']:
    if (comm_way == 'SPI' or comm_way == 'uart') and shift_way == 'MM':
      continue
    if comm_way == 'i2c' and shift_way == 'TXB':
      continue

    #記録ファイルの生成
    try:
      analyzed_data_dir = 'analyzed_data/' + comm_way.upper() + '/'
      record_dir = comm_way.upper() + '_P(' + shift_way + ')/'
      record_file_path = comm_way.upper() + '_P(' + shift_way + ').txt'
      record_file_path = base_dir + analyzed_data_dir + record_dir + record_file_path
      with open(record_file_path, mode = 'w', encoding = 'utf-8') as fh:
        # ファイルに項目名を追加
        fh.write('speed_hz[hz]\tsend_bytes[byte]\taverage_proctime[us]\t median_proctime[us]\tmode_proctime[us]\tmax_proctime[us]\tmin_proctime[us]\n')
    except IOError:
      print('Cannot find directory : ' + base_dir + analyzed_data_dir + record_dir[:-1])
      continue

    speed_hz_arr = list(set(list(range(10000, 300001, 1000)) + [10000, 14400, 19200, 28800, 38400, 57600]))
    speed_hz_arr.sort()
    for speed_hz in speed_hz_arr:
      send_bytes = 10000
      # データファイルのレコードを配列として読み取る
      try:
        fetch_data_dir = 'fetched_data/' + comm_way.upper() + '/'
        proc_dir = comm_way.upper() + '_proc_time(' + shift_way + ')/'
        raw_data_file = str(speed_hz) + 'Hz_' + str(send_bytes) + 'bytes_' + comm_way + '_measure_proc_time.txt'
        raw_data_file_path = base_dir + fetch_data_dir + proc_dir +raw_data_file
        with open(raw_data_file_path, mode = 'r', encoding = 'utf-8') as fh:
          records = fh.readlines()
      except IOError:
        print(raw_data_file_path + ' cannot be opened.')
        continue

      # 配列のサイズはsend_bytesでない場合、有効なデータファイルでないのでスキップ
      if len(records) != send_bytes:
        print(raw_data_file_path + ' : ' + str(speed_hz) + 'Hz_' + str(send_bytes) + 'bytes experiment data set has not enough data.')
        continue

      # Pの配列を取る
      p_array = []
      for record in records:
        p_array.append(float(record))

      # Pの平均値、中央値、最頻値、最大値、最小値を計算する
      avr_p = np.mean(p_array)
      median_p = np.median(p_array)
      try:
        mode_p = mode(p_array)
      except StatisticsError:
        mode_p = -1
      max_p = max(p_array)
      min_p = min(p_array)


      # ファイルに記録
      with open(record_file_path, mode = 'a', encoding = 'utf-8') as fh:
        fh.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\n'.format(speed_hz, send_bytes, avr_p, median_p, mode_p, max_p, min_p))
      print('{0} : Recorded {1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}'.format(record_file_path, speed_hz, send_bytes, avr_p, median_p, mode_p, max_p, min_p))

      # ヒストグラムを作成、pngで保存
      fig2 = plt.figure()
      plt.rcParams["font.size"] = 14
      ax = fig2.add_subplot(1,1,1)
      ax.grid(which='major',color='gray',linestyle='--')
      ax.grid(which='minor',color='gray',linestyle='dotted')
      ax.hist(p_array, bins=100, ec='black')
      plt.title(comm_way.upper() + ' ' + str(speed_hz) + 'Hz Proc_time')
      plt.yscale('log')
      ax.set_xlabel('Proc_time [us]')
      ax.set_ylabel('Freq')
      ax.set_xlim(left = 0)
#       ax.set_ylim(bottom = 0)
      # x軸の範囲を固定したいなら以下のコメントを外す
      # ax.set_xlim(xmax =  9)
      pdf_folder_path = base_dir + analyzed_data_dir + comm_way.upper() + '_P(' + shift_way + ')/pdf'
      png_folder_path = base_dir + analyzed_data_dir + comm_way.upper() + '_P(' + shift_way + ')/png'
      try:
        os.mkdir(png_folder_path)
        os.mkdir(pdf_folder_path)
      except FileExistsError:
        pass
      plt.savefig(pdf_folder_path + '/' + str(speed_hz) + 'Hz.pdf')
      plt.savefig(png_folder_path + '/' + str(speed_hz) + 'Hz.png')
      plt.close()
