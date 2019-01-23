# -*- coding: utf-8 -*-
import random

with open('send_bytes_SPI.txt', mode = 'w', encoding = 'utf-8') as fh:
  for i in range(128):
    fh.write('{}\n'.format(random.randint(0, 255)))
