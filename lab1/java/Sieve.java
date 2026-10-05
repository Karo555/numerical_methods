// Lab 1 - Sieve of Eratosthenes, Java implementation (extra credit).
//
// byte[] flags with 0/1 values, long accumulator, warm-up and measurement in the same JVM,
// timing with System.nanoTime().
//
// Usage: java Sieve [warmup_calls=5] [block=1] [csv_path=../results/raw_java.csv]

import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.Arrays;

public class Sieve {
    /** Returns flags for 0..n: flags[k] == 1 iff k is prime. */
    static byte[] sieveFlags(int n) {
        byte[] flags = new byte[n + 1];
        Arrays.fill(flags, (byte) 1);  // bulk initialization is allowed
        flags[0] = 0;
        flags[1] = 0;
        // long p avoids overflow in p * p; loop stops at floor(sqrt(n)).
        for (long p = 2; p * p <= n; p++) {
            if (flags[(int) p] == 1) {
                for (long m = p * p; m <= n; m += p) {
                    flags[(int) m] = 0;
                }
            }
        }
        return flags;
    }

    /** Number of primes <= n. This is the benchmarked function. */
    static long countPrimes(int n) {
        byte[] flags = sieveFlags(n);
        long count = 0;
        for (int k = 0; k <= n; k++) {
            count += flags[k];
        }
        return count;
    }

    static boolean runChecks() {
        int[] ns = {2, 10, 100, 100_000, 1_000_000, 10_000_000};
        long[] expected = {1, 4, 25, 9592, 78498, 664579};
        boolean ok = true;
        for (int i = 0; i < ns.length; i++) {
            long got = countPrimes(ns[i]);
            System.out.println("check pi(" + ns[i] + ") = " + got + (got == expected[i] ? "  OK" : "  FAIL"));
            ok &= got == expected[i];
        }
        byte[] flags = sieveFlags(30);
        StringBuilder sb = new StringBuilder("primes <= 30:");
        for (int k = 0; k <= 30; k++) if (flags[k] == 1) sb.append(' ').append(k);
        System.out.println(sb);
        return ok;
    }

    public static void main(String[] args) throws IOException {
        int warmup = args.length > 0 ? Integer.parseInt(args[0]) : 5;
        int block = args.length > 1 ? Integer.parseInt(args[1]) : 1;
        String csvPath = args.length > 2 ? args[2] : "../results/raw_java.csv";
        int runs = 10;
        int[] sizes = {100_000, 1_000_000, 10_000_000};

        System.out.println("Java " + System.getProperty("java.version") + " " + System.getProperty("java.vm.name"));
        if (!runChecks()) {
            System.err.println("correctness checks failed");
            System.exit(1);
        }

        try (PrintWriter csv = new PrintWriter(new FileWriter(csvPath))) {
            csv.println("language,N,block,warmup_calls,run,elapsed_ms,prime_count,batch_size");
            for (int n : sizes) {
                for (int i = 0; i < warmup; i++) countPrimes(n);  // untimed warm-up
                double[] times = new double[runs];
                long[] counts = new long[runs];
                for (int r = 0; r < runs; r++) {
                    long t0 = System.nanoTime();
                    long c = countPrimes(n);
                    long t1 = System.nanoTime();
                    times[r] = (t1 - t0) / 1e6;
                    counts[r] = c;  // result consumed outside the timed interval
                }
                for (int r = 0; r < runs; r++) {
                    csv.println("Java," + n + "," + block + "," + warmup + "," + (r + 1) + "," + times[r] + "," + counts[r] + ",1");
                    System.out.println("N=" + n + " run " + (r + 1) + ": " + times[r] + " ms, pi=" + counts[r]);
                }
            }
        }
    }
}
