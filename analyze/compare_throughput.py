# -*- coding: utf-8 -*-

###########################################################
# それぞれのスループットのデータからbaudrateによる比較を行い、スループットとエラー率をそれぞれ棒グラフと折れ線グラフにまとめる。
# analyze_throuputで生成したテキストを参照するので、事前にanalyze_throuputを実行しておくこと。
###########################################################

import re
import matplotlib.pyplot as plt
from matplotlib import cm
import os
import sys


if __name__ == '__main__':

  argvs = sys.argv
  device = argvs[1]
  protocol = argvs[2]
  level_shift = argvs[3]

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

    # speed_hzの情報を取り出す
    with open(os.path.abspath('../configuration.json'), mode='r') as f:
      config = json.load(f)
    speed_hz_arr = eval(config['delay'][protocol]['speed_hz'])
    speed_hz_arr.sort()

    # スループットのデータを取得
    try:
      analyzed_data_dir = '../analyzed_data/' + protocol + '/' + device + '/Throuput/' + level_shift + '/'
      throuput_file_path = analyzed_data_dir + "throuput.txt"
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
      continue

    for speed_hz in speed_hz_arr:
      # スループット平均値と誤り率を得る
      elms = records.get(speed_hz)
      if elms == None
        throuput_array.append('#')
        error_rate_array.append('#')
        spdhz_array_for_draw.append('#')
        continue

      thput_bps = float(elms[2])
      error_rate = float(elms[8])

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
    print('Protting... {}: {}'.format(protocol, send_bytes))
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
    print('stop plot {} : {}'.format(protocol, send_bytes))

  # グラフ画像を保存
  error_graph.legend(title='Send Data[byte]')
  throuput_graph.legend(title='Send Data[byte]')
  throuput_graph.set_xlim(xmin=0)
  error_graph.set_ylim(ymin = 0, ymax = 100)
  error_graph.set_xlim(xmin=0)
  throuput_graph.set_title('Compare Throuput(' + protocol.upper() + ')')
  error_graph.set_title('Compare Error Rate(' + protocol.upper() + ')')

  pdf_folder_path = analyzed_data_dir + '/pdf'
  png_folder_path = analyzed_data_dir + '/png'
  os.mkdir(png_folder_path, exist_ok = True)
  os.mkdir(pdf_folder_path, exist_ok = True)

  fig1.savefig(pdf_path + '/' + 'compare_error_rate.pdf')
  fig1.savefig(png_path + '/' + 'compare_error_rate.png')
  fig2.savefig(pdf_path + '/' + 'compare_throuput.pdf')
  fig2.savefig(png_path + '/' + 'compare_throuput.png')
  plt.close()

  print(protocol + ': Record image of ' + str(send_bytes))
