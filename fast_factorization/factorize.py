import argparse
import logging
import math
import os
import sys
import time
from multiprocessing import Pool

try:
    import gmpy2
except ImportError:
    gmpy2 = None


LOGGER = logging.getLogger(__name__)
SMALL_PRIMES = (
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37,
)
TRIAL_DIVISION_LIMIT = 10_000
FERMAT_MAX_STEPS = 100_000
POLLARD_PM1_BOUND = 10_000
POLLARD_PM1_MAX_BOUND = 1_000_000
POLLARD_RHO_MAX_ATTEMPTS = 100
POLLARD_RHO_MAX_STEPS = 1_000_000
MILLER_RABIN_WITNESSES_SMALL = (2, 3, 5, 7, 11, 13, 17)
MILLER_RABIN_WITNESSES_64 = (2, 325, 9375, 28178, 450775, 9780504, 1795265022)


def _generate_primes(limit: int):
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[0:2] = b"\x00\x00"
    for candidate in range(2, math.isqrt(limit) + 1):
        if sieve[candidate]:
            start = candidate * candidate
            step_count = ((limit - start) // candidate) + 1
            sieve[start:limit + 1:candidate] = b"\x00" * step_count
    return tuple(index for index, is_prime_candidate in enumerate(sieve) if is_prime_candidate)


TRIAL_PRIMES = _generate_primes(TRIAL_DIVISION_LIMIT)


def _primes_up_to(limit: int):
    if limit <= TRIAL_DIVISION_LIMIT:
        for prime in TRIAL_PRIMES:
            if prime > limit:
                break
            yield prime
        return

    yield from _generate_primes(limit)


def _gcd(left: int, right: int):
    if gmpy2 is not None:
        return int(gmpy2.gcd(left, right))
    return math.gcd(left, right)


def _isqrt(num: int):
    if gmpy2 is not None:
        return int(gmpy2.isqrt(num))
    return math.isqrt(num)


def _is_square(num: int):
    if gmpy2 is not None:
        return bool(gmpy2.is_square(num))
    root = math.isqrt(num)
    return root * root == num


def _pow_mod(base: int, exp: int, mod: int):
    if gmpy2 is not None:
        return int(gmpy2.powmod(base, exp, mod))
    return pow(base, exp, mod)


def digit_root(n: int):
    if n == 0:
        return 0
    return (abs(n) - 1) % 9 + 1


def last_digits(num: int, dig: int):
    if dig < 1:
        raise ValueError("dig must be greater than 0")
    try:
        return int(str(abs(num))[-dig])
    except IndexError:
        return None


def is_even(num: int):
    return num % 2 == 0


def jacobi(a: int, n: int):
    if not (n > a > 0 and n % 2 == 1):
        raise ValueError("jacobi requires n > a > 0 and odd n")

    t = 1
    while a != 0:
        while a % 2 == 0:
            a //= 2
            r = n % 8
            if r == 3 or r == 5:
                t = -t
        a, n = n, a
        if a % 4 == n % 4 == 3:
            t = -t
        a %= n
    if n == 1:
        return t
    return 0


def is_perfect_square(num: int):
    if num < 0:
        return 0
    if _is_square(num):
        return _isqrt(num)
    return 0


def is_prime(num: int):
    """Miller-Rabin primality test.

    Deterministic for numbers below 2**64. For larger numbers this is a
    probable-prime screen using a fixed witness set.
    """
    if num < 2:
        return False

    for prime in SMALL_PRIMES:
        if num == prime:
            return True
        if num % prime == 0:
            return False

    d = num - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2

    if num < 341_550_071_728_321:
        witnesses = MILLER_RABIN_WITNESSES_SMALL
    elif num < 2**64:
        witnesses = MILLER_RABIN_WITNESSES_64
    else:
        witnesses = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)

    for witness in witnesses:
        if witness >= num:
            continue
        x = _pow_mod(witness, d, num)
        if x == 1 or x == num - 1:
            continue
        for _ in range(s - 1):
            x = _pow_mod(x, 2, num)
            if x == num - 1:
                break
        else:
            return False
    return True


