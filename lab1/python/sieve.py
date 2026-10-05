"""Lab 1 - Sieve of Eratosthenes, Python (CPython) baseline implementation.

Baseline rules: one-byte flags in a bytearray, explicit loops for marking and
counting (no slicing, no NumPy), a fresh array on every call, timing with
time.perf_counter().

Usage: python3 sieve.py [warmup_calls=5] [block=1] [csv_path=../results/raw_python.csv]
"""

import csv
import platform
import sys
import time


def sieve_flags(n):
    """Return a bytearray for 0..n where flags[k] == 1 iff k is prime."""
    flags = bytearray(b"\x01") * (n + 1)  # bulk initialization is allowed
    flags[0] = 0
    flags[1] = 0
    p = 2
    # Outer loop stops at floor(sqrt(n)); p * p <= n avoids floating-point sqrt.
    while p * p <= n:
        if flags[p] == 1:
            # Start at p*p: smaller multiples were marked by smaller primes.
            m = p * p
            while m <= n:
                flags[m] = 0
                m += p
        p += 1
    return flags


def count_primes(n):
    """Number of primes <= n. This is the benchmarked function."""
    flags = sieve_flags(n)
    count = 0  # Python ints are arbitrary precision
    for k in range(n + 1):
        count += flags[k]
    return count


def run_checks():
    """Correctness checks, run before (and outside) any timing."""
    expected = {2: 1, 10: 4, 100: 25, 10**5: 9592, 10**6: 78498, 10**7: 664579}
    ok = True
    for n, want in expected.items():
        got = count_primes(n)
        print(f"check pi({n}) = {got}  {'OK' if got == want else 'FAIL'}")
        ok = ok and got == want
    flags = sieve_flags(30)
    print("primes <= 30:", *[k for k in range(31) if flags[k]])
    return ok


def main():
    warmup = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    block = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    csv_path = sys.argv[3] if len(sys.argv) > 3 else "../results/raw_python.csv"
    runs = 10
    sizes = [10**5, 10**6, 10**7]

    print(f"{platform.python_implementation()} {platform.python_version()}")
    if not run_checks():
        sys.exit("correctness checks failed")

    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["language", "N", "block", "warmup_calls", "run", "elapsed_ms", "prime_count", "batch_size"])
        for n in sizes:
            for _ in range(warmup):  # untimed warm-up
                count_primes(n)
            times, counts = [], []
            for _ in range(runs):
                t0 = time.perf_counter()
                c = count_primes(n)
                t1 = time.perf_counter()
                times.append((t1 - t0) * 1e3)
                counts.append(c)  # result consumed outside the timed interval
            for r, (t, c) in enumerate(zip(times, counts), start=1):
                w.writerow(["Python", n, block, warmup, r, f"{t:.6f}", c, 1])
                print(f"N={n} run {r}: {t:.3f} ms, pi={c}")


if __name__ == "__main__":
    main()
