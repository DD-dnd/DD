import io
import unittest
from unittest.mock import patch

from calculator import Inputs, calc_3ph, calc_rectifier, lookup_last_leq, CB_TABLE, WIRE_TABLE, main


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

    def test_missing_args_returns_help_error(self):
        with patch("sys.stdout", new=io.StringIO()) as fake:
            rc = main(["rectifier", "--vdc", "600"])
        self.assertEqual(rc, 2)
        self.assertIn("missing required arguments", fake.getvalue())


if __name__ == "__main__":
    unittest.main()
