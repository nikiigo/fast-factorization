import unittest

import factorize


class TestFactorize(unittest.TestCase):

    def test_digit_root(self):
        self.assertEqual(factorize.digit_root(36524), 2)
        self.assertEqual(factorize.digit_root(91999), 1)
        self.assertEqual(factorize.digit_root(98909990), 8)

    def test_last_digits(self):
        self.assertEqual(factorize.last_digits(36524, 1), 4)
        self.assertEqual(factorize.last_digits(36524, 2), 2)
        self.assertEqual(factorize.last_digits(36524, 3), 5)
        self.assertEqual(factorize.last_digits(36524, 4), 6)

    def test_is_even(self):
        self.assertTrue(factorize.is_even(36524))
        self.assertFalse(factorize.is_even(36523))

    def test_is_perfect_square(self):
        roots_dict = {82: 82 * 82, 453: 453 * 453, 894: 894 * 894, 578934526542: 578934526542 * 578934526542}
        roots_list = (6452627485, 5869707947462525421, 84857563655242423, 75748439393939249574636535)
        for num in roots_dict:
            self.assertEqual(factorize.is_perfect_square(roots_dict[num]), num)
        for num in roots_list:
            self.assertEqual(factorize.is_perfect_square(num), 0)

    def test_factorize(self):
        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
