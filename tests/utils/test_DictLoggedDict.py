import unittest
from time import struct_time

from src.CAPcore.DictLoggedDict import DictOfLoggedDict


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
            d1['a']
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
        print(v1)

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
        print(v1)

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
        di1 = {'a': dAux1, 'b': dAux1, 'c': dAux1}

        d1.update(newValues=di1)
        r1 = d1.purge('a')
        r2 = d1.purge('a', 'b')
        r3 = d1.purge('a')

        self.assertTrue(r1)
        self.assertTrue(r2)
        self.assertFalse(r3)
        self.assertEqual(len(d1), 1)

    def test_purge2(self):
        d1 = DictOfLoggedDict()
        dAux1 = {'a1': 1, 'a2': 'ce'}
        di1 = {'a': dAux1, 'b': dAux1, 'c': dAux1}

        d1.update(newValues=di1)
        r1 = d1.purge('a')
        r2 = d1.purge('a', 'b')
        r3 = d1.purge('a')

        self.assertTrue(r1)
        self.assertTrue(r2)
        self.assertFalse(r3)
        self.assertEqual(len(d1), 1)

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

        res1 = {'a': "{'a1': 1 [t:2024-12-13 23:04:34+0000 l:1], 'a2': 'ce' [t:2024-12-13 23:04:34+0000 l:1]} ["
                     "t:2024-12-13 23:04:44+0000 D l:3]",
                'b': "{'a1': 1 [t:2024-12-13 23:04:34+0000 l:1], 'a2': 'ce' [t:2024-12-13 23:04:34+0000 l:1]} ["
                     "t:2024-12-13 23:04:34+0000 l:2]"}

        d1 = DictOfLoggedDict(timestamp=time0)
        dAux1 = {'a1': 1, 'a2': 'ce'}
        di1 = {'a': dAux1, 'b': dAux1}

        d1.update(newValues=di1, timestamp=time1)
        d1.purge('a', timestamp=time2)

        r1 = {k: v.showV() for k, v in d1.itemsV()}
        r2 = {k: repr(v) for k, v in d1.itemsV()}

        self.assertDictEqual(r1, res1)
        self.assertDictEqual(r2, res1)

    def test_getitem(self):
        d1 = DictOfLoggedDict()

        with self.assertRaises(KeyError):
            v1 = d1['a']

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
            v1 = d1.get('d')

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
            v3 = d1.pop('d')

        with self.assertRaises(KeyError):
            v3 = d1.pop('b')

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
