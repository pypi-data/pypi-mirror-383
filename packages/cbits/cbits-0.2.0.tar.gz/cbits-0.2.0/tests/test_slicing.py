import unittest
from cbits import BitVector

class TestSlicing(unittest.TestCase):
    def setUp(self):
        self.bv = BitVector(10)
        for i in range(10):
            if i % 2 == 0:
                self.bv.set(i)

    def test_basic_slice(self):
        sv = self.bv[2:7]
        self.assertIsInstance(sv, BitVector)
        self.assertEqual(5, len(sv))
        expected = [self.bv.get(i) for i in range(2, 7)]
        self.assertEqual(expected, [sv.get(i) for i in range(len(sv))])

    def test_slice_default_bounds(self):
        full = self.bv[:]
        self.assertEqual(len(self.bv), len(full))
        self.assertEqual([self.bv.get(i) for i in range(10)],
                         [full.get(i) for i in range(10)])
        prefix = self.bv[:5]
        self.assertEqual(5, len(prefix))
        suffix = self.bv[5:]
        self.assertEqual(5, len(suffix))

    def test_negative_indices_slice(self):
        sv = self.bv[-8:-2]
        expected = [self.bv.get(i) for i in range(2, 8)]
        self.assertEqual(expected, [sv.get(i) for i in range(len(sv))])

    def test_step_slices(self):
        sv = self.bv[1:9:2]
        self.assertEqual(4, len(sv))
        expected = [self.bv.get(i) for i in range(1, 9, 2)]
        self.assertEqual(expected, [sv.get(i) for i in range(len(sv))])

        single = self.bv[0:3:5]
        self.assertEqual(1, len(single))
        self.assertEqual(self.bv.get(0), single.get(0))

    def test_negative_step_slice(self):
        rv = self.bv[::-1]
        self.assertEqual(len(self.bv), len(rv))
        for i in range(len(rv)):
            self.assertEqual(self.bv.get(9 - i), rv.get(i))

        mid = self.bv[8:2:-2]
        expected = [self.bv.get(i) for i in (8,6,4)]
        self.assertEqual(expected, [mid.get(i) for i in range(len(mid))])

    def test_zero_step_slice_error(self):
        with self.assertRaises(ValueError):
            _ = self.bv[1:5:0]
        with self.assertRaises(ValueError):
            self.bv[::0] = BitVector(10)

    def test_empty_slice(self):
        empty = self.bv[3:3]
        self.assertIsInstance(empty, BitVector)
        self.assertEqual(0, len(empty))
        self.assertEqual([], list(iter(empty)))

    def test_slice_assignment_basic(self):
        new_piece = BitVector(4)
        for i in range(4):
            new_piece.set(i)
        self.bv[1:5] = new_piece
        for i in range(1, 5):
            self.assertTrue(self.bv.get(i))

    def test_slice_assignment_with_step(self):
        target = BitVector(3)
        for i in range(3):
            target.set(i)

        self.bv[0:6:2] = target
        for _, bv_idx in enumerate(range(0,6,2)):
            self.assertTrue(self.bv.get(bv_idx))

    def test_slice_assignment_length_mismatch(self):
        too_long = BitVector(5)
        with self.assertRaises(ValueError):
            self.bv[1:4] = too_long

        too_short = BitVector(1)
        with self.assertRaises(ValueError):
            self.bv[0:6:2] = too_short

    def test_slice_out_of_bounds(self):
        sv = self.bv[-100:100]
        self.assertEqual(len(self.bv), len(sv))
        self.assertEqual([self.bv.get(i) for i in range(10)],
                         [sv.get(i) for i in range(10)])

        patch = BitVector(10)
        for i in range(10):
            patch.set(i)

        self.bv[-100:100] = patch
        self.assertTrue(all(self.bv.get(i) for i in range(10)))

    def test_slice_assignment_list_tuple_generator(self):
        self.bv[0:3] = [True, False, True]
        self.assertTrue(self.bv.get(0))
        self.assertFalse(self.bv.get(1))
        self.assertTrue(self.bv.get(2))

        self.bv[3:6] = (False, True, False)
        self.assertFalse(self.bv.get(3))
        self.assertTrue(self.bv.get(4))
        self.assertFalse(self.bv.get(5))

        self.bv[6:10] = (i % 2 != 0 for i in range(4))
        expected = [False, True, False, True]
        for offset, idx in enumerate(range(6, 10)):
            self.assertEqual(expected[offset], self.bv.get(idx))

    def test_slice_assignment_negative_step(self):
        seq = [True, False, True, False]
        self.bv[9:5:-1] = seq
        indices = list(range(9, 5, -1))
        for bit, idx in zip(seq, indices):
            self.assertEqual(bit, self.bv.get(idx))

    def test_slice_assignment_invalid_non_iterable(self):
        with self.assertRaises(TypeError):
            self.bv[0:3] = 123

    def test_slice_assignment_zero_length_assign(self):
        orig = BitVector(5)
        orig.set(2)

        orig[3:3] = []
        self.assertTrue(orig.get(2))
        orig[3:3] = ()
        self.assertTrue(orig.get(2))

    def test_slice_assignment_out_of_bounds_behavior(self):
        orig = BitVector(5)
        orig.set(0)
        orig.set(4)

        orig[10:20] = []
        self.assertTrue(orig.get(0))
        self.assertTrue(orig.get(4))

        with self.assertRaises(ValueError):
            orig[10:20] = [True]

    def test_slice_assignment_step_length_mismatch(self):
        with self.assertRaises(ValueError):
            self.bv[0:6:3] = [True]
        with self.assertRaises(ValueError):
            self.bv[0:6:3] = [True, True, False]

        with self.assertRaises(ValueError):
            self.bv[9:5:-1] = [True, False]

    def test_slice_assignment_boolean_int_values(self):
        self.bv[1:4] = [1, 0, 1]
        self.assertTrue(self.bv.get(1))
        self.assertFalse(self.bv.get(2))
        self.assertTrue(self.bv.get(3))

if __name__ == '__main__':
    unittest.main()
