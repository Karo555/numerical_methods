// Lab 1 - Sieve of Eratosthenes, C++ baseline implementation.
//
// Baseline rules: one-byte flags in std::vector<std::uint8_t>, explicit loops for
// marking and counting, a fresh array on every call, timing with std::chrono::steady_clock.
//
// Usage: sieve_cpp [warmup_calls=5] [block=1] [csv_path=../results/raw_cpp.csv]

#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

// Returns the flag array for 0..n: flags[k] == 1 iff k is prime.
static std::vector<std::uint8_t> sieve_flags(std::int64_t n) {
    std::vector<std::uint8_t> flags(static_cast<std::size_t>(n + 1), 1);  // bulk init allowed
    flags[0] = 0;
    flags[1] = 0;
    // Outer loop stops at floor(sqrt(n)): p * p <= n avoids floating-point sqrt.
    for (std::int64_t p = 2; p * p <= n; ++p) {
        if (flags[p] == 1) {
            // Smaller multiples k*p (k < p) were already marked by a smaller prime.
            for (std::int64_t m = p * p; m <= n; m += p) {
                flags[m] = 0;
            }
        }
    }
    return flags;
}

// Number of primes <= n. This is the benchmarked function.
static std::int64_t count_primes(std::int64_t n) {
    std::vector<std::uint8_t> flags = sieve_flags(n);
    std::int64_t count = 0;  // wide accumulator, not uint8_t
    for (std::int64_t k = 0; k <= n; ++k) {
        count += flags[k];
    }
    return count;
}

// Correctness checks, run before (and outside) any timing.
static bool run_checks() {
    const std::int64_t ns[] = {2, 10, 100, 100000, 1000000, 10000000};
    const std::int64_t expected[] = {1, 4, 25, 9592, 78498, 664579};
    bool ok = true;
    for (int i = 0; i < 6; ++i) {
        std::int64_t got = count_primes(ns[i]);
        std::cout << "check pi(" << ns[i] << ") = " << got << (got == expected[i] ? "  OK" : "  FAIL") << "\n";
        ok = ok && got == expected[i];
    }
    // Inspect surviving flags for a small input.
    std::vector<std::uint8_t> flags = sieve_flags(30);
    std::cout << "primes <= 30:";
    for (int k = 0; k <= 30; ++k)
        if (flags[k]) std::cout << ' ' << k;
    std::cout << "\n";
    return ok;
}

int main(int argc, char** argv) {
    const int warmup = argc > 1 ? std::atoi(argv[1]) : 5;
    const int block = argc > 2 ? std::atoi(argv[2]) : 1;
    const std::string csv_path = argc > 3 ? argv[3] : "../results/raw_cpp.csv";
    const int runs = 10;
    const std::int64_t sizes[] = {100000, 1000000, 10000000};

    if (!run_checks()) {
        std::cerr << "correctness checks failed\n";
        return 1;
    }

    std::ofstream csv(csv_path);
    csv << "language,N,block,warmup_calls,run,elapsed_ms,prime_count,batch_size\n";

    for (std::int64_t n : sizes) {
        for (int i = 0; i < warmup; ++i) count_primes(n);  // untimed warm-up

        std::vector<double> times;
        std::vector<std::int64_t> counts;
        for (int r = 0; r < runs; ++r) {
            auto t0 = std::chrono::steady_clock::now();
            std::int64_t c = count_primes(n);
            auto t1 = std::chrono::steady_clock::now();
            times.push_back(std::chrono::duration<double, std::milli>(t1 - t0).count());
            counts.push_back(c);  // result consumed outside the timed interval
        }
        for (int r = 0; r < runs; ++r) {
            csv << "C++," << n << ',' << block << ',' << warmup << ',' << r + 1 << ','
                << times[r] << ',' << counts[r] << ",1\n";
            std::cout << "N=" << n << " run " << r + 1 << ": " << times[r] << " ms, pi=" << counts[r] << "\n";
        }
    }
    return 0;
}
