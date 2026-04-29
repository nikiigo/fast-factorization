# fast-factorization

Factor composite integers into two non-trivial factors.

The implementation uses trial division, perfect-square checks, Fermat for close
factors, Pollard p-1, deterministic Miller-Rabin primality checks, and Pollard
Rho. It has no runtime dependencies outside the Python standard library. Python
3.14 or newer is required.

For larger integers, install the optional native arithmetic backend:

```bash
python -m pip install ".[fast]"
```

![Algorithm](./docs/fast-factorization.jpg?raw=true "Scheme of one-point and five-points models")

## Usage

```bash
python factorize.py 10000015400005913
```

Example output:

```text
Factors: 100000073 100000081
Product check: 10000015400005913
Elapsed time hh:mm:ss 00:00:00
```

Use multiple workers when a factor is not found quickly:

```bash
python factorize.py --processes 4 10000015400005913
```

Limit or disable the Fermat close-factor pre-pass:

```bash
python factorize.py --fermat-steps 0 10000015400005913
```

Tune or disable Pollard p-1:

```bash
python factorize.py --pm1-bound 50000 10009000070063
python factorize.py --pm1-bound 0 10009000070063
```

## Tests

```bash
python -m unittest -v
```

Run the optional big-number performance test:

```bash
RUN_BIG_FACTOR_TEST=1 python -m unittest test_factorize_unittest.TestFactorize.test_factorize_big_close_semiprime_performance -v
```

## Benchmark

```bash
python benchmark.py
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
```

## Practice Numbers

The repo includes public and synthetic practice numbers in `challenge_numbers.py`:

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

## API

```python
import factorize

factors = factorize.factorize(91)
print(factors)  # (7, 13)
```

`factorize.factorize(n)` returns a two-item tuple for composite integers and
`None` for invalid input or prime numbers.
