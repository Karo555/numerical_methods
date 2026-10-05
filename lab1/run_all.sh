#!/usr/bin/env bash
# Builds every implementation and runs the benchmarks one at a time.
# Usage: ./run_all.sh [warmup_calls=5] [block=1]
# Raw CSVs go to results/raw_<lang>.csv (block > 1 writes raw_<lang>_block<k>.csv).
set -euo pipefail
cd "$(dirname "$0")"
W=${1:-5}
B=${2:-1}
suffix=$([ "$B" = 1 ] && echo "" || echo "_block$B")
R="$PWD/results"

{
  echo "date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "cpu: $(sysctl -n machdep.cpu.brand_string)"
  echo "ram_bytes: $(sysctl -n hw.memsize)"
  echo "os: $(sw_vers -productName) $(sw_vers -productVersion) ($(sw_vers -buildVersion)), $(uname -m)"
  echo "power: $(pmset -g batt | head -1)"
  echo "c++: $(clang++ --version | head -1)"
  echo "python: $(python3 -c 'import platform; print(platform.python_implementation(), platform.python_version())')"
  echo "julia: $(julia --version)"
  echo "java: $(java -version 2>&1 | head -1)"
  echo "rust: $(rustc --version)"
  echo "warmup_calls: $W, block: $B"
} > "$R/environment$suffix.txt"

echo "== build"
clang++ -O3 -std=c++17 cpp/sieve.cpp -o cpp/sieve_cpp
javac -d java java/Sieve.java
(cd rust && cargo build --release -q)

echo "== C++";    (cd cpp    && ./sieve_cpp "$W" "$B" "$R/raw_cpp$suffix.csv")
echo "== Python"; (cd python && python3 sieve.py "$W" "$B" "$R/raw_python$suffix.csv")
echo "== Julia";  (cd julia  && julia sieve.jl "$W" "$B" "$R/raw_julia$suffix.csv")
echo "== Java";   (cd java   && java -cp . Sieve "$W" "$B" "$R/raw_java$suffix.csv")
echo "== Rust";   (cd rust   && ./target/release/sieve_rust "$W" "$B" "$R/raw_rust$suffix.csv")
