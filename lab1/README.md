# Lab 1: Sieve of Eratosthenes benchmark

This lab implements the same full sieve (one-byte flags, explicit loops, a fresh array on every call)
in C++, Python and Julia, with Java and Rust as extra credit. Results and analysis are in
[REPORT.md](REPORT.md).

## Hardware and software

| | |
|---|---|
| CPU / RAM | Apple M1 Pro, 16 GB |
| OS | macOS 26.6.2 (25G83), arm64. Battery power, Low Power Mode off |
| C++ | Apple clang 21.0.0 (clang-2100.0.123.102), `-O3 -std=c++17` |
| Python | CPython 3.14.2 |
| Julia | 1.13.1, default options (`-O2`) |
| Java | OpenJDK / javac 27 (2026-09-15), default JVM options |
| Rust | rustc 1.99.0, cargo 1.99.0, release profile (`opt-level = 3`) |
| Analysis | matplotlib 3.10.8 |

`run_all.sh` writes these details to `results/environment*.txt` each time it runs.

## Build

Run these from `lab1/`:

```bash
clang++ -O3 -std=c++17 cpp/sieve.cpp -o cpp/sieve_cpp   # g++ on macOS is this same Apple clang
javac -d java java/Sieve.java
(cd rust && cargo build --release)
```

## Run

Every program takes the same three arguments: `warmup_calls block csv_path`. Each one first checks
π(N) against the expected values for N from 2 to 10⁷ and prints the primes ≤ 30. It then measures each
N ∈ {10⁵, 10⁶, 10⁷}: the given number of untimed warm-up calls, followed by 10 timed calls in the
same process. Batch size is 1. These are the exact commands for the reported block (block 2), run
one at a time:

```bash
(cd cpp    && ./sieve_cpp                  20 2 ../results/raw_cpp_block2.csv)
(cd python && python3 sieve.py            20 2 ../results/raw_python_block2.csv)
(cd julia  && julia sieve.jl               20 2 ../results/raw_julia_block2.csv)
(cd java   && java -cp . Sieve             20 2 ../results/raw_java_block2.csv)
(cd rust   && ./target/release/sieve_rust  20 2 ../results/raw_rust_block2.csv)
```

## Reproduce all measurements

```bash
cd lab1
./run_all.sh 5 1       # block 1: 5 warm-up calls  -> results/raw_<lang>.csv        (superseded)
./run_all.sh 20 2      # block 2: 20 warm-up calls -> results/raw_<lang>_block2.csv (final)
python3 analyze.py 2   # -> results/all_measurements.csv, summary.csv, summary.md, scaling.png
pdflatex report.tex    # report PDF (uses results/scaling.png)
```

`run_all.sh` builds everything, records the environment, then runs the five benchmarks one after
another. Before running it, close other heavy applications and keep the power mode the same for
every block.

`results/all_measurements.csv` contains every timed call, with the columns
`language,N,block,status,warmup_calls,run,elapsed_ms,prime_count,batch_size`.