def _trial_division(num: int):
    for prime in TRIAL_PRIMES:
        if prime * prime > num:
            break
        if num % prime == 0:
            return prime
    return None


def _default_fermat_steps(num: int):
    return min(FERMAT_MAX_STEPS, max(1_000, _isqrt(_isqrt(num))))


def _fermat_factor(num: int, max_steps: int | None = None):
    if num % 2 == 0:
        return 2
    if max_steps is None:
        max_steps = _default_fermat_steps(num)
    if max_steps <= 0:
        return None

    a = _isqrt(num)
    if a * a < num:
        a += 1
    b_squared = a * a - num

    for _ in range(max_steps):
        b = is_perfect_square(b_squared)
        if b:
            factor = a - b
            if 1 < factor < num and num % factor == 0:
                return factor
        b_squared += 2 * a + 1
        a += 1
    return None


def _pollard_pm1(num: int, bound: int = POLLARD_PM1_BOUND, base: int = 2):
    if bound < 2:
        return None
    if bound > POLLARD_PM1_MAX_BOUND:
        raise ValueError(f"Pollard p-1 bound must be <= {POLLARD_PM1_MAX_BOUND}")
    if num % 2 == 0:
        return 2

    a = base % num
    for prime in _primes_up_to(bound):
        power = prime
        while power * prime <= bound:
            power *= prime
        a = _pow_mod(a, power, num)

    divisor = _gcd(a - 1, num)
    if divisor in (1, num):
        return None
    return divisor


def _pollard_rho(
    num: int,
    start: int = 2,
    constant: int = 1,
    batch_size: int = 128,
    max_steps: int = POLLARD_RHO_MAX_STEPS,
):
    if num % 2 == 0:
        return 2
    if num % 3 == 0:
        return 3

    def polynomial(value):
        return (_pow_mod(value, 2, num) + constant) % num

    y = start % num
    r = 1
    q = 1
    divisor = 1
    steps = 0

    while divisor == 1 and steps < max_steps:
        x = y
        for _ in range(r):
            y = polynomial(y)
            steps += 1

        k = 0
        while k < r and divisor == 1:
            ys = y
            for _ in range(min(batch_size, r - k)):
                y = polynomial(y)
                q = (q * abs(x - y)) % num
                steps += 1
            divisor = _gcd(q, num)
            k += batch_size
        r *= 2

    if divisor == num and "ys" in locals():
        divisor = 1
        while divisor == 1 and steps < max_steps * 2:
            ys = polynomial(ys)
            divisor = _gcd(abs(x - ys), num)
            steps += 1

    if divisor in (1, num):
        return None
    return divisor


def _find_factor(
    num: int,
    processes: int = 1,
    proc_id: int = 0,
    rho_attempts: int = POLLARD_RHO_MAX_ATTEMPTS,
    rho_max_steps: int = POLLARD_RHO_MAX_STEPS,
):
    stride = max(1, processes)
    attempt = proc_id
    attempts_used = 0
    while rho_attempts == 0 or attempts_used < rho_attempts:
        constant = 1 + attempt
        start = 2 + attempt * 2
        divisor = _pollard_rho(
            num,
            start=start,
            constant=constant,
            max_steps=rho_max_steps,
        )
        if divisor is not None:
            return divisor
        attempt += stride
        attempts_used += 1
    return None


