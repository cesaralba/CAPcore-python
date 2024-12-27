import unittest
from time import struct_time

from src.CAPcore.LoggedDict import LoggedDict
from src.CAPcore.Misc import SetDiff


class TestLoggedDict(unittest.TestCase):
    def test_constructor1(self):
        d1 = LoggedDict()

        self.assertEqual(len(d1), 0)

    def test_constructor2(self):
        with self.assertRaises(TypeError):
            d1 = LoggedDict(exclusions=25)

    def test_set1(self):
        d1 = LoggedDict(exclusions={'a'})

        with self.assertRaises(KeyError):
            d1['a'] = 3

    def test_set_get1(self):
        d1 = LoggedDict()

        d1['b'] = 3
        v1 = d1['b']

        self.assertEqual(v1, 3)
        self.assertEqual(len(d1), 1)

    def test_set_get2(self):
        d1 = LoggedDict(exclusions={'a'})

        d1['b'] = 3
        d1['b'] = 4
        v1 = d1['b']
        self.assertEqual(v1, 4)
        self.assertEqual(len(d1), 1)

        lv1 = d1.getV('b')
        self.assertEqual(len(lv1), 2)

    def test_setget1(self):
        d1 = LoggedDict()

        d1['b'] = 3
        v1 = d1.get('b')
        v2 = d1.get('c')

        self.assertEqual(v1, 3)
        self.assertIsNone(v2)

    def test_setget2(self):
        d1 = LoggedDict()

        d1['b'] = 3
        d1.purge({'b'})
        v1 = d1.get('b', 'Deleted')
        v2 = d1.get('c', 25)

        self.assertEqual(v1, 'Deleted')
        self.assertEqual(v2, 25)

    def test_update1(self):
        data1 = {'a': 3, 'b': 4, 'c': 5}
        data2 = {'a': 4, 'b': 5, 'c': 6}
        d1 = LoggedDict(exclusions={'a'})
        r1 = d1.update(data1)
        self.assertTrue(r1)
        self.assertEqual(d1['b'], 4)
        self.assertEqual(d1['c'], 5)

        r2 = d1.update(data2)
        self.assertTrue(r2)
        self.assertEqual(d1['b'], 5)
        self.assertEqual(d1['c'], 6)
        lv1 = d1.getV('b')
        self.assertEqual(len(lv1), 2)

    def test_update2(self):
        data1 = {'a': 3, 'b': 4, 'c': 5}
        data2 = {'a': 4}
        d1 = LoggedDict(exclusions={'a'})
        d1.update(data1)
        r1 = d1.update(data2)

        self.assertFalse(r1)
        self.assertEqual(d1['b'], 4)
        self.assertEqual(d1['c'], 5)

    def test_purge1(self):
        data1 = {'a': 3, 'b': 4, 'c': 5}
        d1 = LoggedDict(exclusions={'a'})
        d1.update(data1)

        r1 = d1.purge(['c', 'a'])
        self.assertTrue(r1)

        with self.assertRaises(ValueError):
            v1 = d1['c']

    def test_purge2(self):
        data1 = {'a': 3, 'b': 4, 'c': 5}
        d1 = LoggedDict(exclusions={'a'})
        d1.update(data1)

        r1 = d1.purge(['a'])
        self.assertFalse(r1)

    def test_addExclusion1(self):
        d1 = LoggedDict()
        r1 = d1.addExclusion('c')

        self.assertEqual(len(d1.exclusions), 1)
        self.assertFalse(r1)

    def test_addExclusion2(self):
        d1 = LoggedDict()
        d1.update({'c': 25})
        r1 = d1.addExclusion({'c'})

        self.assertEqual(len(d1), 0)
        self.assertTrue(r1)

    def test_removeExclusion1(self):
        d1 = LoggedDict(exclusions={'a', 'b'})
        d1.removeExclusion('c')

        self.assertEqual(len(d1.exclusions), 2)

    def test_removeExclusion2(self):
        d1 = LoggedDict(exclusions={'a', 'b'})
        d1.removeExclusion('a')

        self.assertEqual(len(d1.exclusions), 1)

    def test_iters1(self):
        d1 = LoggedDict()
        d1.update(dict(zip('abcd', range(0, 4, 1))))

        k1 = list(d1.keys())
        i1 = list(d1.items())
        v1 = list(d1.values())

        self.assertEqual(k1, list('abcd'))
        self.assertEqual(v1, list(range(0, 4, 1)))
        self.assertEqual(i1, list(zip('abcd', range(0, 4, 1))))

    def test_iters2(self):
        d1 = LoggedDict()
        d1.update(dict(zip('abcd', range(0, 4, 1))))

        d1.purge('c')

        k1 = list(d1.keys())
        i1 = list(d1.items())
        v1 = list(d1.values())

        self.assertEqual(k1, list('abd'))
        self.assertEqual(v1, [0, 1, 3])
        self.assertEqual(i1, list(zip('abd', [0, 1, 3])))

    def test_itersV1(self):
        d1 = LoggedDict()
        d1.update(dict(zip('abcd', range(0, 4, 1))))

        k1 = list(d1.keysV())
        i1 = list(d1.itemsV())
        v1 = list(d1.valuesV())
        di1 = d1._asdict()

        self.assertEqual(k1, list('abcd'))
        self.assertEqual(v1, list(range(0, 4, 1)))
        self.assertEqual(i1, list(zip('abcd', range(0, 4, 1))))
        self.assertEqual(di1, dict(zip('abcd', range(0, 4, 1))))

    def test_itersV2(self):
        d1 = LoggedDict()
        d1.update(dict(zip('abcd', range(0, 4, 1))))

        d1.purge('c')

        k1 = list(d1.keysV())
        i1 = list(d1.itemsV())
        v1 = list(["DELETED" if v.isDeleted() else v.get() for v in d1.valuesV()])
        di1 = d1._asdict()

        numDeleted = sum([1 if v.isDeleted() else 0 for v in d1.valuesV()])

        self.assertEqual(k1, list('abcd'))
        self.assertEqual(v1, [0, 1, "DELETED", 3])
        self.assertEqual(numDeleted, 1)
        self.assertEqual(di1, dict(zip('abd', [0, 1, 3])))

    def test_replace1(self):
        di1 = {'a': 1, 'b': 2, 'c': 3}
        di2 = {'b': 2, 'c': 4, 'd': 5}

        d1 = LoggedDict()
        d1.update(di1)
        r1 = d1.replace(di2)

        k1 = list(d1.keys())
        kV1 = list(d1.keysV())
        rd1 = d1._asdict()
        rd2 = dict(d1.itemsV())

        self.assertTrue(r1)
        self.assertDictEqual(rd1, di2)
        self.assertEqual(len(k1), 3)
        self.assertEqual(len(kV1), 4)
        self.assertTrue(rd2['a'].isDeleted())
        self.assertEqual(len(rd2['b']), 1)
        self.assertEqual(len(rd2['c']), 2)

    def test_replace2(self):
        di1 = {'a': 1, 'b': 2, 'c': 3}
        di2 = {'b': 2, 'c': 4, 'd': 5}

        d1 = LoggedDict()
        d1.update(di1)
        d2 = LoggedDict()
        d2.update(di2)
        r1 = d1.replace(d2)

        k1 = list(d1.keys())
        kV1 = list(d1.keysV())
        rd1 = d1._asdict()
        rd2 = dict(d1.itemsV())
        self.assertTrue(r1)
        self.assertDictEqual(rd1, d2._asdict())
        self.assertEqual(len(k1), 3)
        self.assertEqual(len(kV1), 4)
        self.assertTrue(rd2['a'].isDeleted())
        self.assertEqual(len(rd2['b']), 1)
        self.assertEqual(len(rd2['c']), 2)

    def test_replace3(self):
        di1 = {'a': 1, 'b': 2, 'c': 3}

        d1 = LoggedDict()
        d1.update(di1)

        with self.assertRaises(TypeError):
            d1.replace(5)

    def test_replace4(self):
        di1 = {'a': 1, 'b': 2, 'c': 3}
        di2 = {'b': 2, 'c': 4, 'd': 5, 'e': 7}

        d1 = LoggedDict(exclusions={'e'})
        d1.update(di1)
        r1 = d1.replace(di2)

        k1 = list(d1.keys())
        kV1 = list(d1.keysV())
        rd1 = d1._asdict()
        rd2 = dict(d1.itemsV())
        self.assertTrue(r1)
        self.assertDictEqual(rd1, {'b': 2, 'c': 4, 'd': 5})
        self.assertEqual(len(k1), 3)
        self.assertEqual(len(kV1), 4)
        self.assertTrue(rd2['a'].isDeleted())
        self.assertEqual(len(rd2['b']), 1)
        self.assertEqual(len(rd2['c']), 2)

    def test_compareKeys1(self):
        di1 = {'a': 1, 'b': 2, 'c': 3}
        di2 = {'b': 2, 'c': 4, 'd': 5}

        exp11 = SetDiff(shared={'a', 'b', 'c'})
        exp12 = SetDiff(missing={'a'}, shared={'b', 'c'}, new={'d'})

        d1 = LoggedDict()
        d1.update(di1)
        d2 = LoggedDict()
        d2.update(di2)

        r1D1 = d1.compareWithOtherKeys(d1)
        r1d1 = d1.compareWithOtherKeys(di1)
        r1D2 = d1.compareWithOtherKeys(d2)
        r1d2 = d1.compareWithOtherKeys(di2)

        with self.assertRaises(TypeError):
            d1.compareWithOtherKeys(5)

        self.assertEqual(r1D1, exp11)
        self.assertEqual(r1d1, exp11)
        self.assertEqual(r1D2, exp12)
        self.assertEqual(r1d2, exp12)

    def test_compare1(self):
        di1 = {'a': 1, 'b': 2, 'c': 3}

        d1 = LoggedDict()
        d1.update(di1)

        dif1 = d1.diff(di1)

        self.assertFalse(dif1)
        self.assertEqual(repr(dif1), "")

    def test_compare2(self):
        di1 = {'a': 1, 'b': 2, 'c': 3}

        d1 = LoggedDict()
        d1.update(di1)
        d2 = LoggedDict()
        d2.update(di1)

        dif1 = d1.diff(d2)

        self.assertEqual(d1, d2)
        self.assertEqual(d1, di1)
        self.assertFalse(dif1)

    def test_compare3(self):
        di1 = {'a': 1, 'b': 2, 'c': 3}

        d1 = LoggedDict()
        d1.update(di1)

        with self.assertRaises(TypeError):
            d1.diff(5)

    def test_compare4(self):
        di1 = {'a': 1, 'b': 2, 'c': 3}
        di2 = {'b': 2, 'c': 3, 'd': 5}

        d1 = LoggedDict()
        d1.addExclusion('d', 'a')
        d1.update(di1)

        dif1 = d1.diff(di2)

        self.assertFalse(dif1)

    def test_compare5(self):
        """
        'a' doesn't show in di2, 'd' is ignored -> Different

        """
        di1 = {'a': 1, 'b': 2, 'c': 3}
        di2 = {'b': 2, 'c': 3, 'd': 5}
        expStr = "'a': D '1'"
        d1 = LoggedDict()
        d1.addExclusion('d')
        d1.update(di1)

        dif1 = d1.diff(di2)

        self.assertTrue(dif1)
        self.assertNotEqual(d1, di2)
        self.assertEqual(repr(dif1), expStr)

    def test_compare6(self):
        di1 = {'a': 1, 'b': 2, 'c': 3}
        di2 = {'b': 2, 'c': 4, 'd': 5}
        expStr = "'c': C '3' -> '4'"

        d1 = LoggedDict()
        d1.addExclusion('d', 'a')
        d1.update(di1)

        dif1 = d1.diff(di2)

        self.assertTrue(dif1)
        self.assertEqual(repr(dif1), expStr)

    def test_compare8(self):
        di1 = {'a': 1, 'b': 2, 'c': 3}
        di2 = {'b': 2, 'c': 3, 'd': 5}
        expStr = "'d': A '5'"

        d1 = LoggedDict()
        d1.addExclusion('a')
        d1.update(di1)

        dif1 = d1.diff(di2)

        self.assertTrue(dif1)
        self.assertEqual(repr(dif1), expStr)

    def test_compare9(self):
        di1 = {'a': 1, 'b': 2, 'c': 3}
        di2 = {'b': 2, 'c': 3, 'd': 5}
        expStr = "'a': D '1', 'd': A '5'"

        d1 = LoggedDict()
        d1.update(di1)

        dif1 = d1.diff(di2)

        self.assertTrue(dif1)
        self.assertEqual(repr(dif1), expStr)
        self.assertEqual(len(dif1), 2)

    def test_compare10(self):
        di1 = {'a': 1, 'b': 2, 'c': 3}
        di2 = {'b': 2, 'c': 3, 'd': 5}
        expStr = "'a': D '1', 'd': A '5'"

        d1 = LoggedDict()
        d1.update(di1)
        d2 = LoggedDict()
        d2.update(di2)

        dif1 = d1.diff(d2)

        self.assertTrue(dif1)
        self.assertNotEqual(d1, d2)
        self.assertNotEqual(d1, di2)
        self.assertEqual(repr(dif1), expStr)
        self.assertEqual(len(dif1), 2)

    def test_show1(self):
        time1 = struct_time((2024, 12, 13, 23, 4, 34, 4, 348, 0))
        time2 = struct_time((2024, 12, 13, 23, 4, 44, 4, 348, 0))

        di1 = {'a': 1, 'b': 2}

        expStr1 = "{'a': None [t:2024-12-13 23:04:44+0000 D l:2], 'b': 2 [t:2024-12-13 23:04:34+0000 l:1]}"
        expStr2 = "{ 'a': None [t:2024-12-13 23:04:44+0000 D l:2],\n  'b': 2 [t:2024-12-13 23:04:34+0000 l:1]\n}"

        d1 = LoggedDict()
        d1.update(di1, timestamp=time1)
        d1.purge('a', timestamp=time2)

        self.assertEqual(repr(d1), expStr1)
        self.assertEqual(d1.show(compact=True), expStr1)
        self.assertEqual(d1.show(compact=False), expStr2)

    def test_show2(self):
        d1 = LoggedDict()
        expStr1 = "{}"

        self.assertEqual(repr(d1), expStr1)
