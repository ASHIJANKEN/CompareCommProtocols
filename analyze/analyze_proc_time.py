# -*- coding: utf-8 -*-

###########################################################
# pの生データから、i2cのproc_timeの分布を通信速度ごとにヒストグラムにまとめて出力する。
# proc_timeの平均値、中央値、最頻値、最大値、最小値もまとめてテキストに出力する。
###########################################################

import numpy as np
import matplotlib.pyplot as plt
from statistics import mode, StatisticsError
import re
import os
import sys
import json


if __name__ == '__main__':

  argvs = sys.argv
  device = argvs[1]
  protocol = argvs[2]
  level_shift = argvs[3]

  #記録用フォルダの生成
  record_dir_path = '../analyzed_data/' + protocol + '/' + device + '/proc_time/' + level_shift + '/'
  os.makedirs(record_dir_path, exist_ok = True)

  # 記録ファイルの生成
  record_file_path = record_dir_path + 'proc_time.txt'
  with open(os.path.abspath(record_file_path), mode = 'w', encoding = 'utf-8') as fh:
    # ファイルに項目名を追加
    fh.write('speed_hz[hz]\tsend_bytes[byte]\taverage_proctime[us]\t median_proctime[us]\tmode_proctime[us]\tmax_proctime[us]\tmin_proctime[us]\n')

  # speed_hzの情報を取り出す
  with open(os.path.abspath('../configuration.json'), mode='r') as f:
    config = json.load(f)
  speed_hz_arr = eval(config['proc_time'][protocol]['speed_hz'])
  speed_hz_arr.sort()
  for speed_hz in speed_hz_arr:
    send_bytes = 10000
    # データファイルのレコードを配列として読み取る
    try:
      fetch_data_dir = '../measured_data/' + protocol + '/' + device + '/proc_time/' + level_shift + '/'
      proc_file = str(speed_hz) + 'Hz_' + str(send_bytes) + 'bytes.txt'
      proc_file_path = fetch_data_dir + proc_file
      with open(os.path.abspath(proc_file_path), mode = 'r', encoding = 'utf-8') as fh:
        records = fh.readlines()
    except IOError:
      print(proc_file_path + ' cannot be opened.')
      continue

    # 配列のサイズはsend_bytesでない場合、有効なデータファイルでないのでスキップ
    if len(records) != send_bytes:
      print(proc_file_path + ' : ' + str(speed_hz) + 'Hz_' + str(send_bytes) + 'bytes experiment data set has not enough data.')
      continue

    # Pの配列を取る
    p_array = []

    for record in records:
      elms = re.split(':|\t', record.strip())
      p_array.append(float(elms[1]) * 1000000)

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
    with open(os.path.abspath(record_file_path), mode = 'a', encoding = 'utf-8') as fh:
      fh.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\n'.format(speed_hz, send_bytes, avr_p, median_p, mode_p, max_p, min_p))
    print('{0} : Recorded {1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}'.format(record_file_path, speed_hz, send_bytes, avr_p, median_p, mode_p, max_p, min_p))

    # ヒストグラムを作成、pngで保存
    fig2 = plt.figure()
    plt.rcParams["font.size"] = 14
    ax = fig2.add_subplot(1,1,1)
    ax.grid(which='major',color='gray',linestyle='--')
    ax.grid(which='minor',color='gray',linestyle='dotted')
    ax.hist(p_array, bins=100, ec='black')
    plt.title(protocol + ' ' + str(speed_hz) + 'Hz proc_time')
    plt.yscale('log')
    ax.set_xlabel('Proc_time [us]')
    ax.set_ylabel('Freq')
    ax.set_xlim(left = 0)
    # x軸の範囲を固定したいなら以下のコメントを外す
    # ax.set_xlim(xmax =  9)

    pdf_folder_path = record_dir_path + 'pdf'
    png_folder_path = record_dir_path + 'png'
    os.makedirs(png_folder_path, exist_ok = True)
    os.makedirs(pdf_folder_path, exist_ok = True)

    plt.savefig(pdf_folder_path + '/' + str(speed_hz) + 'Hz.pdf')
    plt.savefig(png_folder_path + '/' + str(speed_hz) + 'Hz.png')
    plt.close()