def _sorted_factor_pair(num: int, divisor: int):
    return tuple(sorted((divisor, num // divisor)))


def _factorize_fast_paths(
    num: int,
    fermat_steps: int | None = None,
    pm1_bound: int = POLLARD_PM1_BOUND,
):
    if num < 2:
        return True, None
    if num in (2, 3):
        return True, None
    if num % 2 == 0:
        return True, (2, num // 2)

    square_root = is_perfect_square(num)
    if square_root and square_root > 1:
        return True, (square_root, square_root)

    trial_factor = _trial_division(num)
    if trial_factor is not None:
        return True, (trial_factor, num // trial_factor)

    if is_prime(num):
        return True, None

    fermat_factor = _fermat_factor(num, max_steps=fermat_steps)
    if fermat_factor is not None:
        return True, _sorted_factor_pair(num, fermat_factor)

    pm1_factor = _pollard_pm1(num, bound=pm1_bound)
    if pm1_factor is not None:
        return True, _sorted_factor_pair(num, pm1_factor)

    return False, None


def factor_pair(
    num: int,
    processes=1,
    proc_id=0,
    fermat_steps: int | None = None,
    pm1_bound: int = POLLARD_PM1_BOUND,
    rho_attempts: int = POLLARD_RHO_MAX_ATTEMPTS,
    rho_max_steps: int = POLLARD_RHO_MAX_STEPS,
):
    """Return two non-trivial factors of num, or None.

    None means the input is invalid, prime/probable-prime, or no factor was
    found within the configured search limits.
    """
    handled, result = _factorize_fast_paths(
        num,
        fermat_steps=fermat_steps,
        pm1_bound=pm1_bound,
    )
    if handled:
        return result

    divisor = _find_factor(
        num,
        processes=processes,
        proc_id=proc_id,
        rho_attempts=rho_attempts,
        rho_max_steps=rho_max_steps,
    )
    if divisor in (None, 1, num):
        return None

    return _sorted_factor_pair(num, divisor)


def _factorize_recursive(num: int, kwargs: dict):
    if num < 2:
        return None
    if is_prime(num):
        return (num,)

    pair = factor_pair(num, **kwargs)
    if pair is None:
        return None

    factors = []
    for part in pair:
        subfactors = _factorize_recursive(part, kwargs)
        if subfactors is None:
            return None
        factors.extend(subfactors)
    return tuple(sorted(factors))


def factorize(
    num: int,
    processes=1,
    proc_id=0,
    fermat_steps: int | None = None,
    pm1_bound: int = POLLARD_PM1_BOUND,
    rho_attempts: int = POLLARD_RHO_MAX_ATTEMPTS,
    rho_max_steps: int = POLLARD_RHO_MAX_STEPS,
):
    """Return a sorted tuple of recursively discovered factors, or None.

    None means the input is invalid or no factorization was found within the
    configured search limits. Prime and probable-prime inputs return `(num,)`.
    """
    kwargs = {
        "processes": processes,
        "proc_id": proc_id,
        "fermat_steps": fermat_steps,
        "pm1_bound": pm1_bound,
        "rho_attempts": rho_attempts,
        "rho_max_steps": rho_max_steps,
    }
    if processes > 1:
        return _factorize_parallel_recursive(
            num,
            processes,
            fermat_steps=fermat_steps,
            pm1_bound=pm1_bound,
            rho_attempts=rho_attempts,
            rho_max_steps=rho_max_steps,
        )
    return _factorize_recursive(num, kwargs)


def _pollard_worker(args):
    return _find_factor(*args)


def _parse_args(argv):
    parser = argparse.ArgumentParser(
        prog=argv[0],
        description="Recursively factor an integer.",
    )
    parser.add_argument("number", type=int)
    parser.add_argument(
        "-p",
        "--processes",
        type=int,
        default=1,
        help="number of worker processes to try in parallel",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="enable debug logging",
    )
    parser.add_argument(
        "--fermat-steps",
        type=int,
        default=None,
        help="maximum Fermat iterations before Pollard Rho",
    )
    parser.add_argument(
        "--pm1-bound",
        type=int,
        default=POLLARD_PM1_BOUND,
        help=f"smoothness bound for Pollard p-1; use 0 to disable; max {POLLARD_PM1_MAX_BOUND}",
    )
    parser.add_argument(
        "--rho-attempts",
        type=int,
        default=POLLARD_RHO_MAX_ATTEMPTS,
        help="Pollard Rho retry attempts; use 0 for unlimited",
    )
    parser.add_argument(
        "--rho-max-steps",
        type=int,
        default=POLLARD_RHO_MAX_STEPS,
        help="maximum polynomial steps per Pollard Rho attempt",
    )
    return parser.parse_args(argv[1:])


def _factorize_parallel(
    num: int,
    processes: int,
    fermat_steps: int | None = None,
    pm1_bound: int = POLLARD_PM1_BOUND,
    rho_attempts: int = POLLARD_RHO_MAX_ATTEMPTS,
    rho_max_steps: int = POLLARD_RHO_MAX_STEPS,
):
    if processes <= 1:
        return factor_pair(
            num,
            fermat_steps=fermat_steps,
            pm1_bound=pm1_bound,
            rho_attempts=rho_attempts,
            rho_max_steps=rho_max_steps,
        )

    handled, result = _factorize_fast_paths(
        num,
        fermat_steps=fermat_steps,
        pm1_bound=pm1_bound,
    )
    if handled:
        return result

    worker_count = min(processes, os.cpu_count() or 1)
    worker_attempts = rho_attempts
    if rho_attempts > 0:
        worker_attempts = math.ceil(rho_attempts / worker_count)
    args = [
        (num, worker_count, proc_id, worker_attempts, rho_max_steps)
        for proc_id in range(worker_count)
    ]
    try:
        with Pool(worker_count) as pool:
            for divisor in pool.imap_unordered(_pollard_worker, args):
                if divisor not in (None, 1, num):
                    pool.terminate()
                    return _sorted_factor_pair(num, divisor)
    except OSError as exc:
        LOGGER.warning("multiprocessing unavailable: %s; falling back to one process", exc)
        return factor_pair(
            num,
            fermat_steps=fermat_steps,
            pm1_bound=pm1_bound,
            rho_attempts=rho_attempts,
            rho_max_steps=rho_max_steps,
        )
    return None


def _factorize_parallel_recursive(
    num: int,
    processes: int,
    fermat_steps: int | None = None,
    pm1_bound: int = POLLARD_PM1_BOUND,
    rho_attempts: int = POLLARD_RHO_MAX_ATTEMPTS,
    rho_max_steps: int = POLLARD_RHO_MAX_STEPS,
):
    if num < 2:
        return None
    if is_prime(num):
        return (num,)

    pair = _factorize_parallel(
        num,
        processes,
        fermat_steps=fermat_steps,
        pm1_bound=pm1_bound,
        rho_attempts=rho_attempts,
        rho_max_steps=rho_max_steps,
    )
    if pair is None:
        return None

    factors = []
    for part in pair:
        subfactors = _factorize_parallel_recursive(
            part,
            processes,
            fermat_steps=fermat_steps,
            pm1_bound=pm1_bound,
            rho_attempts=rho_attempts,
            rho_max_steps=rho_max_steps,
        )
        if subfactors is None:
            return None
        factors.extend(subfactors)
    return tuple(sorted(factors))


def main(argv=None):
    if argv is None:
        argv = sys.argv

    args = _parse_args(argv)
    logging.basicConfig(
        stream=sys.stderr,
        level=logging.DEBUG if args.verbose else logging.WARNING,
    )

    if args.processes < 1:
        print("--processes must be greater than 0", file=sys.stderr)
        return 2
    if args.fermat_steps is not None and args.fermat_steps < 0:
        print("--fermat-steps must be greater than or equal to 0", file=sys.stderr)
        return 2
    if args.pm1_bound < 0:
        print("--pm1-bound must be greater than or equal to 0", file=sys.stderr)
        return 2
    if args.pm1_bound > POLLARD_PM1_MAX_BOUND:
        print(f"--pm1-bound must be <= {POLLARD_PM1_MAX_BOUND}", file=sys.stderr)
        return 2
    if args.rho_attempts < 0:
        print("--rho-attempts must be greater than or equal to 0", file=sys.stderr)
        return 2
    if args.rho_max_steps < 1:
        print("--rho-max-steps must be greater than 0", file=sys.stderr)
        return 2

    started_at = time.time()
    result = _factorize_parallel_recursive(
        args.number,
        args.processes,
        args.fermat_steps,
        args.pm1_bound,
        args.rho_attempts,
        args.rho_max_steps,
    )
    elapsed = time.time() - started_at

    if result is None:
        print(f"No non-trivial factor found for {args.number}")
        return 1

    print(f"Factors: {' '.join(str(factor) for factor in result)}")
    print(f"Product check: {math.prod(result)}")
    print("Elapsed time hh:mm:ss", time.strftime("%H:%M:%S", time.gmtime(elapsed)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
