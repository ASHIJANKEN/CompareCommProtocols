import os

with open(os.path.abspath("throughput.txt"), mode = 'r') as f:
  thput_txt = f.readlines()
  thput_txt.pop(0)

max_throughput = 0

for line in thput_txt:
  elms = line.split()

  if int(elms[1]) != 32:
    continue

  thput = float(elms[3]) * (1 - float(elms[8]))

  if thput > max_throughput:
    max_throughput = thput

print("Maximum throughput(only by correct transactions) is {}[bps]".format(max_throughput))
