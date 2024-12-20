import unittest

from src.CAPcore.LoggedValue import LoggedValue
from time import struct_time

class Test_LoggedValue(unittest.TestCase):
    def test_constructor1(self):
        v1 = LoggedValue()
        v1.get()

        self.assertEqual(len(v1), 0)
        self.assertIsNone(v1.get())

    def test_constructor2(self):
        v1 = LoggedValue(5)

        self.assertEqual(len(v1), 1)
        self.assertEqual(v1.get(), 5)

    def test_clear1(self):
        v1 = LoggedValue()
        r1=v1.clear()

        self.assertEqual(len(v1), 1)
        self.assertTrue(v1.deleted)
        self.assertTrue(r1)
        with self.assertRaises(ValueError):
            v1.get()

    def test_clear2(self):
        v1 = LoggedValue(5)
        r1=v1.clear()

        self.assertEqual(len(v1), 2)
        self.assertTrue(v1.deleted)
        self.assertTrue(r1)
        with self.assertRaises(ValueError):
            v1.get()

    def test_clear3(self):
        v1 = LoggedValue(5)
        r1=v1.clear()
        r2=v1.clear()

        self.assertEqual(len(v1), 2)
        self.assertTrue(v1.deleted)
        self.assertTrue(r1)
        self.assertFalse(r2)
        with self.assertRaises(ValueError):
            v1.get()

    def test_set1(self):
        v1 = LoggedValue(5)
        r1 = v1.set(4)

        self.assertEqual(len(v1), 2)
        self.assertEqual(v1.get(), 4)
        self.assertTrue(r1)

    def test_set2(self):
        v1 = LoggedValue(5)
        r1 = v1.set(5)

        self.assertEqual(len(v1), 1)
        self.assertEqual(v1.get(), 5)
        self.assertFalse(r1)

    def test_set3(self):
        v1 = LoggedValue(5)
        v1.clear()
        r1 = v1.set(5)

        self.assertEqual(len(v1), 3)
        self.assertEqual(v1.get(), 5)
        self.assertTrue(r1)

    def test_set4(self):
        v1 = LoggedValue(5)
        v1.clear()
        r1 = v1.set(None)

        self.assertEqual(len(v1), 3)
        self.assertIsNone(v1.get())
        self.assertTrue(r1)

    def test_set5(self):
        v1 = LoggedValue(5)
        v1.clear()
        v1.set(None)
        r1 = v1.set(None)

        self.assertEqual(len(v1), 3)
        self.assertIsNone(v1.get())
        self.assertFalse(r1)

    def test_set6(self):
        time1 = struct_time((2024, 12, 13, 23, 4, 44, 4, 348, 0))
        time2 = struct_time((2024, 12, 13, 23, 4, 34, 4, 348, 0))
        v1 = LoggedValue(v=5,timestamp=time1)

        with self.assertRaises(ValueError):
            v1.set(v=6,timestamp=time2)

    def test_eq1(self):
        v1=LoggedValue(5)
        v2=LoggedValue(5)

        self.assertEqual(v1,v2)

    def test_eq2(self):
        v1=LoggedValue(5)
        v2=5

        self.assertEqual(v1,v2)

    def test_eq3(self):
        v1=LoggedValue()
        v2=LoggedValue()

        self.assertEqual(v1,v2)

    def test_eq4(self):
        v1=LoggedValue()
        v2=None

        self.assertEqual(v1,v2)

    def test_eq5(self):
        v1=LoggedValue(5)
        v2=None

        self.assertNotEqual(v1,v2)

    def test_eq6(self):
        v1=LoggedValue()
        v2=5

        self.assertNotEqual(v1,v2)

    def test_eq8(self):
        v1=LoggedValue()
        v1.clear()
        v2=5

        self.assertNotEqual(v1,v2)

    # def test_eq9(self):
    #     v1=LoggedValue()
    #     v1.clear()
    #     v2=None
    #
    #     self.assertNotEqual(v1,v2)

    def test_repr1(self):
        time1 = struct_time((2024, 12, 13, 23, 4, 34, 4, 348, 0))
        time2 = struct_time((2024, 12, 13, 23, 4, 44, 4, 348, 0))
        time3 = struct_time((2024, 12, 13, 23, 4, 54, 4, 348, 0))

        v1 = LoggedValue(v=5,timestamp=time1)
        self.assertEqual(repr(v1),'5 [t:2024-12-13 23:04:34+0000 l:1]')
        v1.set(6,timestamp=time2)
        self.assertEqual(repr(v1),'6 [t:2024-12-13 23:04:44+0000 l:2]')
        v1.clear(timestamp=time3)
        self.assertEqual(repr(v1),'None [t:2024-12-13 23:04:54+0000 D l:3]')

    def test_repr2(self):
        time1 = struct_time((2024, 12, 13, 23, 4, 34, 4, 348, 0))

        v1 = LoggedValue(timestamp=time1)
        self.assertEqual(repr(v1),'None [t:2024-12-13 23:04:34+0000 l:0]')
