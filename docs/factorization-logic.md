# Factorization Logic

This project factors an integer by applying a sequence of increasingly general
checks. The internal `factor_pair()` helper finds one non-trivial split:

```python
(divisor, n // divisor)
```

The public `factorize()` function recursively factors both returned values and
returns a sorted tuple of discovered factors.

If no factorization is found, `factorize()` returns `None`.

## Pipeline

`fast_factorization.factorize.factor_pair()` runs these stages:

1. Reject invalid input and tiny primes.
2. Return immediately for even numbers.
3. Detect perfect-square composites.
4. Try trial division by small primes.
5. Reject prime or probable-prime inputs with Miller-Rabin.
6. Try Fermat factorization for close factors.
7. Try Pollard p-1 for p-1-smooth factors.
8. Try Brent-style Pollard Rho for general medium composites.

## Default Limits

The public API and CLI use the same defaults unless an option is supplied:

| Step | Default | Disable or change |
| --- | ---: | --- |
| Multiprocessing | `processes=1` | `--processes N` |
| Trial division | primes up to `10_000` | fixed internal limit |
| Miller-Rabin below `2**64` | deterministic witnesses | fixed internal witness sets |
| Miller-Rabin above `2**64` | fixed probable-prime witness set | fixed internal witness set |
| Fermat | `min(100_000, max(1_000, isqrt(isqrt(n))))` | `--fermat-steps N`; `0` disables |
| Pollard p-1 | `10_000` smoothness bound | `--pm1-bound N`; `0` disables; max `1_000_000` |
| Pollard Rho attempts | `100` attempts | `--rho-attempts N`; `0` means unlimited |
| Pollard Rho steps | `1_000_000` polynomial steps per attempt | `--rho-max-steps N` |

## Stage Details

### Invalid, Prime, and Even Inputs

Inputs below `2` return `None`.

The primes `2` and `3` return `None`.

Even composites return immediately:

```python
(2, n // 2)
```

### Perfect Squares

Perfect-square detection uses an exact integer square-root check:

```python
root = isqrt(n)
root * root == n
```

When the optional `gmpy2` backend is installed, the same exact check is
accelerated with `gmpy2.is_square()` and `gmpy2.isqrt()`.

If `n` is a square composite, the result is:

```python
(root, root)
```

### Trial Division

The package precomputes primes up to `10_000` at import time and tests whether
any of them divide `n`. This is a fixed internal limit and is not exposed as a
CLI option.

This cheaply handles numbers with small factors and avoids heavier algorithms
when the answer is easy.

### Miller-Rabin

Miller-Rabin is used as a primality screen after cheap composite checks.

It is deterministic below `2**64`. Above `2**64`, the implementation uses a
fixed witness set and should be treated as a probable-prime screen.

If the number passes this stage, `factor_pair()` returns `None`.

### Fermat Factorization

Fermat factorization is effective when the two factors are close together.

It searches for:

```python
n = a*a - b*b = (a - b) * (a + b)
```

The default number of Fermat steps is adaptive:

```python
min(100_000, max(1_000, isqrt(isqrt(n))))
```

This means Fermat tries at least `1_000` iterations, at most `100_000`
iterations, and scales between those limits based on the size of `n`.

CLI tuning:

```bash
python -m fast_factorization --fermat-steps 0 N
python -m fast_factorization --fermat-steps 200000 N
```

Use `0` to disable the Fermat pre-pass.

### Pollard p-1

Pollard p-1 is effective when one factor `p` has `p - 1` composed only of small
prime powers.

The default smoothness bound is `10_000`. The package accepts bounds up to
`1_000_000`.

CLI tuning:

```bash
python -m fast_factorization --pm1-bound 50000 N
python -m fast_factorization --pm1-bound 0 N
```

Use `0` to disable Pollard p-1.

### Pollard Rho

The final built-in stage is Brent-style Pollard Rho.

Each attempt uses a polynomial of this form:

```python
f(x) = x*x + c mod n
```

Different attempts vary the starting value and constant. The implementation
batches GCD checks to reduce overhead.

The default retry budget is `100` attempts. Each attempt may run up to
`1_000_000` polynomial steps.

CLI tuning:

```bash
python -m fast_factorization --rho-attempts 200 --rho-max-steps 1000000 N
python -m fast_factorization --rho-attempts 0 N
```

`--rho-attempts 0` means unlimited attempts.

## Multiprocessing

The CLI can run Pollard Rho attempts across multiple worker processes:

```bash
python -m fast_factorization --processes 4 N
```

Fast-path stages run once before workers are started. Workers are only used for
the Pollard Rho stage.

The default is `--processes 1`. When more than one process is requested, the
worker count is capped at the machine CPU count.

If multiprocessing is unavailable in the environment, the CLI logs a warning
and falls back to one process.

## Return Semantics

`factor_pair(n)` returns:

- `(a, b)` when a non-trivial factor split is found
- `None` for invalid input
- `None` for prime or probable-prime input
- `None` if no factor is found within configured search limits

The returned pair is sorted in ascending order.

`factorize(n)` recursively factors both values returned by `factor_pair()` and
returns a sorted tuple. For example, factoring `100` returns:

```python
(2, 2, 5, 5)
```

Prime and probable-prime inputs return a one-item tuple, such as `(97,)`.

If any recursive subfactor cannot be split within the configured search limits,
`factorize(n)` returns `None` rather than returning a partial factorization.

## Scope

This project is designed for educational factorization and medium-sized
benchmark cases.

It is useful for:

- numbers with small factors
- perfect-square composites
- close-factor semiprimes
- p-1-smooth factors
- composites reachable by Pollard Rho

It is not intended to compete with QS/NFS implementations such as CADO-NFS,
YAFU, Msieve, or GGNFS on RSA challenge numbers.
