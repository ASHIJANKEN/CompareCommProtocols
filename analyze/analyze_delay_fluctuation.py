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
import sys

if __name__ == '__main__':

  argvs = sys.argv
  device = argvs[1]
  protocol = argvs[2]
  level_shift = argvs[3]

  # 記録ファイルの生成
  record_dir_path = '../analyzed_data/' + protocol + '/' + device + '/Delay/' + level_shift + '/'
  os.mkdirs(record_dir_path, exist_ok = True)

  record_file_path = record_dir_path + 'delay.txt'
  with open(record_file_path, mode = 'w', encoding = 'utf-8') as fh:
    # ファイルに項目名を追加
    fh.write('speed_hz[hz]\tsend_bytes[byte]\taverage_2Delay[ms]\tmedian_2Delay[ms]\tmode_2Delay[ms]\tmax_2Delay[ms]\tmin_2Delay[ms]\tfluctuation[ms]\terror_rate\tvariance[ms^2]\tstandard deviation[ms]\n')

  # speed_hzの情報を取り出す
  with open(os.path.abspath('../configuration.json'), mode='r') as f:
    config = json.load(f)
  speed_hz_arr = eval(config['delay'][protocol]['speed_hz'])
  speed_hz_arr.sort()

  for speed_hz in speed_hz_arr:
    send_bytes = 10000
    # データファイルのレコードを配列として読み取る
    try:
      fetch_data_dir = '../measured_data/' + protocol + '/' + device + '/Delay/' + level_shift + '/'
      delay_file = str(speed_hz) + 'Hz_' + str(send_bytes) + 'bytes.txt'
      delay_file_path = fetch_data_dir + delay_file
      with open(delay_file_path, mode = 'r', encoding = 'utf-8') as fh:
        records = fh.readlines()
    except IOError:
      print(delay_file_path + ' cannot be opened.')
      continue

    # delayからproc_timeを引かなければならない場合、そのデータも取得
    if protocol == 'i2c' or (device == 'ESP32-DevKitC' and protocol in ['SPI', 'TCP']):
      p_file_path = '../analyzed_data/' + protocol + '/' + device + '/ProcTime/' + level_shift + '/proc_time.txt'
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
    delay_arr = []
    err_arr = []
    for record in records:
      elms = re.split(':|\t', record)
      if protocol =='i2c' or (device == 'ESP32-DevKitC' and protocol in ['SPI', 'TCP']):
        delay_arr.append((float(elms[1]) - proc_time) * 1000)
      else:
        delay_arr.append(float(elms[1]) * 1000)
      err_arr.append(int(elms[2]))

    # いろんな値を計算する
    avr_delay = np.mean(delay_arr)
    median_delay = np.median(delay_arr)
    try:
      mode_delay = mode(delay_arr)
    except StatisticsError:
      mode_delay = -1
      print('---------- StatisticsError occured! ----------')
    max_delay = max(delay_arr)
    min_delay = min(delay_arr)
    error_rate = np.mean(err_arr)
    fluctuation = max(delay_arr) - avr_delay
    variance = np.var(delay_arr)
    std = np.std(delay_arr)

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
    ax.hist(delay_arr, bins=100, ec='black')
    ax.set_xlim(xmin = 0)
    # x軸の範囲を固定したいなら以下のコメントを外す
    # ax.set_xlim(xmax =  9)
    plt.title(protocol.upper() + ' ' + str(speed_hz) + 'Hz')
    plt.yscale('log')
    ax.set_xlabel('2Delay[ms]')
    ax.set_ylabel('Freq')

    pdf_folder_path = record_dir_path + '/pdf'
    png_folder_path = record_dir_path + '/png'
    os.mkdir(png_folder_path, exist_ok = True)
    os.mkdir(pdf_folder_path, exist_ok = True)

    plt.savefig(pdf_folder_path + '/' + str(speed_hz) + 'Hz.pdf')
    plt.savefig(png_folder_path + '/' + str(speed_hz) + 'Hz.png')
    plt.close()

