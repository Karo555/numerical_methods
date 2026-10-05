"""Lab 1 - combine raw measurements, build the results table and the scaling plot.

Usage: python3 analyze.py [final_block=2]
Reads results/raw_*.csv, writes:
  results/all_measurements.csv  every timed call, with a status column (final / superseded)
  results/summary.csv           median/min/max/slowdown per language and N (final block)
  results/summary.md            the same table in Markdown
  results/scaling.png           median time vs N, error bars = min..max of the final block
"""

import csv
import glob
import statistics
import sys
from collections import defaultdict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

FINAL_BLOCK = int(sys.argv[1]) if len(sys.argv) > 1 else 2
REQUIRED = ["C++", "Python", "Julia"]
ORDER = ["C++", "Python", "Julia", "Java", "Rust"]
# Fixed categorical order (validated for CVD separation); never cycled.
COLORS = {"C++": "#2a78d6", "Python": "#eb6834", "Julia": "#1baf7a", "Java": "#eda100", "Rust": "#e87ba4"}
MARKERS = {"C++": "o", "Python": "s", "Julia": "^", "Java": "D", "Rust": "v"}

rows = []
for path in sorted(glob.glob("results/raw_*.csv")):
    with open(path) as f:
        rows.extend(csv.DictReader(f))
for r in rows:
    r["status"] = "final" if int(r["block"]) == FINAL_BLOCK else "superseded"

fields = ["language", "N", "block", "status", "warmup_calls", "run", "elapsed_ms", "prime_count", "batch_size"]
rows.sort(key=lambda r: (ORDER.index(r["language"]), int(r["block"]), int(r["N"]), int(r["run"])))
with open("results/all_measurements.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows({k: r[k] for k in fields} for r in rows)

# Summaries per block, so block-to-block variability can be reported too.
times = defaultdict(list)
counts = defaultdict(set)
for r in rows:
    key = (int(r["block"]), r["language"], int(r["N"]))
    times[key].append(float(r["elapsed_ms"]))
    counts[key].add(int(r["prime_count"]))

sizes = sorted({k[2] for k in times})
langs = [l for l in ORDER if any(k[1] == l for k in times)]
med = {k: statistics.median(v) for k, v in times.items()}

summary = []
for n in sizes:
    ref = min(med[(FINAL_BLOCK, l, n)] for l in REQUIRED)
    for l in langs:
        k = (FINAL_BLOCK, l, n)
        (pi,) = counts[k]  # all runs must agree on the count
        prev = med.get((1, l, n)) if FINAL_BLOCK != 1 else None
        summary.append({
            "language": l, "N": n, "median_ms": med[k], "min_ms": min(times[k]), "max_ms": max(times[k]),
            "pi_N": pi, "slowdown": med[k] / ref, "block1_median_ms": prev,
        })

with open("results/summary.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(summary[0]))
    w.writeheader()
    w.writerows(summary)

def fmt(x):
    return f"{x:.4g}" if x < 1000 else f"{x:.0f}"

with open("results/summary.md", "w") as f:
    f.write(f"Final block = {FINAL_BLOCK}. Slowdown reference = smallest median among C++, Python, Julia.\n\n")
    f.write("| Language | N | Median (ms) | Min (ms) | Max (ms) | π(N) | Slowdown | Block-1 median (ms) |\n")
    f.write("|---|---:|---:|---:|---:|---:|---:|---:|\n")
    for s in summary:
        b1 = fmt(s["block1_median_ms"]) if s["block1_median_ms"] else "-"
        f.write(f"| {s['language']} | 10^{len(str(s['N'])) - 1} | {fmt(s['median_ms'])} | {fmt(s['min_ms'])} | "
                f"{fmt(s['max_ms'])} | {s['pi_N']:,} | {s['slowdown']:.2f} | {b1} |\n")
print(open("results/summary.md").read())

# Scaling plot: log-log, one line per language, min..max error bars, direct labels.
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(figsize=(7, 4.6), dpi=150)
for l in langs:
    s = [x for x in summary if x["language"] == l]
    xs = [x["N"] for x in s]
    ys = [x["median_ms"] for x in s]
    err = [[y - x["min_ms"] for x, y in zip(s, ys)], [x["max_ms"] - y for x, y in zip(s, ys)]]
    dashed = l not in REQUIRED
    ax.errorbar(xs, ys, yerr=err, color=COLORS[l], marker=MARKERS[l], markersize=6, linewidth=2,
                linestyle="--" if dashed else "-", capsize=3, elinewidth=1,
                label=l + (" (extra credit)" if dashed else ""))
# Direct labels at the right end, nudged apart in log space so they never overlap.
import math
ends = sorted((math.log10(x["median_ms"]), x["language"]) for x in summary if x["N"] == sizes[-1])
placed = []
for y, l in ends:
    y = max(y, placed[-1][0] + 0.2) if placed else y
    placed.append((y, l))
for y, l in placed:
    ax.annotate(l, (sizes[-1] * 1.25, 10 ** y), va="center", color="#333333", annotation_clip=False)
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xticks(sizes, [f"$10^{len(str(n)) - 1}$" for n in sizes])
ax.set_xlim(sizes[0] / 1.6, sizes[-1] * 3)
ax.set_xlabel("N (sieve upper bound)")
ax.set_ylabel("Median time per call (ms)")
ax.set_title(f"Sieve of Eratosthenes: median of 10 timed calls (block {FINAL_BLOCK})", loc="left", fontsize=11)
ax.grid(True, which="major", color="#e5e5e5", linewidth=0.8)
ax.legend(frameon=False, fontsize=9, loc="upper left")
fig.text(0.01, 0.01, "Error bars span min to max of the 10 calls. Apple M1 Pro, macOS 26.6.2.", fontsize=8, color="#666666")
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig("results/scaling.png")
