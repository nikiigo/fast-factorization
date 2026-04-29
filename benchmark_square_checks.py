import argparse
import math
import random
import statistics
import time

import factorize


LEGENDRE_PRIMES = (97, 179, 257, 683, 1427, 2399, 3547, 6971, 7919)


def _digit_root_old(num: int):
    return (num - 1) % 9 + 1


def _last_digit_at(num: int, position: int):
    try:
        return int(str(num)[-position])
    except IndexError:
        return None


def _is_even(num: int):
    return num % 2 == 0


def _legendre_symbol(num: int, prime: int):
    value = pow(num % prime, (prime - 1) // 2, prime)
    if value == prime - 1:
        return -1
    return value


def old_perfect_square_check(num: int):
    last_dig = _last_digit_at(num, 1)
    last_2dig = _last_digit_at(num, 2)
    last_3dig = _last_digit_at(num, 3)
    last_4dig = _last_digit_at(num, 4)

    if last_dig not in (0, 1, 4, 5, 6, 9):
        return 0
    if last_dig == 5:
        if last_2dig is not None and last_2dig == 2:
            if last_3dig is not None and last_3dig not in (0, 2, 6):
                return 0
            if last_3dig is not None and last_3dig == 6:
                if last_4dig is not None and last_4dig not in (0, 5):
                    return 0
    elif last_dig == 6:
        if last_2dig is not None and _is_even(last_2dig):
            return 0
    elif last_dig in (1, 9):
        if last_2dig is not None and not _is_even(last_2dig):
            return 0
        if last_2dig is not None and last_2dig in (2, 6):
            if last_3dig is not None and _is_even(last_3dig):
                return 0
        elif last_2dig is not None and last_2dig in (0, 4, 8):
            if last_3dig is not None and not _is_even(last_3dig):
                return 0
    elif last_dig == 4:
        if last_2dig is not None and not _is_even(last_2dig):
            return 0
    if _digit_root_old(num) not in (0, 1, 4, 7, 9):
        return 0
    for prime in LEGENDRE_PRIMES:
        if _legendre_symbol(num, prime) == -1:
            return 0

    num_sqrt = math.isqrt(num)
    if num_sqrt * num_sqrt == num:
        return num_sqrt
    return 0


def new_perfect_square_check(num: int):
    return factorize.is_perfect_square(num)


def _make_cases(size: int, bits: int, seed: int):
    rng = random.Random(seed)
    roots = [rng.getrandbits(bits) | 1 for _ in range(size)]
    squares = [root * root for root in roots]
    nonsquares = [square + 2 for square in squares]
    random_numbers = [rng.getrandbits(bits * 2) | 1 for _ in range(size)]
    return {
        f"{bits * 2}-bit squares": squares,
        f"{bits * 2}-bit near nonsquares": nonsquares,
        f"{bits * 2}-bit random nonsquares": random_numbers,
    }


def _time_call(func, numbers: list[int]):
    started_at = time.perf_counter()
    checksum = 0
    for number in numbers:
        checksum ^= func(number)
    return time.perf_counter() - started_at, checksum


def _measure(func, numbers: list[int], repeats: int):
    timings = []
    checksum = None
    for _ in range(repeats):
        elapsed, checksum = _time_call(func, numbers)
        timings.append(elapsed)
    return statistics.median(timings), checksum


def _parse_args():
    parser = argparse.ArgumentParser(
        description="Compare old and new perfect-square check performance.",
    )
    parser.add_argument("--size", type=int, default=5_000)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--seed", type=int, default=12345)
    return parser.parse_args()


def main():
    args = _parse_args()
    all_cases = {}
    for bits in (32, 128, 512):
        all_cases.update(_make_cases(args.size, bits, args.seed + bits))

    print(f"numbers per case: {args.size}")
    print(f"repeats: {args.repeats}")
    print()
    print(f"{'case':32} {'old':>10} {'new':>10} {'speedup':>10}")
    print("-" * 67)
    for name, numbers in all_cases.items():
        old_elapsed, old_checksum = _measure(old_perfect_square_check, numbers, args.repeats)
        new_elapsed, new_checksum = _measure(new_perfect_square_check, numbers, args.repeats)
        if old_checksum != new_checksum:
            raise AssertionError(f"checksum mismatch for {name}")
        speedup = old_elapsed / new_elapsed if new_elapsed else float("inf")
        print(f"{name:32} {old_elapsed:10.6f} {new_elapsed:10.6f} {speedup:9.2f}x")


if __name__ == "__main__":
    main()
