# -*- coding: utf-8 -*-

import sys
import subprocess

#####################################################
# settings
#####################################################

one_byte = {'base_dir_FET':'I2C_1byte(FET)/',
             'base_dir_MM':'I2C_1byte(MM)/',
             'base_dir_reg_div':'I2C_1byte(reg_div)/',
             'speed_hz': [10000, 14400, 19200, 28800, 38400, 57600, 100000, 115200, 230400, 250000, 1000000, 2000000, 3000000, 4000000, 5000000],
             'file_name': 'i2c_1byte.py',
             }

throuput_block_ack = {'base_dir_FET':'I2C_throuput_block_ack(FET)/',
             'base_dir_MM':'I2C_throuput_block_ack(MM)/',
             'base_dir_reg_div':'I2C_throuput_block_ack(reg_div)/',
             'speed_hz': [10000, 14400, 19200, 28800, 38400, 57600, 100000, 115200, 1000000, 10000000, 100000000],
             'file_name': 'i2c_throuput_block_ack.py',
             }

throuput_each_ack = {'base_dir_FET':'I2C_throuput_each_ack(FET)/',
             'base_dir_MM':'I2C_throuput_each_ack(MM)/',
             'base_dir_reg_div':'I2C_throuput_each_ack(reg_div)/',
             'speed_hz': [10000, 14400, 19200, 28800, 38400, 57600, 100000, 115200, 1000000, 10000000, 100000000],
             'file_name': 'i2c_throuput_each_ack.py',
             }

proc_time = {'base_dir_FET':'I2C_proc_time(FET)/',
             'base_dir_MM':'I2C_proc_time(MM)/',
             'base_dir_reg_div':'I2C_proc_time(reg_div)/',
             'speed_hz': [10000, 14400, 19200, 28800, 38400, 57600, 100000, 115200, 230400, 250000, 1000000, 2000000, 3000000, 4000000, 5000000],
             'file_name': 'i2c_measure_proc_time.py',
             }

if __name__ == '__main__':
    try:
        run_settings = None
        # どのスクリプトを呼び出すか決定
        while True:
            print('Please set select script to run.')
            print('1...1_byte  2...proc_time 3...throuput_block_ack  4...throuput_each_ack')
            cmd = input('> ')
            cmd = cmd.split(' ')
            if cmd[0] == '1':
                run_settings = one_byte
                break
            elif cmd[0] == '2':
                run_settings = proc_time
                break
            elif cmd[0] == '3':
                run_settings = throuput_block_ack
                break
            elif cmd[0] == '4':
                run_settings = throuput_each_ack
                break
            else:
                print('Oops! Wrong command.')

        # 結果の保存場所の指定
        while True:
            # proc_timeの時は保存場所の指定をスキップ
            if run_settings == proc_time:
                break

            print('Please set select level_shift_way.')
            print('level_shift_way: 1...FET  2...MM  3...reg_div')
            cmd = input('> ')
            cmd = cmd.split(' ')
            if cmd[0] == '1':
                base_dir = run_settings['base_dir_FET']
                break
            elif cmd[0] == '2':
                base_dir = run_settings['base_dir_MM']
                break
            elif cmd[0] == '3':
                base_dir = run_settings['base_dir_reg_div']
                break
            else:
                print('Oops! Wrong command.')

        for speed_hz in run_settings['speed_hz']:
            # 速度の変更
            baudrate = 'baudrate=' + str(speed_hz)
            subprocess.call(['sudo', 'modprobe', '-r', 'i2c_bcm2708'])
            subprocess.call(['sudo', 'modprobe', 'i2c_bcm2708', baudrate])

            # Arduinoのスピードをセットさせ、結果の保存場所を指定する。
            while True:
                print("Next speed is {}. Please set wire speed of Arduino and type 'start'.".format(speed_hz))
                print("If you want to skip this speed, please type 'skip'.")
                cmd = input('> ')
                if cmd == 'start':
                    break
                if cmd == 'skip':
                    break
                else:
                    print('Oops! Wrong command.')
            if cmd == 'skip':
                continue

            # 実際の送受信スクリプトを実行
            if run_settings == proc_time:
                subprocess.call(['python', run_settings['file_name'], str(speed_hz)])
            else:
                subprocess.call(['python', run_settings['file_name'], base_dir, str(speed_hz)])

        sys.exit(0)
    except KeyboardInterrupt:
        sys.exit(0)
