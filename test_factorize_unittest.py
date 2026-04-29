import math
import os
import time
import unittest

import challenge_numbers
import benchmark
import factorize


class TestFactorize(unittest.TestCase):

    def assert_factor_pair(self, number, factors):
        self.assertIsNotNone(factors)
        self.assertEqual(math.prod(factors), number)
        self.assertGreater(factors[0], 1)
        self.assertGreater(factors[1], 1)

    def test_digit_root(self):
        self.assertEqual(factorize.digit_root(0), 0)
        self.assertEqual(factorize.digit_root(36524), 2)
        self.assertEqual(factorize.digit_root(91999), 1)
        self.assertEqual(factorize.digit_root(98909990), 8)

    def test_last_digits(self):
        self.assertEqual(factorize.last_digits(36524, 1), 4)
        self.assertEqual(factorize.last_digits(36524, 2), 2)
        self.assertEqual(factorize.last_digits(36524, 3), 5)
        self.assertEqual(factorize.last_digits(36524, 4), 6)
        self.assertIsNone(factorize.last_digits(36524, 10))

    def test_last_digits_rejects_invalid_position(self):
        with self.assertRaises(ValueError):
            factorize.last_digits(36524, 0)

    def test_is_even(self):
        self.assertTrue(factorize.is_even(36524))
        self.assertFalse(factorize.is_even(36523))

    def test_jacobi(self):
        self.assertEqual(factorize.jacobi(1001, 9907), -1)
        with self.assertRaises(ValueError):
            factorize.jacobi(10, 9)

    def test_is_perfect_square(self):
        roots_dict = {
            82: 82 * 82,
            453: 453 * 453,
            894: 894 * 894,
            578934526542: 578934526542 * 578934526542,
        }
        roots_list = (
            6452627485,
            5869707947462525421,
            84857563655242423,
            75748439393939249574636535,
        )
        for root, square in roots_dict.items():
            self.assertEqual(factorize.is_perfect_square(square), root)
        for num in roots_list:
            self.assertEqual(factorize.is_perfect_square(num), 0)
        self.assertEqual(factorize.is_perfect_square(-4), 0)

    def test_is_prime(self):
        for num in (2, 3, 5, 97, 104729):
            self.assertTrue(factorize.is_prime(num))
        for num in (-1, 0, 1, 4, 91, 10000015400005913):
            self.assertFalse(factorize.is_prime(num))

    def test_factorize_rejects_invalid_and_prime_inputs(self):
        for num in (-10, 0, 1, 2, 97):
            self.assertIsNone(factorize.factorize(num))

    def test_factorize_respects_pollard_rho_attempt_limit(self):
        self.assertIsNone(
            factorize.factorize(
                challenge_numbers.PRACTICAL_RHO_SEMIPRIME,
                fermat_steps=0,
                pm1_bound=0,
                rho_attempts=1,
                rho_max_steps=1,
            )
        )

    def test_factorize_even_composite(self):
        self.assertEqual(factorize.factorize(100), (2, 50))

    def test_factorize_small_trial_division_factor(self):
        self.assertEqual(factorize.factorize(101 * 1000003), (101, 1000003))

    def test_factorize_perfect_square(self):
        self.assertEqual(factorize.factorize(49), (7, 7))

    def test_factorize_close_semiprime(self):
        number = 100000073 * 100000081
        self.assertEqual(factorize.factorize(number), (100000073, 100000081))

    def test_factorize_can_skip_fermat_fast_path(self):
        number = 100000073 * 100000081
        self.assertEqual(
            factorize.factorize(number, fermat_steps=0),
            (100000073, 100000081),
        )

    def test_factorize_pollard_rho_semiprime(self):
        self.assertEqual(
            factorize.factorize(challenge_numbers.PRACTICAL_RHO_SEMIPRIME),
            (
                challenge_numbers.PRACTICAL_RHO_LEFT,
                challenge_numbers.PRACTICAL_RHO_RIGHT,
            ),
        )

    def test_factorize_pollard_pm1_friendly_semiprime(self):
        self.assertEqual(
            factorize.factorize(challenge_numbers.PM1_FRIENDLY_SEMIPRIME),
            (
                challenge_numbers.PM1_FRIENDLY_LEFT,
                challenge_numbers.PM1_FRIENDLY_RIGHT,
            ),
        )

    def test_pollard_pm1_honors_bounds_above_trial_division_limit(self):
        number = 20_123 * 1_000_000_007
        self.assertIsNone(factorize._pollard_pm1(number, bound=10_000))
        self.assertEqual(factorize._pollard_pm1(number, bound=10_061), 20_123)

    def test_pollard_pm1_rejects_excessive_bounds(self):
        with self.assertRaises(ValueError):
            factorize._pollard_pm1(91, bound=factorize.POLLARD_PM1_MAX_BOUND + 1)

    def test_external_command_overrides_executable_lookup(self):
        self.assertEqual(
            benchmark._find_external_command("cado-nfs", "python /tmp/cado-nfs.py"),
            ["python", "/tmp/cado-nfs.py"],
        )

    def test_factorize_project_euler_3_number(self):
        factors = factorize.factorize(challenge_numbers.PROJECT_EULER_3)
        self.assert_factor_pair(challenge_numbers.PROJECT_EULER_3, factors)

    def test_rsa_100_reference_factors_are_correct(self):
        self.assertEqual(
            math.prod(challenge_numbers.RSA_100_FACTORS),
            challenge_numbers.RSA_100,
        )

    def test_factorize_small_semiprimes(self):
        self.assertEqual(factorize.factorize(15), (3, 5))
        self.assertEqual(factorize.factorize(21), (3, 7))
        self.assertEqual(factorize.factorize(91), (7, 13))

    def test_factorize_readme_example(self):
        number = 10000015400005913
        self.assert_factor_pair(number, factorize.factorize(number))

    @unittest.skipUnless(
        os.environ.get("RUN_BIG_FACTOR_TEST") == "1",
        "set RUN_BIG_FACTOR_TEST=1 to run the optional big-number performance test",
    )
    def test_factorize_big_close_semiprime_performance(self):
        started_at = time.perf_counter()
        factors = factorize.factorize(challenge_numbers.BIG_CLOSE_SEMIPRIME)
        elapsed = time.perf_counter() - started_at

        self.assertEqual(
            factors,
            (challenge_numbers.BIG_CLOSE_LEFT, challenge_numbers.BIG_CLOSE_RIGHT),
        )
        self.assertLess(elapsed, 1.0)


if __name__ == '__main__':
    unittest.main()
