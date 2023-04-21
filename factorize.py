import math
import sys
import sympy.ntheory as nt


def digit_root(n: int):
    return (n - 1) % 9 + 1


def last_digits(num: int, dig: int):
    my_dig = int(str(num)[-dig])
    return my_dig


def is_even(num: int):
    if (num % 2) == 0:
        return True
    else:
        return False


def jacobi(a: int, n: int):
    assert (n > a > 0 and n % 2 == 1)
    t = 1
    while a != 0:
        while a % 2 == 0:
            a /= 2
            r = n % 8
            if r == 3 or r == 5:
                t = -t
        a, n = n, a
        if a % 4 == n % 4 == 3:
            t = -t
        a %= n
    if n == 1:
        return t
    else:
        return 0


def is_perfect_square(num: int):
    last_dig = last_digits(num, 1)
    last_2dig = last_digits(num, 2)
    last_3dig = last_digits(num, 3)
    last_4dig = last_digits(num, 4)
    if last_dig not in (0, 1, 4, 5, 6, 9):
        return 0
    if last_dig == 5:
        if last_2dig == 2:
            if last_3dig not in (0, 2, 6):
                return 0
            if last_3dig == 6:
                if last_4dig not in (0, 5):
                    return 0
    elif last_dig == 6:
        if is_even(last_2dig):
            return 0
    elif last_dig in (1, 9):
        if not is_even(last_2dig):
            return 0
        if last_2dig in (2, 6):
            if is_even(last_3dig):
                return 0
        elif last_2dig in (0, 4, 8):
            if not is_even(last_3dig):
                return 0
    elif last_dig == 4:
        if not is_even(last_2dig):
            return 0
    if digit_root(num) not in (0, 1, 4, 7, 9):
        return 0
    for i in (13, 29, 43, 61, 83, 97, 179, 257, 683, 1427, 2399, 3547, 6971, 7919):
        if nt.legendre_symbol(num, i) == -1:
            return 0
    num_sqrt = math.isqrt(num)
    if num_sqrt * num_sqrt == num:
        return num_sqrt
    else:
        return 0


def factorize(num: int):
    s2 = pow(num, 2)
    s4 = pow(s2, 2)
    n = 0
    q4 = s2
    while q4 < s4:
        sqrt1 = is_perfect_square(s4 + pow(120 * n, 2))
        if not sqrt1:
            n += 1
            q4 += 120 * n
            continue
        else:
            q4 = 120 * n + sqrt1
            q2 = is_perfect_square(q4)
            if not q2:
                q = is_perfect_square(q2)
                if not q:
                    return q, num / q
                else:
                    n += 1
                    continue
            else:
                n += 1
                continue
    return num, 1


def main(argv: list):
    if len(argv) == 2:
        print(f'Prime numbers are: {factorize(argv[1])} ')
        sys.exit(0)
    else:
        print(f'Usage: {argv[0]} number')
        sys.exit(-1)


if __name__ == "__main__":
    main(sys.argv)
