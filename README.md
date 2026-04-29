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

Limit or disable the Fermat close-factor pre-pass:

```bash
python -m fast_factorization --fermat-steps 0 10000015400005913
```

Tune or disable Pollard p-1:

```bash
python -m fast_factorization --pm1-bound 50000 10009000070063
python -m fast_factorization --pm1-bound 0 10009000070063
```

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

The table below compares the PyPI package `fast-factorization==0.1.0` with
SymPy `factorint` from `sympy==1.14.0`. Times are medians of 7 runs on Python
3.14.3, Linux x86_64, Intel Core i5-8350U. Lower is better. These are local
benchmark results, not general performance guarantees.

| Case | fast-factorization | SymPy `factorint` | Result |
| --- | ---: | ---: | --- |
| small semiprime | 0.0038 ms | 0.0038 ms | same |
| small trial factor | 0.0255 ms | 0.0469 ms | fast-factorization faster |
| close semiprime | 0.2150 ms | 0.1342 ms | SymPy faster |
| Project Euler 3 | 0.0969 ms | 0.0905 ms | about equal |
| p-1 friendly | 6.4198 ms | 0.1195 ms | SymPy much faster |
| rho semiprime | 8.9985 ms | 0.2068 ms | SymPy much faster |
| perfect square | 0.0746 ms | 0.1859 ms | fast-factorization faster |
| prime input | 0.0111 ms | 0.0155 ms | fast-factorization faster |
| big close semiprime | 2.8214 ms | 0.2220 ms | SymPy faster |

With the optional `gmpy2` backend installed:

| Case | fast-factorization + `gmpy2` | SymPy `factorint` | Result |
| --- | ---: | ---: | --- |
| small semiprime | 0.0038 ms | 0.0039 ms | same |
| small trial factor | 0.0184 ms | 0.0451 ms | fast-factorization faster |
| close semiprime | 0.1744 ms | 0.1398 ms | SymPy slightly faster |
| Project Euler 3 | 0.1608 ms | 0.0799 ms | SymPy faster |
| p-1 friendly | 1.5618 ms | 0.1053 ms | SymPy much faster |
| rho semiprime | 5.5338 ms | 0.1210 ms | SymPy much faster |
| perfect square | 0.0446 ms | 0.1177 ms | fast-factorization faster |
| prime input | 0.0101 ms | 0.0186 ms | fast-factorization faster |
| big close semiprime | 0.5950 ms | 0.1917 ms | SymPy faster |

This package is competitive on simple educational cases such as small factors,
perfect squares, and prime screening. SymPy is much stronger for general-purpose
integer factorization, especially Pollard-heavy cases.

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
