# -*- coding: utf-8 -*-

###########################################################
# SPIのblock_ackに関して、error_rateの折れ線グラフとthrouputの棒グラフを出力する。
# 誤り率とスループットを通信速度や遅延ごとにまとめてテキストに出力する。
###########################################################

import re
import numpy as np
import matplotlib.pyplot as plt
import os

base_dir = '/Users/ashija/Documents/通信方法比較/'

comm_way = 'SPI'
for shift_way in ['FET']:
  # 記録ファイルの生成
  try:
    analyzed_data_dir = 'analyzed_data/' + comm_way.upper() + '/'
    folder_dir = comm_way.upper() + '_throuput_delay_or_not(' + shift_way + ')/'
    record_file_path = comm_way.upper() + '_throuput_delay_or_not(' + shift_way + ').txt'
    record_file_path = base_dir + analyzed_data_dir + folder_dir + record_file_path
    with open(record_file_path, mode = 'w', encoding = 'utf-8') as fh:
      # ファイルに項目名を追加
      fh.write('speed_hz[hz]\tthrouput[bps]\terror_rate\n')
  except IOError:
    print('Cannot find directory : ' + base_dir + analyzed_data_dir + folder_dir[:-1])
    continue

  # グラフ描画領域を作成
  fig1 = plt.figure()
  fig2 = plt.figure(figsize=(10, 5))
  plt.rcParams["font.size"] = 14
  error_graph = fig1.add_subplot(1,1,1)
  throuput_graph = fig2.add_subplot(1,1,1)
  error_graph.grid(which='major',color='gray',linestyle='--')
  error_graph.grid(which='minor',color='gray',linestyle='dotted')
  throuput_graph.grid(which='major',color='gray',linestyle='--')
  throuput_graph.grid(which='minor',color='gray',linestyle='dotted')
#   plt.yscale('log')
  width = 0.3
  throuput_graph.set_xlabel('baudrate[kbaud(kHz)]')
  throuput_graph.set_ylabel('throuput[kbps]')
  error_graph.set_xlabel('baudrate[kbaud(kHz)]')
  error_graph.set_ylabel('error rate[%]')

  delay_way_arr = ['', 'delay', 'nodelay']
  for num, delay_way in enumerate(delay_way_arr):
    throuput_array = []
    error_rate_array = []
#     speed_hz_arr = [10000, 14400, 19200, 28800, 38400, 57600, 100000, 115200]
    speed_hz_arr = [38400, 57600, 100000, 115200, 250000, 500000, 750000, 801282]
    for speed_hz in speed_hz_arr:
      send_bytes = 4096

      # ディレイの平均時間を取得する
      try:
        delay_dir = comm_way.upper() + '_2delay(' + shift_way + ')/'
        delay_file = comm_way.upper() + '_2delay(' + shift_way + ').txt'
        delay_file_path = base_dir + analyzed_data_dir + delay_dir + delay_file
        with open(delay_file_path, mode = 'r', encoding = 'utf-8') as fh:
          delays = fh.readlines()
          delays.pop(0)
          for i in delays:
            i = i.split('\t')
            if int(i[0]) == speed_hz:
              delay_sec = float(i[2]) / 1000
              break
      except IOError:
        print(delay_file_path + ' cannot be opened.')
        continue

      # データファイルのレコードを配列として読み取る
      try:
        fetch_data_dir = 'fetched_data/' + comm_way.upper() + '/'
        folder_dir = delay_way + comm_way.upper() + '_throuput_block_ack(' + shift_way + ')/'
        if delay_way == 'delay':
          delay_elm = '0_'
        else:
          delay_elm = ''
        raw_data_file = str(speed_hz) + 'Hz_' + str(send_bytes) + 'bytes_' + delay_elm + comm_way + '_throuput.txt'
        raw_data_file_path = base_dir + fetch_data_dir + folder_dir + raw_data_file
        with open(raw_data_file_path, mode = 'r', encoding = 'utf-8') as fh:
          records = fh.readlines()
      except IOError:
        print(raw_data_file_path + ' cannot be opened.')
        throuput_array.append(0)
        continue

      # exectimeとerrorを取り出す
      exectime_arr = []
      err_arr = []
      for record in records:
        elms = re.split(':|\t', record)
        exectime_arr.append(float(elms[1]))
        err_arr.append(int(elms[2]))

      # throuputと誤り率を計算する
      # exectimeから2Dを引く
      exectime_arr = [i - delay_sec for i in exectime_arr]
      throuput_arr = [send_bytes*8/i for i in exectime_arr]
      avr_throuput = np.mean(throuput_arr)
      error_rate = np.mean(err_arr)

      # グラフ描画用に値を保存
      throuput_array.append((avr_throuput * (1-error_rate)) / 1000)
      error_rate_array.append(error_rate*100)

      # ファイルに記録
      with open(record_file_path, mode = 'a', encoding = 'utf-8') as fh:
        fh.write('{0}\t{1}\t{2}\t {3}\t{4}\n'.format(speed_hz, send_bytes, delay_way, avr_throuput, error_rate))
      print('{0} : Recorded {1}\t{2}\t{3}\t{4}\t{5}'.format(record_file_path, speed_hz, send_bytes, delay_way, avr_throuput, error_rate))

    # グラフを描画
    if delay_way == '':
      label = '.append(0)'
    elif delay_way == 'delay':
      label = 'time.sleep(0)'
    elif delay_way == 'nodelay':
      label = 'spi.xfer2([0])'
    error_graph.plot([i/1000 for i in speed_hz_arr][:len(error_rate_array)], error_rate_array, '-D', linewidth = 4, label=label)
    if num == 0:
      left = np.arange(len(throuput_array))
    print(len(throuput_array))
    throuput_graph.bar(left[:len(throuput_array)]+width*num, throuput_array, align='center', width=width, label=label)

  # グラフ画像を保存
  plt.xticks(left + width, [str(i) for i in [j/1000 for j in speed_hz_arr]])
  error_graph.legend()
  throuput_graph.legend()
  error_graph.set_title('Compare Error Rate')
  throuput_graph.set_title('Compare Throuput')
  analyzed_data_dir = 'analyzed_data/' + comm_way.upper() + '/'
  folder_dir = comm_way.upper() + '_throuput_delay_or_not(' + shift_way + ')/'
  pdf_path = base_dir + analyzed_data_dir + folder_dir + 'pdf'
  png_path = base_dir + analyzed_data_dir + folder_dir + 'png'
  try:
    os.mkdir(pdf_path)
    os.mkdir(png_path)
  except FileExistsError:
    pass
  fig1.savefig(pdf_path + '/' + comm_way.upper() + '_compare_error_rate(' + shift_way + ').pdf')
  fig1.savefig(png_path + '/' + comm_way.upper() + '_compare_error_rate(' + shift_way + ').png')
  fig2.savefig(pdf_path + '/' + comm_way.upper() + '_compare_throuput(' + shift_way + ').pdf')
  fig2.savefig(png_path + '/' + comm_way.upper() + '_compare_throuput(' + shift_way + ').png')

  plt.close()
