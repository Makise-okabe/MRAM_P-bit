"""M4B common logit contract checks, independent of the three official graphs."""
import math
import random
import unittest
from experiments.m4_common_logit import (
    encode_gain, round_divide_signed_even, quantized_logit, beta_at,
    GAIN_FRAC, LOGIT_FRAC, LOGIT_LIMIT,
)


class TestM4B(unittest.TestCase):
    def test_exact_ties_to_even_including_negative(self):
        s=16
        self.assertEqual(round_divide_signed_even(1 << 15,s),0)
        self.assertEqual(round_divide_signed_even(3 << 15,s),2)
        self.assertEqual(round_divide_signed_even(5 << 15,s),2)
        self.assertEqual(round_divide_signed_even(-3 << 15,s),-2)
        self.assertEqual(round_divide_signed_even(-5 << 15,s),-2)

    def test_saturation_and_zero(self):
        g=encode_gain(2)
        self.assertEqual(quantized_logit(0,g),0)
        self.assertEqual(quantized_logit(100,g),LOGIT_LIMIT)
        self.assertEqual(quantized_logit(-100,g),-LOGIT_LIMIT)
        with self.assertRaises(ValueError):
            encode_gain(8.0)

    def test_random_integer_reference(self):
        rng=random.Random(777)
        for _ in range(2000):
            a=rng.randint(-44352,44352)
            g=rng.uniform(0.0001,7.99)
            gc=encode_gain(g)
            raw=a*gc
            q=round_divide_signed_even(raw,GAIN_FRAC-LOGIT_FRAC)
            want=max(-LOGIT_LIMIT,min(LOGIT_LIMIT,q))
            self.assertEqual(quantized_logit(a,gc),want)

    def test_m1_schedule_and_precision(self):
        self.assertEqual(beta_at(1.0,0),0.5)
        self.assertEqual(beta_at(1.0,49999),2.0)
        self.assertTrue(beta_at(1.0,0) < beta_at(1.0,24999))
        self.assertEqual(encode_gain(0.5),1<<(GAIN_FRAC-1))
        with self.assertRaises(ValueError):
            quantized_logit(0,0)


if __name__=="__main__":
    unittest.main()
