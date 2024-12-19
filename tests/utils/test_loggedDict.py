import unittest

from  src.CAPcore.LoggedDict import LoggedDict

class TestLoggedDict(unittest.TestCase):
    def test_constructor1(self):
        d1 = LoggedDict()

        self.assertEqual(len(d1), 0)

    def test_constructor2(self):
        with self.assertRaises(TypeError):
            d1 = LoggedDict(exclusions=25)
            d1.addExclusion('a')

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

        lv1 = d1.getValue('b')
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
        v1 = d1.get('b','Deleted')
        v2 = d1.get('c',25)

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
        lv1=d1.getValue('b')
        self.assertEqual(len(lv1),2)

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

        r1 = d1.purge(['c','a'])
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
        r1=d1.addExclusion('c')

        self.assertEqual(len(d1.exclusions),1)
        self.assertFalse(r1)

    def test_addExclusion2(self):
        d1 = LoggedDict()
        d1.update({'c':25})
        r1=d1.addExclusion('c')

        self.assertEqual(len(d1),0)
        self.assertTrue(r1)

if __name__ == '__main__':
    unittest.main()
