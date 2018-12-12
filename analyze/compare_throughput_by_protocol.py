# -*- coding: utf-8 -*-

###########################################################
# それぞれのスループットのデータから比較を行い、スループットとエラー率をそれぞれ棒グラフと折れ線グラフにまとめる。
# analyze_throuputで生成したテキストを参照するので、事前にanalyze_throuputを実行しておくこと。
###########################################################

import re
import numpy as np
import matplotlib.pyplot as plt
import os
import sys


if __name__ == '__main__':

  argvs = sys.argv
  device = argvs[1]
  level_shift = argvs[2]


  for send_bytes in [512, 1024, 2048, 4096]:
    # グラフ描画領域を作成
    fig1 = plt.figure(figsize=(10, 10))
    fig2 = plt.figure(figsize=(10, 10))
    plt.rcParams["font.size"] = 14
    error_graph = fig1.add_subplot(1,1,1)
    throuput_graph = fig2.add_subplot(1,1,1)
    error_graph.grid(which='major',color='gray',linestyle='--')
    error_graph.grid(which='minor',color='gray',linestyle='dotted')
    throuput_graph.grid(which='major',color='gray',linestyle='--')
    throuput_graph.grid(which='minor',color='gray',linestyle='dotted')
  #   plt.yscale('log')
    width = 0.2
    throuput_graph.set_xlabel('Baudrate[kbaud(kHz)]')
    throuput_graph.set_ylabel('Throuput[kbps]')
    error_graph.set_xlabel('Baudrate[kbaud(kHz)]')
    error_graph.set_ylabel('Error Rate[%]')

    for num, protocol in enumerate(['SPI', 'I2C', 'UART', 'Bluetooth', 'TCP']):
      throuput_array = []
      error_rate_array = []
      spdhz_array_for_error_rate = []
      speed_hz_arr = [10000, 14400, 19200, 28800, 38400, 57600, 100000, 115200]

      # スループットのデータを取得
      try:
        analyzed_throughput_dir = '../analyzed_data/' + protocol + '/' + device + '/Throuput/' + level_shift + '/'
        throuput_file_path = analyzed_throughput_dir + 'throughput.txt'
        with open(throuput_file_path, mode = 'r', encoding = 'utf-8') as fh:
          all_records = fh.readlines()
          all_records.pop(0)
          records = {}
          for record in all_records:
            elms = re.split(':|\t', record)
            if send_bytes == int(elms[1]):
              records[speed_hz] = elms
      except IOError:
        print(throuput_file_path + ' cannot be opened.')
        throuput_array.append(0)
        continue

      for speed_hz in speed_hz_arr:
        # スループット平均値と誤り率を得る
        elms = records.get(speed_hz)
        if elms == None
          continue

        # グラフ描画用に値を保存
        thput_bps = float(elms[2])
        error_rate = float(elms[8])
        throuput_array.append((thput_bps * (1-error_rate)) / 1000)
        error_rate_array.append(error_rate*100)
        spdhz_array_for_error_rate.append(speed_hz)

      # グラフを描画
      error_graph.plot([i/1000 for i in spdhz_array_for_error_rate], error_rate_array, '-D', linewidth = 4, label=protocol.upper())
      if num == 0:
        left = np.arange(len(throuput_array))
      print(len(throuput_array))
      throuput_graph.bar(left[:len(throuput_array)]+width*num, throuput_array, align='center', width=width, label=protocol.upper())

    # グラフ画像を保存
    plt.xticks(left + width, [str(i) for i in [j/1000 for j in speed_hz_arr]])
    error_graph.legend()
    throuput_graph.legend()
    error_graph.set_xlim(xmin=0)
    throuput_graph.set_title('When RPi sends ' + str(send_bytes) + ' bytes to Arduino')
    error_graph.set_title('When RPi sends ' + str(send_bytes) + ' bytes to Arduino')

    compare_throughput_dir = '../analyzed_data/compare_throughput/' + level_shift + '/'
    pdf_folder_path = compare_throughput_dir + 'pdf'
    png_folder_path = compare_throughput_dir + 'png'
    os.mkdir(pdf_folder_path, exist_ok = True)
    os.mkdir(png_folder_path, exist_ok = True)

    fig1.savefig(pdf_folder_path + '/' + str(send_bytes) + 'bytes_compare_error_rate.pdf')
    fig1.savefig(png_folder_path + '/' + str(send_bytes) + 'bytes_compare_error_rate.png')
    fig2.savefig(pdf_folder_path + '/' + str(send_bytes) + 'bytes_compare_throuput.pdf')
    fig2.savefig(png_folder_path + '/' + str(send_bytes) + 'bytes_compare_throuput.png')
    plt.close()

    print(protocol + ': Record image of ' + str(send_bytes))
