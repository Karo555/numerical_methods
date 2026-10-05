# Lab 1 - Sieve of Eratosthenes, Julia baseline implementation.
#
# Baseline rules: one-byte flags in Vector{UInt8} (not BitArray), explicit loops,
# no @inbounds, a fresh array on every call, timing with time_ns().
# Indexing: array position n + 1 represents integer n, everywhere.
#
# Usage: julia sieve.jl [warmup_calls=5] [block=1] [csv_path=../results/raw_julia.csv]

"Return a Vector{UInt8} where flags[k + 1] == 1 iff k is prime, for k in 0:n."
function sieve_flags(n::Int)
    flags = fill(UInt8(1), n + 1)   # bulk initialization is allowed
    flags[0 + 1] = 0
    flags[1 + 1] = 0
    p = 2
    # Outer loop stops at floor(sqrt(n)); p * p <= n avoids floating-point sqrt.
    while p * p <= n
        if flags[p + 1] == 1
            # Start at p^2: smaller multiples were marked by smaller primes.
            m = p * p
            while m <= n
                flags[m + 1] = 0
                m += p
            end
        end
        p += 1
    end
    return flags
end

"Number of primes <= n. This is the benchmarked function."
function count_primes(n::Int)
    flags = sieve_flags(n)
    count = 0                        # Int64 accumulator, not UInt8
    for k in 0:n
        count += flags[k + 1]
    end
    return count
end

"Correctness checks, run before (and outside) any timing."
function run_checks()
    expected = [(2, 1), (10, 4), (100, 25), (10^5, 9592), (10^6, 78498), (10^7, 664579)]
    ok = true
    for (n, want) in expected
        got = count_primes(n)
        println("check pi($n) = $got  ", got == want ? "OK" : "FAIL")
        ok &= got == want
    end
    flags = sieve_flags(30)
    println("primes <= 30: ", join([k for k in 0:30 if flags[k + 1] == 1], " "))
    return ok
end

function main(args)
    warmup = length(args) >= 1 ? parse(Int, args[1]) : 5
    block = length(args) >= 2 ? parse(Int, args[2]) : 1
    csv_path = length(args) >= 3 ? args[3] : joinpath(@__DIR__, "..", "results", "raw_julia.csv")
    runs = 10
    sizes = [10^5, 10^6, 10^7]

    println("Julia ", VERSION)
    run_checks() || error("correctness checks failed")

    open(csv_path, "w") do io
        println(io, "language,N,block,warmup_calls,run,elapsed_ms,prime_count,batch_size")
        for n in sizes
            for _ in 1:warmup           # untimed warm-up, same Int argument type
                count_primes(n)
            end
            times = Float64[]
            counts = Int[]
            for _ in 1:runs
                t0 = time_ns()
                c = count_primes(n)
                t1 = time_ns()
                push!(times, (t1 - t0) / 1e6)
                push!(counts, c)        # result consumed outside the timed interval
            end
            for r in 1:runs
                println(io, "Julia,$n,$block,$warmup,$r,$(times[r]),$(counts[r]),1")
                println("N=$n run $r: $(times[r]) ms, pi=$(counts[r])")
            end
        end
    end
end

main(ARGS)
