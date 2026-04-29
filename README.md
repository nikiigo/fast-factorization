# fast-factorization

Educational integer factorization toolkit with a CLI, Python API, benchmarks,
and reference challenge numbers.

The implementation uses trial division, perfect-square checks, Fermat for close
factors, Pollard p-1, Miller-Rabin primality checks, and Pollard Rho. Miller-
Rabin is deterministic below `2**64` and used as a probable-prime screen above
that. It has no runtime dependencies outside the Python standard library.
Python 3.14 or newer is required.

This is not a production cryptography tool. It is not intended to break real
RSA keys or compete with specialized ECM/QS/NFS implementations.

## Installation

```bash
python -m pip install fast-factorization
```

For larger integers, install the optional native arithmetic backend:

```bash
python -m pip install "fast-factorization[fast]"
```

## Usage

```bash
python -m fast_factorization 10000015400005913
```

Example output:

```text
Factors: 100000073 100000081
Product check: 10000015400005913
Elapsed time hh:mm:ss 00:00:00
```

Use multiple workers when a factor is not found quickly:

```bash
python -m fast_factorization --processes 4 10000015400005913
```

By default, multiple workers split Pollard Rho attempts after the earlier stages
run sequentially. To race expensive fallback methods after cheap checks fail:

```bash
python -m fast_factorization --processes 4 --strategy methods 10000015400005913
```

Limit or disable the Fermat close-factor pre-pass:

```bash
python -m fast_factorization --fermat-steps 0 10000015400005913
```

Tune or disable Pollard p-1:

```bash
python -m fast_factorization --pm1-bound 50000 10009000070063
python -m fast_factorization --pm1-bound 0 10009000070063
```

The p-1 bound is a maximum. The implementation checks staged lower bounds first
and stops early when a factor is found.

Tune or disable Pollard Rho retry limits:

```bash
python -m fast_factorization --rho-attempts 200 --rho-max-steps 1000000 10000015400005913
python -m fast_factorization --rho-attempts 0 10000015400005913
```

