import unittest
from time import struct_time

from src.CAPcore.DictLoggedDict import DictOfLoggedDict, DictData
from src.CAPcore.LoggedDict import LoggedDict
from src.CAPcore.Misc import SetDiff


class TestDictLoggedDict(unittest.TestCase):
    def test_constructor1(self):
        d1 = DictOfLoggedDict()

        self.assertEqual(len(d1), 0)
        self.assertEqual(len(d1.exclusions), 0)

    def test_constructor2(self):
        with self.assertRaises(TypeError):
            DictOfLoggedDict(exclusions=25)

    def test_constructor3(self):
        d1 = DictOfLoggedDict(exclusions={'a'})
        self.assertEqual(len(d1.exclusions), 1)

    def test_setItem1(self):
        d1 = DictOfLoggedDict()
        dAux1 = {'a1': 1, 'a2': 'ce'}
        dAux2 = {'a1': 1, 'a2': 'de'}
        di1 = {'a': dAux1}

        d1.update(newValues=di1)
        LH1 = len(d1.history)
        LD1 = LoggedDict()
        LD1.update(dAux1)
        DD1 = DictData()
        DD1.update(dAux1)

        d1['a'] = LD1
        self.assertEqual(len(d1.history), LH1)

        d1['a'] = DD1
        self.assertEqual(len(d1.history), LH1)

        d1['a'] = dAux1
        self.assertEqual(len(d1.history), LH1)

        d1['a'] = dAux2
        self.assertEqual(len(d1.history), LH1 + 1)

    def test_update1(self):
        d1 = DictOfLoggedDict()
        dAux1 = {'a1': 1, 'a2': 'ce'}
        di1 = {'a': dAux1}

        r1 = d1.update(newValues=di1)
        r2 = d1.update(newValues=di1)
        v1 = d1.get('a')

        self.assertTrue(r1)
        self.assertFalse(r2)
        self.assertDictEqual(v1, dAux1)

    def test_update2(self):
        d1 = DictOfLoggedDict(exclusions={'a1'})
        dAux1 = {'a2': 'ce'}
        dAux2 = {'a1': 1}
        dAux2.update(dAux1)
        di1 = {'a': dAux2}

        r1 = d1.update(newValues=di1)
        v1 = d1.get('a')

        self.assertTrue(r1)
        self.assertDictEqual(v1, dAux1)

    def test_update3(self):
        d1 = DictOfLoggedDict()

        with self.assertRaises(TypeError):
            d1.update(newValues=5)

    def test_update4(self):
        d1 = DictOfLoggedDict()
        dAux1 = {'a1': 1, 'a2': 'ce'}
        di1 = {'a': dAux1, 'b': dAux1}

        d1.update(newValues=di1)
        r1 = d1.purge('a')
        rd1 = d1._asdict()
        v1 = d1['b']
        self.assertTrue(r1)
        self.assertDictEqual(rd1, {'b': dAux1})
        with self.assertRaises(KeyError):
            print(d1['a'])
        with self.assertRaises(KeyError):
            d1.get('a')

        self.assertDictEqual(v1, dAux1)

    def test_update5(self):
        d1 = DictOfLoggedDict()
        dAux1 = {'a1': 1, 'a2': 'ce'}
        di1 = {'a': dAux1, 'b': dAux1}

        d1.update(newValues=di1)
        d1.purge('a')

        with self.assertRaises(ValueError):
            d1.getV('a').update(dAux1)

        with self.assertRaises(ValueError):
            d1.current['a'].update(dAux1)

    def test_iters1(self):
        d1 = DictOfLoggedDict()
        dAux1 = {'a1': 1, 'a2': 'ce'}
        di1 = {'a': dAux1, 'b': dAux1}

        d1.update(newValues=di1)

        k1 = set(d1.keys())
        i1 = dict(d1.items())
        v1 = list(d1.values())

        self.assertSetEqual(k1, {'a', 'b'})
        self.assertDictEqual(i1, di1)
        self.assertListEqual(v1, [dAux1, dAux1])

    def test_iters2(self):
        d1 = DictOfLoggedDict()
        dAux1 = {'a1': 1, 'a2': 'ce'}
        di1 = {'a': dAux1, 'b': dAux1}

        d1.update(newValues=di1)
        d1.purge('a')

        k1 = set(d1.keys())
        i1 = dict(d1.items())
        v1 = list(d1.values())

        self.assertSetEqual(k1, {'b'})
        self.assertDictEqual(i1, {'b': dAux1})
        self.assertListEqual(v1, [dAux1])

    def test_itersV1(self):
        d1 = DictOfLoggedDict()
        dAux1 = {'a1': 1, 'a2': 'ce'}
        di1 = {'a': dAux1, 'b': dAux1}

        d1.update(newValues=di1)

        k1 = set(d1.keysV())
        i1 = dict(d1.itemsV())
        v1 = list(d1.valuesV())

        self.assertSetEqual(k1, {'a', 'b'})
        self.assertDictEqual(i1, di1)
        self.assertListEqual(v1, [dAux1, dAux1])

    def test_itersV2(self):
        d1 = DictOfLoggedDict()
        dAux1 = {'a1': 1, 'a2': 'ce'}
        di1 = {'a': dAux1, 'b': dAux1}
        di2 = {'a': True, 'b': False}

        d1.update(newValues=di1)
        d1.purge('a')

        k1 = set(d1.keysV())
        auxDel1 = {k: v.isDeleted() for k, v in d1.itemsV()}
        l1 = list(d1.valuesV())

        self.assertSetEqual(k1, {'a', 'b'})
        self.assertDictEqual(auxDel1, di2)

        with self.assertRaises(ValueError):
            l1[0].get('a1')

    def test_purge1(self):
        d1 = DictOfLoggedDict()
        dAux1 = {'a1': 1, 'a2': 'ce'}
        di1 = {'a': dAux1, 'b': dAux1, 'c': dAux1, 'ca': dAux1}

        d1.update(newValues=di1)
        r1 = d1.purge('a')
        r2 = d1.purge('a', 'b', 'ca', 'x')
        r3 = d1.purge('a', 'x')

        self.assertTrue(r1)
        self.assertTrue(r2)
        self.assertFalse(r3)
        self.assertEqual(len(d1), 1)
        self.assertNotIn('ca', d1)

    def test_getitem(self):
        d1 = DictOfLoggedDict()

        with self.assertRaises(KeyError):
            print(d1['a'])

    def test_setitem(self):
        d1 = DictOfLoggedDict()
        dAux1 = {'a1': 1, 'a2': 'ce'}
        d1['a'] = dAux1
        v1 = d1['a']

        self.assertDictEqual(v1, dAux1)

    def test_get(self):
        d1 = DictOfLoggedDict()
        dAux1 = {'a1': 1, 'a2': 'ce'}
        d1['a'] = dAux1

        with self.assertRaises(KeyError):
            print(d1.get('d'))

    def test_getV(self):
        d1 = DictOfLoggedDict()
        dAux1 = {'a1': 1, 'a2': 'ce'}
        d1['a'] = dAux1
        d1['b'] = dAux1
        d1.purge('b')
        v1 = d1.getV('a')
        v2 = d1.getV('b')

        self.assertFalse(v1.isDeleted())
        self.assertDictEqual(v1._asdict(), dAux1)

        self.assertTrue(v2.isDeleted())

        with self.assertRaises(KeyError):
            v1 = d1.getV('d')

    def test_pop(self):
        d1 = DictOfLoggedDict()
        dAux1 = {'a1': 1, 'a2': 'ce'}
        d1['a'] = dAux1
        d1['b'] = dAux1
        d1.purge('b')

        v1 = d1.pop('a')
        v2 = d1.pop('b', 25)

        self.assertDictEqual(v1, dAux1)
        self.assertEqual(v2, 25)

        with self.assertRaises(KeyError):
            print(d1.pop('d'))

        with self.assertRaises(KeyError):
            print(d1.pop('b'))

    def test_addExclusion(self):
        d1 = DictOfLoggedDict()
        dAux1 = {'a1': 1, 'a2': 'ce'}
        di1 = {'a': dAux1, 'b': dAux1, 'c': dAux1}
        d1.update(di1)
        d1.purge('c')

        r1 = d1.addExclusion({'a1'})
        r2 = d1.addExclusion({'a3'})
        v1 = d1['a']
        self.assertTrue(r1)
        self.assertFalse(r2)
        self.assertDictEqual(v1, {'a2': 'ce'})

    def test_removeExcls(self):
        d1 = DictOfLoggedDict({'a3', 'a4'})
        dAux1 = {'a1': 1, 'a2': 'ce'}
        di1 = {'a': dAux1, 'b': dAux1, 'c': dAux1}
        d1.update(di1)
        d1.purge('c')

        d1.removeExclusion({'a3'})
        lenExcls = [len(v.exclusions) for v in d1.valuesV()]
        checkRemoved = [('a3' in v.exclusions) for v in d1.valuesV()]

        self.assertListEqual(lenExcls, [1, 1, 2])
        self.assertListEqual(checkRemoved, [False, False, True])

    def test_subKeys(self):
        d1 = DictOfLoggedDict()
        dAux1 = {'a1': 1, 'a2': 'ce'}
        di1 = {'a': dAux1, 'b': dAux1, 'c': dAux1}
        di2 = {'b': {'b1': 2, 'b2': 3}}
        di3 = {'c': {'c1': 2, 'c2': 3}}

        d1.update(di1)
        sk1 = d1.subkeys()
        d1.update(di2)
        sk2 = d1.subkeys()
        d1.update(di3)
        sk3 = d1.subkeys()
        d1.purge('b')
        sk4 = d1.subkeys()

        self.assertSetEqual(sk1, {'a1', 'a2'})
        self.assertSetEqual(sk2, {'a1', 'a2', 'b1', 'b2'})
        self.assertSetEqual(sk3, {'a1', 'a2', 'b1', 'b2', 'c1', 'c2'})
        self.assertSetEqual(sk4, {'a1', 'a2', 'c1', 'c2'})

    def test_diff1(self):
        d1 = DictOfLoggedDict()
        dAux1 = {'a1': 1, 'a2': 'ce'}
        di1 = {'a': dAux1, 'b': dAux1, 'c': dAux1}

        d1.update(di1)

        with self.assertRaises(TypeError):
            d1.diff(25)

    def test_diff2(self):
        d1 = DictOfLoggedDict()
        d2 = DictOfLoggedDict()

        dAux1 = {'a1': 1, 'a2': 'ce'}
        di1 = {'a': dAux1, 'b': dAux1, 'c': dAux1}

        d1.update(di1)
        d2.update(di1)

        r1 = d1.diff(d1)
        r2 = d1.diff(di1)
        r3 = d1.diff(d2)

        self.assertFalse(r1)
        self.assertFalse(r2)
        self.assertFalse(r3)

    def test_diff3(self):
        d1 = DictOfLoggedDict()
        d2 = DictOfLoggedDict()

        dAux1 = {'a1': 1, 'a2': 'ce'}
        dAux2 = {'a1': 2}

        di1 = {'a': dAux1, 'b': dAux1, 'c': dAux1}
        di2 = {'b': dAux1, 'c': dAux2, 'd': dAux1}

        d1.update(di1)
        d2.update(di2)

        r1 = d1.diff(di2)
        r2 = d1.diff(d2)

        self.assertTrue(r1)
        self.assertTrue(r2)

        self.assertNotEqual(d1, d2)
        self.assertNotEqual(d1, di2)

    def test_lenX(self):
        d1 = DictOfLoggedDict()
        dAux1 = {'a1': 1, 'a2': 'ce'}
        di1 = {'a': dAux1, 'b': dAux1}

        d1.update(di1)
        r1 = len(d1)
        rV1 = d1.lenV()

        d1.purge('b')
        r2 = len(d1)
        rV2 = d1.lenV()

        self.assertEqual(r1, 2)
        self.assertEqual(rV1, 2)
        self.assertEqual(r2, 1)
        self.assertEqual(rV2, 2)

    def test_show(self):
        time0 = struct_time((2024, 12, 13, 23, 4, 24, 4, 348, 0))
        time1 = struct_time((2024, 12, 13, 23, 4, 34, 4, 348, 0))
        time2 = struct_time((2024, 12, 13, 23, 4, 44, 4, 348, 0))

        dAux1 = {'a1': 1, 'a2': 'ce'}

        expStr0C = "{} [t:2024-12-13 23:04:24+0000 l:0]"
        expStr1C = ("{'a':{'a1': 1 [t:2024-12-13 23:04:34+0000 l:1], 'a2': 'ce' [t:2024-12-13 23:04:34+0000 l:1]} ("
                    "t:2024-12-13 23:04:34+0000 l:2)} [t:2024-12-13 23:04:34+0000 l:1]")
        expStr2C = ("{'a':{'a1': 1 [t:2024-12-13 23:04:34+0000 l:1], 'a2': 'ce' [t:2024-12-13 23:04:34+0000 l:1]} ("
                    "t:2024-12-13 23:04:34+0000 l:2), 'b1':{'a1': 1 [t:2024-12-13 23:04:34+0000 l:1], 'a2': 'ce' ["
                    "t:2024-12-13 23:04:34+0000 l:1]} (t:2024-12-13 23:04:34+0000 l:2)} [t:2024-12-13 23:04:34+0000 "
                    "l:1]")
        expStr3C = ("{'a':{'a1': 1 [t:2024-12-13 23:04:34+0000 l:1], 'a2': 'ce' [t:2024-12-13 23:04:34+0000 l:1]} ("
                    "t:2024-12-13 23:04:34+0000 l:2), 'b1':{'a1': 1 [t:2024-12-13 23:04:34+0000 l:1], 'a2': 'ce' ["
                    "t:2024-12-13 23:04:34+0000 l:1]} (t:2024-12-13 23:04:34+0000 l:2), 'c12':{'a1': 1 [t:2024-12-13 "
                    "23:04:34+0000 l:1], 'a2': 'ce' [t:2024-12-13 23:04:34+0000 l:1]} (t:2024-12-13 23:04:34+0000 "
                    "l:2)} [t:2024-12-13 23:04:34+0000 l:1]")
        expStr4C = ("{'a':{'a1': 1 [t:2024-12-13 23:04:34+0000 l:1], 'a2': 'ce' [t:2024-12-13 23:04:34+0000 l:1]} ("
                    "t:2024-12-13 23:04:34+0000 l:2), 'b1':{'a1': 1 [t:2024-12-13 23:04:34+0000 l:1], 'a2': 'ce' ["
                    "t:2024-12-13 23:04:34+0000 l:1]} (t:2024-12-13 23:04:34+0000 l:2), 'c12':{'a1': 1 [t:2024-12-13 "
                    "23:04:34+0000 l:1], 'a2': 'ce' [t:2024-12-13 23:04:34+0000 l:1]} (t:2024-12-13 23:04:44+0000 D "
                    "l:3)} [t:2024-12-13 23:04:44+0000 l:2]")

        expStr1 = """{ 'a': { 'a1': 1 [t:2024-12-13 23:04:34+0000 l:1],
         'a2': 'ce' [t:2024-12-13 23:04:34+0000 l:1]
       } (t:2024-12-13 23:04:34+0000 l:2)
} [t:2024-12-13 23:04:34+0000 l:1]"""
        expStr2 = """{ 'a':  { 'a1': 1 [t:2024-12-13 23:04:34+0000 l:1],
          'a2': 'ce' [t:2024-12-13 23:04:34+0000 l:1]
        } (t:2024-12-13 23:04:34+0000 l:2),
  'b1': { 'a1': 1 [t:2024-12-13 23:04:34+0000 l:1],
          'a2': 'ce' [t:2024-12-13 23:04:34+0000 l:1]
        } (t:2024-12-13 23:04:34+0000 l:2)
} [t:2024-12-13 23:04:34+0000 l:1]"""
        expStr4 = """{ 'a':   { 'a1': 1 [t:2024-12-13 23:04:34+0000 l:1],
           'a2': 'ce' [t:2024-12-13 23:04:34+0000 l:1]
         } (t:2024-12-13 23:04:34+0000 l:2),
  'b1':  { 'a1': 1 [t:2024-12-13 23:04:34+0000 l:1],
           'a2': 'ce' [t:2024-12-13 23:04:34+0000 l:1]
         } (t:2024-12-13 23:04:34+0000 l:2),
  'c12': { 'a1': 1 [t:2024-12-13 23:04:34+0000 l:1],
           'a2': 'ce' [t:2024-12-13 23:04:34+0000 l:1]
         } (t:2024-12-13 23:04:44+0000 D l:3)
} [t:2024-12-13 23:04:44+0000 l:2]"""
        expStr4F = """{ 'a':   { 'a1': 1 [t:2024-12-13 23:04:34+0000 l:1],
           'a2': 'ce' [t:2024-12-13 23:04:34+0000 l:1]
         } (t:2024-12-13 23:04:34+0000 l:2),
  'b1':  { 'a1': 1 [t:2024-12-13 23:04:34+0000 l:1],
           'a2': 'ce' [t:2024-12-13 23:04:34+0000 l:1]
         } (t:2024-12-13 23:04:34+0000 l:2),
  'c12': { 'a1': 1 [t:2024-12-13 23:04:34+0000 l:1],
           'a2': 'ce' [t:2024-12-13 23:04:34+0000 l:1]
         } (t:2024-12-13 23:04:44+0000 D l:3)
} [t:2024-12-13 23:04:44+0000 l:2]"""

        d0 = DictOfLoggedDict(timestamp=time0)
        d1 = DictOfLoggedDict(timestamp=time0)
        d2 = DictOfLoggedDict(timestamp=time0)
        d3 = DictOfLoggedDict(timestamp=time0)
        d4 = DictOfLoggedDict(timestamp=time0)

        d1.update({'a': dAux1}, timestamp=time1)
        d2.update({'a': dAux1, 'b1': dAux1}, timestamp=time1)
        d3.update({'a': dAux1, 'b1': dAux1, 'c12': dAux1}, timestamp=time1)
        d4.update({'a': dAux1, 'b1': dAux1, 'c12': dAux1}, timestamp=time1)
        d4.purge({'c12'}, timestamp=time2)

        r0C = d0.show(compact=True)
        r1C = d1.show(compact=True)
        r2C = d2.show(compact=True)
        r3C = d3.show(compact=True)
        r4C = d4.show(compact=True)

        r1 = d1.show(compact=False)
        r2 = d2.show(compact=False)
        r4 = d4.show(compact=False)
        r4F = d4.show(compact=False, firstIndent=1)

        self.maxDiff = None
        self.assertEqual(r0C, expStr0C)
        self.assertEqual(r1C, expStr1C)
        self.assertEqual(r2C, expStr2C)
        self.assertEqual(r3C, expStr3C)
        self.assertEqual(r4C, expStr4C)

        self.assertEqual(r1, expStr1)
        self.assertEqual(r2, expStr2)
        self.assertEqual(r4, expStr4)
        self.assertEqual(r4F, expStr4F)

        r0e = repr(d0)
        r1e = repr(d1)
        r4e = repr(d4)

        self.assertEqual(r0e, expStr0C)
        self.assertEqual(r1e, expStr1C)
        self.assertEqual(r4e, expStr4C)
        self.assertEqual(expStr4F, expStr4)

    def test_diffShow(self):
        time0 = struct_time((2024, 12, 13, 23, 4, 24, 4, 348, 0))
        time1 = struct_time((2024, 12, 13, 23, 4, 34, 4, 348, 0))

        expRes0C = ""
        expRes1C = (" 'a': D {'a1': 1 [t:2024-12-13 23:04:34+0000 l:1], 'a2': 'ce' [t:2024-12-13 23:04:34+0000 l:1]} ("
                    "t:2024-12-13 23:04:34+0000 l:2),  'c': C 'a1': C '1' -> '2', 'a2': D 'ce',  'd': A {'a1': 1, "
                    "'a2': 'ce'}")
        expRes0 = ""
        expRes1 = (" 'a': D {'a1': 1 [t:2024-12-13 23:04:34+0000 l:1], 'a2': 'ce' [t:2024-12-13 23:04:34+0000 l:1]} ("
                   "t:2024-12-13 23:04:34+0000 l:2)\n 'c': C 'a1': C '1' -> '2', 'a2': D 'ce'\n 'd': A {'a1': 1, "
                   "'a2': 'ce'}")

        d1 = DictOfLoggedDict(timestamp=time0)

        dAux1 = {'a1': 1, 'a2': 'ce'}
        dAux2 = {'a1': 2}

        di1 = {'a': dAux1, 'b': dAux1, 'c': dAux1}
        di2 = {'b': dAux1, 'c': dAux2, 'd': dAux1}

        d1.update(di1, timestamp=time1)

        rAux0 = d1.diff(di1)
        rAux1 = d1.diff(di2)

        r0C = rAux0.show(compact=True)
        r0 = rAux0.show(compact=False)
        r1C = rAux1.show(compact=True)
        r1 = rAux1.show(compact=False)
        r0e = repr(rAux0)
        r1e = repr(rAux1)

        self.assertEqual(r0C, expRes0C)
        self.assertEqual(r0, expRes0)

        self.assertEqual(r1C, expRes1C)
        self.assertEqual(r1, expRes1)

        self.assertEqual(r0e, expRes0C)
        self.assertEqual(r1e, expRes1C)

    def test_compareKeys1(self):
        dAux1 = {'ax': 1, 'bx': 2}
        di1 = {'a': dAux1, 'b': dAux1, 'c': dAux1}
        di2 = {'b': dAux1, 'c': dAux1, 'd': dAux1}

        res11 = SetDiff(missing=set(), shared={'a', 'b', 'c'}, new=set())
        res12 = SetDiff(missing={'a'}, shared={'b', 'c'}, new={'d'})
        d1 = DictOfLoggedDict()
        d1.update(di1)
        d2 = DictOfLoggedDict()
        d2.update(di2)

        compKeysD1D1 = d1.compareWithOtherKeys(d1)
        compKeysD1D2 = d1.compareWithOtherKeys(d2)
        compKeysD1d1 = d1.compareWithOtherKeys(di1)
        compKeysD1d2 = d1.compareWithOtherKeys(di2)

        with self.assertRaises(TypeError):
            d1.compareWithOtherKeys(25)

        self.assertEqual(compKeysD1D1, res11)
        self.assertEqual(compKeysD1d1, res11)
        self.assertEqual(compKeysD1D2, res12)
        self.assertEqual(compKeysD1d2, res12)

    def test_replace(self):
        dAux1 = {'ax': 1, 'bx': 2}
        dAux2 = {'ax': 2, 'bx': 3}

        di1 = {'a': dAux1, 'b': dAux1, 'c': dAux1}
        di2 = {'b': dAux1, 'c': dAux2, 'd': dAux1}

        d10 = DictOfLoggedDict()
        d1D1 = DictOfLoggedDict()
        d1d1 = DictOfLoggedDict()
        d1D2 = DictOfLoggedDict()
        d1d2 = DictOfLoggedDict()

        d10.update(di1)
        d1D1.update(di1)
        d1D2.update(di1)
        d1d1.update(di1)
        d1d2.update(di1)

        d1 = DictOfLoggedDict()
        d1.update(di1)
        d2 = DictOfLoggedDict()
        d2.update(di2)

        r1D1 = d1D1.replace(d1)
        r1d1 = d1d1.replace(di1)
        r1D2 = d1D2.replace(d2)
        r1d2 = d1d2.replace(di2)
        r1d2b = d1d2.replace(di2)

        with self.assertRaises(TypeError):
            d10.replace(25)
        with self.assertRaises(TypeError):
            d10.replace(dAux1)

        self.assertFalse(r1D1)
        self.assertFalse(r1d1)
        self.assertTrue(r1D2)
        self.assertTrue(r1d2)
        self.assertFalse(r1d2b)

        self.assertEqual(d1D2._asdict(), di2)
        self.assertEqual(d1d2._asdict(), di2)

    def test_renameKeys(self):
        dAux1 = {'a': 1, 'b': 2, 'c': 3}
        dAux2 = {'b': 2, 'c': 3, 'd': 4}
        dAux3 = {'c': 3, 'd': 4, 'e': 5}

        di1 = {'k1': dAux1, 'k2': dAux2, 'k3': dAux3}
        tr1 = {'b': 'x', 'd': 'y'}
        tr2 = {'e': 'no1', 'f': 'no2'}

        d1 = DictOfLoggedDict()
        d2 = DictOfLoggedDict()

        d1.update(di1)
        d2.update(di1)
        d2.purge({'k3'})

        r1 = d1.renameKeys(tr1)
        r2 = d2.renameKeys(tr2)

        ke1 = set(d1.subkeys())
        ke2 = set(d2.subkeys())

        self.assertTrue(r1)
        self.assertFalse(r2)
        self.assertSetEqual(ke1, {'a', 'x', 'c', 'y', 'e'})
        self.assertSetEqual(ke2, {'a', 'b', 'c', 'd'})
        self.assertDictEqual(d1['k1'], {'a': 1, 'x': 2, 'c': 3})
        self.assertDictEqual(d1['k2'], {'x': 2, 'c': 3, 'y': 4})

    def test_extractKey(self):
        dAux1 = {'ax': 1, 'bx': 2}
        dAux2 = {'ax': 2, 'bx': 3}
        dAux3 = {'bx': 4}

        di1 = {'a': dAux1, 'b': dAux2, 'c': dAux3}

        d1 = DictOfLoggedDict()
        d2 = DictOfLoggedDict()

        d1.update(di1)
        d2.update(di1)
        d2.purge('c')

        r1 = d1.extractKey('ax')
        r1d = d1.extractKey('ax', 'No')

        r2 = d2.extractKey('ax')
        r2d = d2.extractKey('ax', 'No')

        self.assertDictEqual(r1, {'a': 1, 'b': 2, 'c': None})
        self.assertDictEqual(r1d, {'a': 1, 'b': 2, 'c': 'No'})

        self.assertDictEqual(r2, {'a': 1, 'b': 2})
        self.assertDictEqual(r2d, {'a': 1, 'b': 2})

    def testContainsIn(self):
        dAux1 = {'ax': 1, 'bx': 2}

        di1 = {'a': dAux1, 'b': dAux1}

        d1 = DictOfLoggedDict()
        d1.update(di1)
        d1.purge('b')

        r1 = 'a' in d1
        r2 = 'b' in d1
        r3 = 'c' in d1

        self.assertTrue(r1)
        self.assertFalse(r2)
        self.assertFalse(r3)
