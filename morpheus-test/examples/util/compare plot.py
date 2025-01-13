from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import sys

filenames = sys.argv[1:]

values = [[] for _ in filenames]

for (index, filename) in enumerate(filenames):
  with open(filename) as f:
    for l in f.read().splitlines():
      values[index].append(float(l))

for (ia, a) in enumerate(values):
  for (ib, b) in enumerate(values[ia+1:]):
    ibr = ib+ia+1
    
    data = pd.DataFrame({
      "a": a,
      "b": b,
    })
    
    print(f"Correlation: {filenames[ia]} <-> {filenames[ibr]} = {data['a'].corr(data['b'])}")

for (index, v) in enumerate(values):
  plt.plot(v, label=filenames[index])
  plt.legend()

plt.savefig("NHC.png")
