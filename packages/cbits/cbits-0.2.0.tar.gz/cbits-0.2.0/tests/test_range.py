import unittest
from cbits import BitVector

class TestRange(unittest.TestCase):
    def setUp(self):
        self.bv = BitVector(16)

    def test_set_range_basic(self):
        self.bv.set_range(4, 6)
        for i in range(16):
            if 4 <= i < 10:
                self.assertTrue(self.bv.get(i))
            else:
                self.assertFalse(self.bv.get(i))

    def test_clear_range_basic(self):
        self.bv.set_range(0, 16)
        self.bv.clear_range(5, 5)
        for i in range(16):
            if 5 <= i < 10:
                self.assertFalse(self.bv.get(i))
            else:
                self.assertTrue(self.bv.get(i))

    def test_flip_range_basic(self):
        self.bv.set_range(0, 16)
        self.bv.flip_range(8, 4)
        for i in range(16):
            if 8 <= i < 12:
                self.assertFalse(self.bv.get(i))
            else:
                self.assertTrue(self.bv.get(i))

    def test_range_out_of_bounds(self):
        with self.assertRaises(IndexError):
            self.bv.set_range(12, 10)
        with self.assertRaises(IndexError):
            self.bv.clear_range(20, 1)
        with self.assertRaises(IndexError):
            self.bv.flip_range(0, 100)

    def test_zero_length_range(self):
        self.bv.set(3)
        self.bv.set_range(5, 0)
        self.bv.clear_range(5, 0)
        self.bv.flip_range(5, 0)
        self.assertTrue(self.bv.get(3))

    def test_tail_mask_behavior(self):
        bv = BitVector(70)
        bv.set_range(64, 6)
        for i in range(64, 70):
            self.assertTrue(bv.get(i))
        with self.assertRaises(IndexError):
            _ = bv.get(70)

    def test_full_range_set_clear_flip(self):
        bv = BitVector(32)
        bv.set_range(0, 32)
        self.assertTrue(all(bv.get(i) for i in range(32)))

        bv.clear_range(0, 32)
        self.assertTrue(all(not bv.get(i) for i in range(32)))

        bv.flip_range(0, 32)
        self.assertTrue(all(bv.get(i) for i in range(32)))

    def test_single_bit_range(self):
        bv = BitVector(8)
        bv.set_range(3, 1)
        self.assertTrue(bv.get(3))
        bv.clear_range(3, 1)
        self.assertFalse(bv.get(3))
        bv.flip_range(3, 1)
        self.assertTrue(bv.get(3))

    def test_range_at_end(self):
        bv = BitVector(10)
        bv.set_range(8, 2)
        self.assertTrue(bv.get(8))
        self.assertTrue(bv.get(9))
        with self.assertRaises(IndexError):
            bv.set_range(9, 5)
        bv=BitVector(64)
        bv.set_range(60, 4)
        self.assertTrue(bv[63])
        bv.flip_range(0, 64)
        self.assertFalse(bv[63])
        bv.set(63)
        self.assertTrue(bv[63])
        bv.clear_range(0, 64)
        self.assertFalse(bv[63])

    def test_range_crossing_word_boundary(self):
        bv = BitVector(130)
        bv.set_range(60, 10)
        for i in range(60, 70):
            self.assertTrue(bv.get(i))
        self.assertFalse(any(bv.get(i) for i in range(0, 60)))
        self.assertFalse(any(bv.get(i) for i in range(70, 130)))

    def test_multiple_operations_consistency(self):
        bv = BitVector(16)
        bv.set_range(0, 16)
        bv.clear_range(4, 8)
        bv.flip_range(2, 10)
        for i in range(16):
            if i < 2 or i >= 12:
                self.assertTrue(bv.get(i))
            else:
                expected = (4 <= i <= 11)
                self.assertEqual(expected, bv.get(i))

    def test_out_of_bounds_negative(self):
        bv = BitVector(10)
        with self.assertRaises(ValueError):
            bv.set_range(-1, 5)
        with self.assertRaises(IndexError):
            bv.clear_range(0, 20)
        with self.assertRaises(IndexError):
            bv.flip_range(15, 1)

if __name__ == '__main__':
    unittest.main()
