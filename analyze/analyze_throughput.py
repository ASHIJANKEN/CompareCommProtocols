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
import sys
import json


if __name__ == '__main__':

  argvs = sys.argv
  device = argvs[1]
  protocol = argvs[2]
  level_shift = argvs[3]

  # 記録ファイルの生成
  record_dir_path = '../analyzed_data/' + protocol + '/' + device + '/throughput/' + level_shift + '/'
  os.makedirs(record_dir_path, exist_ok = True)

  record_file_path = record_dir_path + 'Throughput.txt'
  with open(os.path.abspath(record_file_path), mode = 'w', encoding = 'utf-8') as fh:
    # ファイルに項目名を追加
    fh.write('speed_hz[hz]\tsend_bytes[byte]\taverage_throughput[bps]\tmedian_throughput[bps]\tmode_throughput[bps]\tmax_throughput[bps]\tmin_throughput[bps]\tfluctuation[bps]\terror_rate\tvariance[bps^2]\tstandard deviation[bps]\n')

  # グラフ描画領域を作成
  fig1 = plt.figure(figsize=(10, 10))
  fig2 = plt.figure(figsize=(12, 10))
  plt.rcParams["font.size"] = 10
  error_graph = fig1.add_subplot(1,1,1)
  throughput_graph = fig2.add_subplot(1,1,1)
  error_graph.grid(which='major',color='gray',linestyle='--')
  error_graph.grid(which='minor',color='gray',linestyle='dotted')
  throughput_graph.grid(which='major',color='gray',linestyle='--')
#       throughput_graph.grid(which='minor',color='gray',linestyle='dotted')
#   plt.yscale('log')
  width = 0.2
  throughput_graph.set_xlabel('Baudrate[baud(Hz)]')
  throughput_graph.set_ylabel('throughput[kbps]')
  error_graph.set_xlabel('Baudrate[baud(Hz)]')
  error_graph.set_ylabel('Error Rate[%]')

  # speed_hzの情報を取り出す
  with open(os.path.abspath('../configuration.json'), mode='r') as f:
    config = json.load(f)
  speed_hz_arr = eval(config['throughput'][protocol]['speed_hz'])
  speed_hz_arr.sort()

  for num, send_bytes in enumerate([2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]):
    throughput_array = []
    error_rate_array = []
    spdhz_array_for_error_rate = []

    for speed_hz in speed_hz_arr:

      # 2Dの最小値を取得
      try:
        delay_file_path = '../analyzed_data/' + protocol + '/' + device + '/delay/' + level_shift + '/delay.txt'
        with open(os.path.abspath(delay_file_path), mode = 'r', encoding = 'utf-8') as fh:
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
            throughput_array.append(0)
            continue
      except IOError:
        print(delay_file_path + ' cannot be opened.')
        continue

      # スループットの生データを取得
      try:
        fetch_data_dir = '../measured_data/' + protocol + '/' + device + '/throughput/' + level_shift + '/'
        thput_file = str(speed_hz) + 'Hz_' + str(send_bytes) + 'bytes.txt'
        thput_file_path = fetch_data_dir + thput_file
        with open(os.path.abspath(thput_file_path), mode = 'r', encoding = 'utf-8') as fh:
          records = fh.readlines()

      except IOError:
        print(thput_file_path + ' cannot be opened.')
        throughput_array.append(0)
        continue

      # recordsが1000なければスキップ(途中で通信が止まった際の実験結果を無視するため)
      if len(records) != 1000:
        print(thput_file_path + ' : ' + str(speed_hz) + 'Hz_' + str(send_bytes) + 'bytes experiment data set has not enough data.')
        throughput_array.append(0)
        continue

      # スループットの配列とエラーの配列を得る
      throughput_arr = []
      err_arr = []
      for i, record in enumerate(records):
        elms = re.split(':|\t|\s', record)
        exec_time = float(elms[1]) - delay_sec
        try:
          throughput = send_bytes * 8 / exec_time
        except ZeroDivisionError:
          continue
        throughput_arr.append(throughput)
        err_arr.append(int(elms[2]))

      # いろんな値を計算する
      avr_thput = np.mean(throughput_arr)
      median_thput = np.median(throughput_arr)
      try:
        mode_thput = mode(throughput_arr)
      except StatisticsError:
        mode_thput = -1
        print('------------------------- StatisticsError occured! -------------------------')
      max_thput = max(throughput_arr)
      min_thput = min(throughput_arr)
      error_rate = np.mean(err_arr)
      fluctuation = max(throughput_arr) - avr_thput
      variance = np.var(throughput_arr)
      std = np.std(throughput_arr)

      # グラフ描画用に値を保存
      throughput_array.append((avr_thput * (1-error_rate)) / 1000)
      error_rate_array.append(error_rate*100)
      spdhz_array_for_error_rate.append(speed_hz)

      # ファイルに記録
      with open(os.path.abspath(record_file_path), mode = 'a', encoding = 'utf-8') as fh:
        fh.write('{0}\t{1}\t{2}\t {3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t{10}\n'.format(speed_hz, send_bytes, avr_thput, median_thput, mode_thput, max_thput, min_thput, fluctuation, error_rate, variance, std))
      print('{0} : Recorded {1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t{10}\t{11}'.format(record_file_path, speed_hz, send_bytes, avr_thput, median_thput, mode_thput, max_thput, min_thput, fluctuation, error_rate, variance, std))


    print("spdhz_array_for_error_rate: {}".format(len(spdhz_array_for_error_rate)))
    print("error_rate_array: {}".format(len(error_rate_array)))
    print("throughput_array: {}".format(len(throughput_array)))
    print("speed_hz_arr: {}".format(len(speed_hz_arr)))


    # グラフを描画
    error_graph.plot(spdhz_array_for_error_rate, error_rate_array, '-D', markersize=4, linewidth = 2, label='send_bytes=' + str(send_bytes) + '[byte]')
    if num == 0:
      left = np.arange(len(throughput_array))
    throughput_graph.bar(left[:len(throughput_array)]+width*num, throughput_array, align='center', width=width, label='send_bytes=' + str(send_bytes) + '[byte]')

  # グラフ画像を保存
  plt.xticks(left + width, [str(i) for i in speed_hz_arr])
  error_graph.legend()
  throughput_graph.legend()
  error_graph.set_ylim(ymin = 0, ymax = 100)
  error_graph.set_xlim(xmin=0)

  pdf_folder_path = record_dir_path + 'pdf'
  png_folder_path = record_dir_path + 'png'
  os.makedirs(png_folder_path, exist_ok = True)
  os.makedirs(pdf_folder_path, exist_ok = True)

  fig1.savefig(pdf_folder_path + '/analyze_error_rate.pdf')
  fig1.savefig(png_folder_path + '/analyze_error_rate.png')
  fig2.savefig(pdf_folder_path + '/analyze_throughput.pdf')
  fig2.savefig(png_folder_path + '/analyze_throughput.png')
  plt.close()
