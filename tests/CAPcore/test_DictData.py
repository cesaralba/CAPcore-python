import unittest
from time import struct_time

from src.CAPcore.DictLoggedDict import DictOfLoggedDict, LoggedDict, DictData


class TestDictData(unittest.TestCase):
    def test_DDrestore1(self):
        d1 = DictOfLoggedDict()
        dAux1 = {'a1': 1, 'a2': 'ce'}
        di1 = {'a': dAux1, 'b': dAux1, 'c': dAux1}

        d1.update(newValues=di1)
        k0 = list(d1.keys())
        r1 = d1.purge('a')
        k1 = list(d1.keys())
        r2 = d1.update(di1)
        k2 = list(d1.keys())

        self.assertTrue(r1)
        self.assertTrue(r2)
        self.assertEqual(len(k0), 3)
        self.assertEqual(len(k1), 2)
        self.assertEqual(len(k2), 3)

    def test_DDrestore2(self):
        d1 = DictOfLoggedDict()
        dAux1 = {'a1': 1, 'a2': 'ce'}
        di1 = {'a': dAux1, 'b': dAux1}

        d1.update(newValues=di1)
        r2 = d1.getV('b').restore()
        self.assertFalse(r2)

    def test_DDshowV1(self):
        time0 = struct_time((2024, 12, 13, 23, 4, 24, 4, 348, 0))
        time1 = struct_time((2024, 12, 13, 23, 4, 34, 4, 348, 0))
        time2 = struct_time((2024, 12, 13, 23, 4, 44, 4, 348, 0))

        res1 = {'a': "{'a1': 1 [t:2024-12-13 23:04:34+0000 l:1], 'a2': 'ce' [t:2024-12-13 23:04:34+0000 l:1]} ("
                     "t:2024-12-13 23:04:44+0000 D l:3)",
                'b': "{'a1': 1 [t:2024-12-13 23:04:34+0000 l:1], 'a2': 'ce' [t:2024-12-13 23:04:34+0000 l:1]} ("
                     "t:2024-12-13 23:04:34+0000 l:2)"}

        d1 = DictOfLoggedDict(timestamp=time0)
        dAux1 = {'a1': 1, 'a2': 'ce'}
        di1 = {'a': dAux1, 'b': dAux1}

        d1.update(newValues=di1, timestamp=time1)
        d1.purge('a', timestamp=time2)

        r1 = {k: v.showV() for k, v in d1.itemsV()}
        r2 = {k: repr(v) for k, v in d1.itemsV()}

        self.assertDictEqual(r1, res1)
        self.assertDictEqual(r2, res1)

    def test_BuildFromLD(self):
        di1 = {'a': 1, 'b': 2, 'c': 3}

        d1 = LoggedDict()
        d1.update(di1)
        d2 = DictData()
        d2.update(di1)

        r2 = DictData.fromLoggedDict(d2)
        r3 = DictData.fromLoggedDict(d1)

        with self.assertRaises(TypeError):
            DictData.fromLoggedDict(25)

        self.assertIs(r2, d2)

        self.assertIsInstance(r3, DictData)
        self.assertIsInstance(r3, LoggedDict)
