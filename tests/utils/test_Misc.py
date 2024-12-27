import unittest

from src.CAPcore.Misc import removeSuffix


class TestRemoveSuffix(unittest.TestCase):
    def test_badParamsBoth(self):
        self.assertRaisesRegex(TypeError, r"^removeSuffix: one or both parameters are not a str.*", removeSuffix, None,
                               None)

    def test_badParamsFirst(self):
        self.assertRaisesRegex(TypeError, r"^removeSuffix: one or both parameters are not a str.*", removeSuffix, 1,
                               "aaa")

    def test_badParamsSecond(self):
        self.assertRaisesRegex(TypeError, r"^removeSuffix: one or both parameters are not a str.*", removeSuffix, "aaa",
                               (3,))

        self.assertRaisesRegex(TypeError, r"^removeSuffix: one or both parameters are not a str.*")

    def test_remove_Suffix_noSuffix(self):
        d1 = removeSuffix('a123', '4')
        self.assertEqual(d1, 'a123')

        d1 = removeSuffix('a123', '3')
        self.assertEqual(d1, 'a12')

        d1 = removeSuffix('a123', '23')
        self.assertEqual(d1, 'a1')

        d1 = removeSuffix('a1233', '3')
        self.assertEqual(d1, 'a123')
