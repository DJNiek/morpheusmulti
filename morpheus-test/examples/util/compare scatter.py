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
    for (ib, b) in enumerate(values[ia + 1:]):
        ibr = ib + ia + 1

        data = pd.DataFrame({
            "a": a,
            "b": b,
        })

        print(
            f"Correlation: {filenames[ia]} <-> {filenames[ibr]} = {data['a'].corr(data['b'])}"
        )

fig, ax = plt.subplots()

for i in range(len(filenames)-1):
    ax.scatter(values[0], values[i+1], label=filenames[i+1])
    b, a = np.polyfit(values[0], values[i+1], deg=1)
    xseq = np.linspace(min(values[0]), max(values[0]), num=100)
    ax.plot(xseq, a+b * xseq, color="k", lw=0.5)
    print(f"Linear regression: {b}x+{a}")

ax.legend()
ax.grid(True)
ax.set_xlabel("Reference")
ax.set_ylabel("Simulated")

plt.savefig("NHC2.png")