Default limits are documented in the
[factorization logic guide](https://github.com/nikiigo/fast-factorization/blob/main/docs/factorization-logic.md#default-limits).

## Tests

From a source checkout:

```bash
python -m unittest -v
```

Run the optional big-number performance test:

```bash
RUN_BIG_FACTOR_TEST=1 python -m unittest test_factorize_unittest.TestFactorize.test_factorize_big_close_semiprime_performance -v
```

## Benchmark

From a source checkout:

```bash
python benchmark.py
```

Compare the current perfect-square check against the old digit/filter approach:

```bash
python benchmark_square_checks.py
```

Compare package performance against SymPy and refresh the README table:

```bash
python -m pip install sympy
python benchmark_compare.py --update-readme
```

Include a larger synthetic close-prime semiprime:

```bash
python benchmark.py --include-big
```

Show RSA-100 reference metadata without attempting to factor it:

```bash
python benchmark.py --show-rsa-100
```

Run RSA-100 with an installed external factoring tool:

```bash
python benchmark.py --external cado-nfs --external-timeout 3600
python benchmark.py --external yafu --external-timeout 3600
python benchmark.py --external cado-nfs --external-command /path/to/cado-nfs.py
python benchmark.py --external cado-nfs --external-command "python /path/to/cado-nfs.py"
```

## Performance Comparison

The table below compares the current `fast-factorization` checkout with
SymPy `factorint` from `sympy==1.14.0`. Times are medians of
7 runs on Python 3.14.3, Linux x86_64, Intel(R) Core(TM) i5-8350U CPU @ 1.70GHz.
Lower is better. These are local benchmark results, not general
performance guarantees.

Optional `gmpy2` backend: `2.3.0`.

Single-process factorization:

| Case | fast-factorization | SymPy `factorint` | Result |
| --- | ---: | ---: | --- |
| small semiprime | 0.0043 ms | 0.0044 ms | about equal |
| small trial factor | 0.0212 ms | 0.0531 ms | fast-factorization faster |
| close semiprime | 0.1934 ms | 0.1388 ms | SymPy faster |
| Project Euler 3 | 0.1030 ms | 0.2483 ms | fast-factorization faster |
| p-1 friendly | 0.9277 ms | 0.1335 ms | SymPy faster |
| rho semiprime | 4.2366 ms | 0.1133 ms | SymPy much faster |
| perfect square | 0.0174 ms | 0.1178 ms | fast-factorization faster |
| prime input | 0.0088 ms | 0.0173 ms | fast-factorization faster |
| big close semiprime | 0.5122 ms | 0.1796 ms | SymPy faster |

With `processes=4, strategy="rho"`:

| Case | fast-factorization `processes=4` | SymPy `factorint` | Result |
| --- | ---: | ---: | --- |
| small semiprime | 0.0036 ms | 0.0025 ms | SymPy faster |
| small trial factor | 0.0182 ms | 0.0500 ms | fast-factorization faster |
| close semiprime | 0.1710 ms | 0.1547 ms | about equal |
| Project Euler 3 | 0.0841 ms | 0.0799 ms | about equal |
| p-1 friendly | 0.7385 ms | 0.1050 ms | SymPy faster |
| rho semiprime | 26.5135 ms | 0.1239 ms | SymPy much faster |
| perfect square | 0.0194 ms | 0.1196 ms | fast-factorization faster |
| prime input | 0.0095 ms | 0.0177 ms | fast-factorization faster |
| big close semiprime | 0.5359 ms | 0.2015 ms | SymPy faster |

With `processes=4, strategy="methods"`:

| Case | fast-factorization `strategy=methods` | SymPy `factorint` | Result |
| --- | ---: | ---: | --- |
| small semiprime | 0.0038 ms | 0.0029 ms | SymPy faster |
| small trial factor | 0.0198 ms | 0.0536 ms | fast-factorization faster |
| close semiprime | 20.3841 ms | 0.1556 ms | SymPy much faster |
| Project Euler 3 | 0.1041 ms | 0.1513 ms | fast-factorization faster |
| p-1 friendly | 22.5737 ms | 0.2629 ms | SymPy much faster |
| rho semiprime | 25.8656 ms | 0.2485 ms | SymPy much faster |
| perfect square | 0.0365 ms | 0.1332 ms | fast-factorization faster |
| prime input | 0.0114 ms | 0.0334 ms | fast-factorization faster |
| big close semiprime | 19.9369 ms | 0.2017 ms | SymPy much faster |

This package is competitive on simple educational cases such as small factors,
perfect squares, and prime screening. SymPy is much stronger for general-purpose
integer factorization, especially Pollard-heavy cases. For small examples,
multiprocessing startup overhead can dominate the actual factorization work.
The `methods` strategy is experimental and is intended only for harder searches
where Fermat, Pollard p-1, and Pollard Rho each have enough work to justify
running in separate worker processes.

## Practice Numbers

The repo includes public and synthetic practice numbers in `fast_factorization/challenge_numbers.py`:

- Project Euler 3: `600851475143`
- Pollard p-1 friendly semiprime: `10009 * 1000000007`
- Practical Pollard Rho semiprime: `1000003 * 1000000007`
- Big close-prime semiprime: `(10**50 + 151) * (10**50 + 447)`
- RSA-100 reference value and known factors

RSA-100 is included as a reference only. This project is not expected to factor
RSA challenge numbers quickly; those require stronger methods such as ECM/GNFS.

## Scope

This project is intended for educational factoring and medium-sized benchmark
cases. It is useful for numbers with small factors, close factors, p-1 smooth
factors, or factors reachable by Pollard Rho. It is not intended to compete with
CADO-NFS, YAFU, Msieve, GGNFS, or other dedicated QS/NFS implementations on RSA
challenge numbers.

See the
[factorization logic guide](https://github.com/nikiigo/fast-factorization/blob/main/docs/factorization-logic.md)
for the full factorization pipeline.
See the
[publishing checklist](https://github.com/nikiigo/fast-factorization/blob/main/docs/publishing.md)
for the release process.

## API

```python
import fast_factorization

factors = fast_factorization.factorize(91)
print(factors)  # (7, 13)

print(fast_factorization.factorize(100))  # (2, 2, 5, 5)
print(fast_factorization.factor_pair(100))  # (2, 50)
```

`fast_factorization.factorize(n)` returns a sorted tuple of recursively
discovered factors. It returns `None` for invalid input or composites that were
not factored within the configured search limits.

Use `fast_factorization.factor_pair(n)` when you only want one non-trivial
split.

Lower-level helpers such as `digit_root()` and `jacobi()` remain available from
`fast_factorization.factorize` for compatibility, but they are not exported from
the top-level package API.
