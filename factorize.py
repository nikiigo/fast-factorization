import math
import sys
import sympy.ntheory as nt
import logging

logging.basicConfig(stream=sys.stdout, level=logging.WARNING)


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
    logging.debug(f'Check if the {num} is perfect square')
    last_dig = last_digits(num, 1)
    last_2dig = last_digits(num, 2)
    last_3dig = last_digits(num, 3)
    last_4dig = last_digits(num, 4)
    logging.debug(f'last digits are:'
                  f'{str(last_dig), str(last_2dig), str(last_3dig), str(last_4dig)}')
    logging.debug(f'Check if the {num} is perfect square by last numbers')
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
    for i in (97, 179, 257, 683, 1427, 2399, 3547, 6971, 7919):
        logging.debug(f'Check if the {num} is perfect square by legendre symbol for {i}')
        if nt.legendre_symbol(num, i) == -1:
            return 0
    logging.debug(f'Calculate square root of {num}')
    num_sqrt = math.isqrt(num)
    if num_sqrt * num_sqrt == num:
        logging.debug(f'Calculated square root of {num} = {num_sqrt} it is num_sqrt')
        return num_sqrt
    else:
        return 0


def factorize(num: int):
    logging.debug(f's = {num}')
    s2 = pow(num, 2)
    logging.debug(f's2 = {s2}')
    s4 = pow(s2, 2)
    logging.debug(f's4 = {s4}')
    n = 0
    n_max = math.floor(s2 / (120 * math.isqrt(3)))
    q4 = s2
    while n < n_max:
        sqrt1 = is_perfect_square(pow(120 * n, 2) + s4)
        logging.debug(f'Iteration number = {n} of {n_max}')
        logging.debug(f'sqrt1 = sqrt({pow(120 * n, 2) + s4})')
        logging.debug(f'q4 = {q4}')
        if not sqrt1:
            logging.debug(f'{pow(120 * n, 2) + s4} is not perfect square')
            n += 1
            continue
        else:
            logging.debug(f'sqrt1 = {sqrt1}')
            logging.warning(f'Iteration number = {n} of {n_max}')
            q4 = sqrt1 - 120 * n
            q2 = is_perfect_square(q4)
            if q2:
                logging.debug(f'q2 = {q2}')
                logging.warning(f'Iteration number = {n} of {n_max}')
                q = is_perfect_square(q2)
                if q:
                    logging.debug(f'q= {q}')
                    logging.warning(f'Iteration number = {n} of {n_max}')
                    if not num % q:
                        return q, int(num / q)
                    else:
                        n += 1
                        continue
                else:
                    logging.debug(f'{q4} is not perfect square')
                    n += 1
                    continue
            else:
                logging.debug(f'{q2} is not perfect square')
                n += 1
                continue
    return num, 1


def main(argv: list):
    if len(argv) == 2:
        print(f'Prime numbers are: {factorize(int(argv[1]))} ')
        sys.exit(0)
    else:
        print(f'Usage: {argv[0]} number')
        sys.exit(-1)


if __name__ == "__main__":
    main(sys.argv)
