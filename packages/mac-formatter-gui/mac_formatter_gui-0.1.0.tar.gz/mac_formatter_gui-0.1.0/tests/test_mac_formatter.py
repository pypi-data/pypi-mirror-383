import unittest

from mac_formatter.app import clean_mac, is_valid_mac12, format_mac


class TestCleanMac(unittest.TestCase):
    def test_various_inputs(self):
        cases = [
            ("", ""),
            (None, ""),
            ("aabb.ccdd.eeff", "aabbccddeeff"),
            ("AA:BB:CC:DD:EE:FF", "AABBCCDDEEFF"),
            ("aa-bb-cc-dd-ee-ff", "aabbccddeeff"),
            ("ZZAABBCCDDEEFF", "AABBCCDDEEFF"),  # non-hex letters stripped
            ("12 34 56 78 9A BC", "123456789ABC"),
            ("g1:h2:i3:j4:k5:l6", "123456"),  # letters removed, digits remain
        ]
        for inp, expected in cases:
            with self.subTest(inp=inp):
                self.assertEqual(clean_mac(inp), expected)


class TestIsValidMac12(unittest.TestCase):
    def test_validity(self):
        cases = [
            ("AABBCCDDEEFF", True),
            ("aabbccddeeff", True),
            ("AABBCCDDEEF", False),   # 11
            ("AABBCCDDEEFF0", False), # 13
            ("AABBCCDDEEFG", False),  # G invalid
            ("", False),
            (None, False),
        ]
        for s, valid in cases:
            with self.subTest(s=s):
                s2 = "" if s is None else s
                self.assertIs(is_valid_mac12(s2), valid)


class TestFormatMac(unittest.TestCase):
    def test_valid_formats(self):
        cases = [
            ("aabbccddeeff", ":", "upper", "AA:BB:CC:DD:EE:FF"),
            ("aabbccddeeff", "-", "upper", "AA-BB-CC-DD-EE-FF"),
            ("AABBCCDDEEFF", ".", "upper", "AABB.CCDD.EEFF"),
            ("AABBCCDDEEFF", ":", "lower", "aa:bb:cc:dd:ee:ff"),
            ("AABBCCDDEEFF", "-", "lower", "aa-bb-cc-dd-ee-ff"),
            ("AABBCCDDEEFF", ".", "lower", "aabb.ccdd.eeff"),
            ("AABBCCDDEEFF", "unknown", "upper", "AA:BB:CC:DD:EE:FF"),
        ]
        for hex_only, style, case, expected in cases:
            with self.subTest(hex_only=hex_only, style=style, case=case):
                self.assertEqual(format_mac(hex_only, style=style, case=case), expected)

    def test_invalid_returns_empty(self):
        self.assertEqual(format_mac("AABBCCDDEE", ":"), "")  # too short
        self.assertEqual(format_mac("AABBCCDDEEFF00", ":"), "")  # too long
        self.assertEqual(format_mac("AABBCCDDEEFG", ":"), "")  # invalid char


if __name__ == "__main__":
    unittest.main()
