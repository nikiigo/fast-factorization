import math
import sympy.ntheory as nt
import logging
import sys
from multiprocessing import current_process


def digit_root(n: int):
    return (n - 1) % 9 + 1


def last_digits(num: int, dig: int):
    try:
        my_dig = int(str(num)[-dig])
        return my_dig
    except IndexError:
        return None


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
    logger = logging.getLogger('PerfectSquare')
    logger.debug(f'Check if the {num} is perfect square')
    last_dig = last_digits(num, 1)
    last_2dig = last_digits(num, 2)
    last_3dig = last_digits(num, 3)
    last_4dig = last_digits(num, 4)
    logger.debug(f'last digits are:'
                 f'{str(last_dig), str(last_2dig), str(last_3dig), str(last_4dig)}')
    logger.debug(f'Check if the {num} is perfect square by last numbers')
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
        if last_2dig is not None and is_even(last_2dig):
            return 0
    elif last_dig in (1, 9):
        if last_2dig is not None and not is_even(last_2dig):
            return 0
        if last_2dig is not None and last_2dig in (2, 6):
            if last_3dig is not None and is_even(last_3dig):
                return 0
        elif last_2dig is not None and last_2dig in (0, 4, 8):
            if last_3dig is not None and not is_even(last_3dig):
                return 0
    elif last_dig == 4:
        if last_2dig is not None and not is_even(last_2dig):
            return 0
    if digit_root(num) not in (0, 1, 4, 7, 9):
        return 0
    for i in (97, 179, 257, 683, 1427, 2399, 3547, 6971, 7919):
        logger.debug(f'Check if the {num} is perfect square by legendre symbol for {i}')
        if nt.legendre_symbol(num, i) == -1:
            return 0
    logger.debug(f'Calculate square root of {num}')
    num_sqrt = math.isqrt(num)
    if num_sqrt * num_sqrt == num:
        logger.debug(f'Calculated square root of {num} = {num_sqrt} it is num_sqrt')
        return num_sqrt
    else:
        return 0


def factorize(num: int, processes=1, proc_id=0):
    if current_process().name != 'MainProcess':
        logger = logging.getLogger('Factorization:' + str(proc_id))
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    else:
        logger = logging.getLogger()
    """logging.debug(f's = {num}')
    s2 = pow(num, 2)
    logging.debug(f's2 = {s2}')
    s4 = pow(s2, 2)
    logging.debug(f's4 = {s4}')
    n_max = math.floor(s2 / (120 * math.isqrt(3)))
    n_min = num // 30 * math.isqrt(num)
    n = n_min
    logging.info(f'n_min = {n}, m_max {n_max}')
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
            logging.info(f'Iteration number = {n} of {n_max}')
            q4 = sqrt1 - 120 * n
            q2 = is_perfect_square(q4)
            if q2:
                logging.debug(f'q2 = {q2}')
                logging.info(f'Iteration number = {n} of {n_max}')
                q = is_perfect_square(q2)
                if q:
                    logging.debug(f'q= {q}')
                    logging.info(f'Iteration number = {n} of {n_max}')
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
    return num, 1"""
    s = num
    n_max = math.floor(math.floor(math.isqrt(s)) / (2 * processes) * (proc_id + 1))
    n_min = 1 + math.floor(math.isqrt(s) / (2 * processes) * proc_id)
    n = n_max
    logger.info(f'n_min = {n_min}, m_max {n_max}')
    while n >= n_min:
        sqrt1 = is_perfect_square(pow(n, 2) + s)
        logger.debug(f'Iteration number = {n_max + n_min - n} of {n_max}')
        logger.debug(f'sqrt1 = sqrt({pow(n, 2) + s})')
        if not sqrt1:
            logger.debug(f'{pow(n, 2) + s} is not perfect square')
            n += -1
            continue
        else:
            logger.debug(f'sqrt1 = {sqrt1}')
            logger.info(f'Iteration number = {n_max + n_min - n} of {n_max}')
            q = sqrt1 - n
            pmod = s % q
            if pmod:
                logger.debug(f'q = {q}')
                logger.debug(f'Iteration number = {n_max + n_min - n} of {n_max}')
                n += -1
                continue
            else:
                logger.debug(f'Iteration number = {n_max + n_min - n} of {n_max}')
                return q, int(s / q)
    return None


def main(argv: list):
    import multiprocessing as mp
    import time
    if len(argv) == 2:
        st = time.time()
        cpu_to_use = 6
        # start the process pool
        prc = mp.Pool(cpu_to_use)
        # submit tasks and collect results
        args = [(int(argv[1]), cpu_to_use, i) for i in range(cpu_to_use)]
        prc_results = prc.starmap(factorize, args)
        prc.close()
        prc.join()
        # Combine results
        results = ()
        for result in prc_results:
            if result is not None:
                results = results + result
        et = time.time() - st
        time_format = time.strftime("%H:%M:%S", time.gmtime(et))
        print(f'Prime numbers are: {results} ')
        print("Elapsed time hh:mm:ss", time_format)
        sys.exit(0)
    else:
        print(f'Usage: {argv[0]} number')
        sys.exit(-1)


if __name__ != "__main__":
    pass
else:
    main(sys.argv)
