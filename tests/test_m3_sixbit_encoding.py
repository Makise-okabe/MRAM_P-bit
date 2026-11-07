"""M3 pure-Python bit-true six-bit codebook checks. No real Mac graph required."""
import math
import random
import tempfile
from pathlib import Path
import unittest

from experiments.m1_precision_codebooks import scalar_quantize, levels
from experiments.m3_sixbit_encoding import (
    FP6_POSITIVE_Q4, decode_raw_sixbit, encode_quantized_sixbit,
    row_accumulator_codes, row_coupling_value, make_vectors
)


class TestM3Sixbit(unittest.TestCase):
    def test_fp6_all_64_sign_and_magnitude_codes(self):
        self.assertEqual(len(FP6_POSITIVE_Q4),32)
        for code in range(64):
            exponent=(code>>2)&7
            frac=code&3
            q4 = (frac if exponent==0 else (4+frac)<<(exponent-1))
            actual=decode_raw_sixbit(code,"fp")
            self.assertEqual(actual, -q4 if code&32 else q4)
            self.assertAlmostEqual(abs(actual)/16,levels(6)[code&31])
        self.assertEqual(decode_raw_sixbit(31,"fp"),448) # exp 111 is finite, NOT NaN
        self.assertEqual(decode_raw_sixbit(63,"fp"),-448)
        self.assertEqual(decode_raw_sixbit(32,"fp"),0) # signed negative zero

    def test_symmetric_int_and_bfp_reserved_minimum(self):
        for family in ("int","bfp"):
            for q in range(-31,32):
                self.assertEqual(decode_raw_sixbit(q & 63,family),q)
            with self.assertRaisesRegex(ValueError,"reserved"):
                decode_raw_sixbit(32,family)

    def test_roundtrip_M1_quantized_value_exactness(self):
        rng=random.Random(20261107)
        for family in ("fp","int","bfp"):
            for scale in (0.125,1.0,3.5,2048.0):
                for x in (0,-1,1,-3500,1e-5,*[rng.uniform(-2500,2500) for _ in range(100)]):
                    q=scalar_quantize(x,family,6,scale)
                    raw=encode_quantized_sixbit(q,scale,family)
                    reconstructed=row_coupling_value(
                        decode_raw_sixbit(raw,family),family,scale)
                    self.assertTrue(math.isclose(q,reconstructed,rel_tol=1e-12,abs_tol=1e-12))

    def test_reject_nonrepresentable_weights(self):
        for family in ("fp","int","bfp"):
            with self.assertRaises(ValueError):
                encode_quantized_sixbit(0.3333333333,1.0,family)

    def test_full_row_integer_sum_vs_represented_weights(self):
        rng=random.Random(97531)
        for family in ("fp","int","bfp"):
            scale=4.0 if family=="bfp" else 1.5
            xs=[rng.uniform(-100,100) for _ in range(99)]
            spins=[bool(rng.randrange(2)) for _ in xs]
            q=[scalar_quantize(x,family,6,scale) for x in xs]
            codes=[encode_quantized_sixbit(x,scale,family) for x in q]
            got=row_coupling_value(row_accumulator_codes(codes,spins,family),family,scale)
            want=sum(c*(1 if s else -1) for c,s in zip(q,spins))
            self.assertTrue(math.isclose(got,want,rel_tol=1e-11,abs_tol=1e-8))

    def test_reproducible_99_term_rtl_vectors(self):
        with tempfile.TemporaryDirectory() as td:
            files=make_vectors(Path(td))
            self.assertEqual(set(files),{"fp","int","bfp"})
            for family,path in files.items():
                data=Path(path).read_text().strip().splitlines()
                self.assertEqual(len(data),99)
                accum=0
                for line in data:
                    code,spin,expect=line.split()
                    raw=int(code,16)
                    accum+=decode_raw_sixbit(raw,family)*(1 if int(spin) else -1)
                    self.assertEqual(accum,int(expect))


if __name__=="__main__":
    unittest.main()
