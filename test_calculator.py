


class TestCalculator(unittest.TestCase):
    def test_lookup_tables(self):
        self.assertEqual(lookup_last_leq(64, CB_TABLE), "70")
        self.assertEqual(lookup_last_leq(121, WIRE_TABLE), "#2")

    def test_rectifier_baseline(self):
        out = calc_rectifier(Inputs(vdc=600, idc=600, vpri=480))
        self.assertAlmostEqual(out.kva, 484, places=0)
        self.assertEqual(out.cb_primary, "800")
        self.assertEqual(out.wire_dc, "300MCM 2x")

    def test_3ph_baseline(self):
        out = calc_3ph(Inputs(vdc=600, idc=600, vpri=480))
        self.assertAlmostEqual(out.kva, 484, places=0)
        self.assertEqual(out.cb_secondary, "800")



if __name__ == "__main__":
    unittest.main()
