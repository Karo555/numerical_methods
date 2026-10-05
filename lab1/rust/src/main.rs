//! Lab 1 - Sieve of Eratosthenes, Rust implementation (extra credit).
//!
//! Vec<u8> flags, u64 accumulator, ordinary safe (bounds-checked) indexing, no unsafe,
//! timing with std::time::Instant.
//!
//! Usage: target/release/sieve_rust [warmup_calls=5] [block=1] [csv_path=../results/raw_rust.csv]

use std::env;
use std::fs::File;
use std::io::{BufWriter, Write};
use std::time::Instant;

/// Returns flags for 0..=n: flags[k] == 1 iff k is prime.
fn sieve_flags(n: usize) -> Vec<u8> {
    let mut flags = vec![1u8; n + 1]; // bulk initialization is allowed
    flags[0] = 0;
    flags[1] = 0;
    // Outer loop stops at floor(sqrt(n)); marking starts at p * p.
    let mut p = 2usize;
    while p * p <= n {
        if flags[p] == 1 {
            let mut m = p * p;
            while m <= n {
                flags[m] = 0;
                m += p;
            }
        }
        p += 1;
    }
    flags
}

/// Number of primes <= n. This is the benchmarked function.
fn count_primes(n: usize) -> u64 {
    let flags = sieve_flags(n);
    let mut count: u64 = 0;
    for k in 0..=n {
        count += flags[k] as u64;
    }
    count
}

fn run_checks() -> bool {
    let expected = [(2, 1), (10, 4), (100, 25), (100_000, 9592), (1_000_000, 78498), (10_000_000, 664579)];
    let mut ok = true;
    for &(n, want) in &expected {
        let got = count_primes(n);
        println!("check pi({}) = {}  {}", n, got, if got == want { "OK" } else { "FAIL" });
        ok &= got == want;
    }
    let flags = sieve_flags(30);
    let primes: Vec<String> = (0..=30).filter(|&k| flags[k] == 1).map(|k| k.to_string()).collect();
    println!("primes <= 30: {}", primes.join(" "));
    ok
}

fn main() -> std::io::Result<()> {
    let args: Vec<String> = env::args().collect();
    let warmup: usize = args.get(1).map_or(5, |s| s.parse().unwrap());
    let block: usize = args.get(2).map_or(1, |s| s.parse().unwrap());
    let csv_path = args.get(3).cloned().unwrap_or_else(|| "../results/raw_rust.csv".to_string());
    let runs = 10;
    let sizes = [100_000usize, 1_000_000, 10_000_000];

    if !run_checks() {
        eprintln!("correctness checks failed");
        std::process::exit(1);
    }

    let mut csv = BufWriter::new(File::create(csv_path)?);
    writeln!(csv, "language,N,block,warmup_calls,run,elapsed_ms,prime_count,batch_size")?;
    for &n in &sizes {
        for _ in 0..warmup {
            count_primes(n); // untimed warm-up
        }
        let mut times = Vec::with_capacity(runs);
        let mut counts = Vec::with_capacity(runs);
        for _ in 0..runs {
            let t0 = Instant::now();
            let c = count_primes(n);
            let dt = t0.elapsed();
            times.push(dt.as_secs_f64() * 1e3);
            counts.push(c); // result consumed outside the timed interval
        }
        for r in 0..runs {
            writeln!(csv, "Rust,{},{},{},{},{},{},1", n, block, warmup, r + 1, times[r], counts[r])?;
            println!("N={} run {}: {} ms, pi={}", n, r + 1, times[r], counts[r]);
        }
    }
    Ok(())
}
