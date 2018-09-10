# -*- coding: utf-8 -*-

###########################################################
# 1byteの生データから、通信速度ごとに、それぞれの通信方法による
# 2Dの値の分布をヒストグラムにまとめて出力する。
# 3つの分布がまとめて一つの画像に出力される。
# i2cの場合、analyzeP_i2cで生成したテキストを参照するので、事前にanalyzeP_i2cを実行しておくこと。
###########################################################

import re
import matplotlib.pyplot as plt
import os

base_dir = '/Users/ashija/Documents/通信方法比較/'

for speed_hz in [14400, 19200, 28800, 38400, 57600, 100000, 115200]:
  send_bytes = 10000
#   for shift_way in ['FET', 'TXB', 'MM', 'reg_div']:
  for shift_way in ['reg_div']:
    all_data_for_hist = {}
    comm_way_arr = ['SPI', 'uart', 'i2c']
    for comm_way in comm_way_arr:
      # データファイルのレコードを配列として読み取る
      try:
        fetch_data_dir = 'fetched_data/' + comm_way.upper() + '/'
        one_byte_dir = comm_way.upper() + '_1byte(' + shift_way + ')/'
        one_byte_file = str(speed_hz) + 'Hz_' + str(send_bytes) + 'bytes_' + comm_way + '_1byte.txt'
        one_byte_file_path = base_dir + fetch_data_dir + one_byte_dir + one_byte_file
        with open(one_byte_file_path, mode = 'r', encoding = 'utf-8') as fh:
          records = fh.readlines()
          if len(records) != send_bytes:
            print(one_byte_file_path + ' has not enough experiment data.')
            continue
      except IOError:
        print(one_byte_file_path + ' cannot be opened.')
        continue

      # i2cの場合delayからproc_timeを引かなければならないので、そのデータの取得
      analyzed_data_dir = 'analyzed_data/'
      if comm_way == 'i2c':
        p_dir = comm_way.upper() + '_P(' + shift_way + ')/'
        P_file_dir = comm_way.upper() + '_P(' + shift_way + ').txt'
        p_file_path = base_dir + analyzed_data_dir + comm_way.upper() + '/' + p_dir + P_file_dir
        with open(p_file_path, mode = 'r', encoding = 'utf-8') as fh:
          P_records = fh.readlines()
          # ヘッダーの除去
          P_records.pop(0)
          for P_record in P_records:
            P_record = P_record.split('\t')
            if P_record[0] == str(speed_hz):
              # 最悪の場合の2Dを考えるため、Pは最小値を用いる。
              proc_time = float(P_record[6]) / 1000000

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

      # ヒストグラムのデータを保存
      all_data_for_hist[comm_way] = throuput_arr

    ###########################################################
    # ヒストグラムを作成、pngで保存
    # 出力方法をoutputで指定
    # output=0 : それぞれのヒストグラムを重ねて出力
    # output=1 : それぞれのグラフを３つの領域に分けて上下に並べて出力
    ###########################################################
    output = 0

    if output == 0:
      # グラフ描画領域を作成
      fig1 = plt.figure()
      plt.rcParams["font.size"] = 14
      compare_graph = fig1.add_subplot(1,1,1)
      compare_graph.grid(which='major',color='gray',linestyle='--')
      compare_graph.grid(which='minor',color='gray',linestyle='dotted')
      compare_graph.set_yscale('log')
      compare_graph.set_xlabel('2Delay[ms]')
      compare_graph.set_ylabel('Freq')

      # x軸の最大値を求める
      max_val = 0
      for comm_way in all_data_for_hist.keys():
        max_val = max(max_val, max(all_data_for_hist[comm_way]))

      # binの幅を指定
      bin_width = max_val/100
      #ヒストグラムを描画
      for comm_way in all_data_for_hist.keys():
        max_val = max(all_data_for_hist[comm_way])
        min_val = min(all_data_for_hist[comm_way])
        compare_graph.hist(all_data_for_hist[comm_way], bins=int((max_val-min_val)/bin_width), ec='black', alpha=0.5, label=comm_way.upper())

      # png出力
      plt.legend()
      plt.xlim(xmin = 0)
      # x軸の範囲を固定したいなら以下のコメントを外す
  #     compare_graph.set_xlim(xmax =  9)
      plt.title('Baudrate : ' + str(speed_hz) + '[baud(Hz)]')
      pdf_folder_path = base_dir + analyzed_data_dir + 'compare_2delay(' + shift_way + ')/pdf'
      png_folder_path = base_dir + analyzed_data_dir + 'compare_2delay(' + shift_way + ')/png'
      try:
        os.mkdir(png_folder_path)
        os.mkdir(pdf_folder_path)
      except FileExistsError:
        pass
      plt.savefig(pdf_folder_path + '/' + str(speed_hz) + 'Hz.pdf')
      plt.savefig(png_folder_path + '/' + str(speed_hz) + 'Hz.png')
      plt.close()



    elif output == 1:
      # x軸の最大値を求める
      max_val = 0
      for comm_way in all_data_for_hist.keys():
        max_val = max(max_val, max(all_data_for_hist[comm_way]))

      # binの幅を指定
      bin_width = max_val/100

      # グラフ描画領域を作成
      fig1 = plt.figure(figsize=(8, 5))
      plt.rcParams["font.size"] = 14

      #ヒストグラムを描画
      graph_num = len(all_data_for_hist)
      for i, comm_way in enumerate(all_data_for_hist.keys()):
        if i == 0:
          compare_graph = fig1.add_subplot(graph_num,1,i+1)
          graph_criteria = compare_graph
        else:
          compare_graph = fig1.add_subplot(graph_num,1,i+1, sharex=graph_criteria)
        compare_graph.grid(which='major',color='gray',linestyle='--')
        compare_graph.grid(which='minor',color='gray',linestyle='dotted')
        compare_graph.set_title(comm_way.upper())
        compare_graph.set_yscale('log')
        compare_graph.set_ylabel('Freq')

        max_val = max(all_data_for_hist[comm_way])
        min_val = min(all_data_for_hist[comm_way])
        compare_graph.hist(all_data_for_hist[comm_way], bins=int((max_val-min_val)/bin_width), ec='black', alpha=0.5, label=comm_way.upper())
        compare_graph.set_xlim(xmin = 0)

      # png出力
      plt.xlabel('2Delay[ms]')
      plt.subplots_adjust(hspace=0.8)
      # x軸の範囲を固定したいなら以下のコメントを外す
  #     compare_graph.set_xlim(xmax =  9)
      pdf_folder_path = base_dir + analyzed_data_dir + 'compare_2delay(' + shift_way + ')/pdf'
      png_folder_path = base_dir + analyzed_data_dir + 'compare_2delay(' + shift_way + ')/png'
      try:
        os.mkdir(png_folder_path)
        os.mkdir(pdf_folder_path)
      except FileExistsError:
        pass
      plt.savefig(pdf_folder_path + '/' + str(speed_hz) + 'Hz(stack_graph).pdf')
      plt.savefig(png_folder_path + '/' + str(speed_hz) + 'Hz(stack_graph).png')
      plt.close()
