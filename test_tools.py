import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import vilod_tools as v


class ToolsTests(unittest.TestCase):
    def test_hash_known_vector(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'a'; p.write_bytes(b'abc')
            self.assertEqual(v.digest(p), 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad')

    def test_compare_and_duplicates(self):
        with tempfile.TemporaryDirectory() as d:
            a, b = Path(d)/'a', Path(d)/'b'; a.mkdir(); b.mkdir()
            for folder in (a, b): (folder/'same').write_bytes(b'123')
            (a/'changed').write_bytes(b'one'); (b/'changed').write_bytes(b'two')
            (a/'extra').write_bytes(b'123')
            self.assertEqual(v.compare(a,b), {'only_left':['extra'],'only_right':[], 'changed':['changed'],'identical_count':1})
            self.assertEqual(v.duplicates(a), [['extra','same']])

    def test_json_nested_duplicate_and_nonstandard(self):
        self.assertFalse(v.json_check('{"a":{"b":1,"b":2}}')['ok'])
        self.assertTrue(v.json_check('{"a":1}')['ok'])
        with self.assertRaises(ValueError): v.json_check('{"a":NaN}')

    def test_csv_quotes_and_width(self):
        self.assertTrue(v.csv_check('a,b\n"one,two",three\n')['ok'])
        self.assertFalse(v.csv_check('a,b\n1\n')['ok'])
        self.assertFalse(v.csv_check('a,a\n1,2\n')['ok'])

    def test_redaction_and_unicode(self):
        text = 'Bearer abc.def password="two words" dev@example.invalid C:\\Users\\SampleUser\\file /home/sample/file 192.0.2.1 Привет'
        clean, counts = v.redact(text)
        for secret in ['abc.def','two words','dev@example.invalid','SampleUser','/home/sample/','192.0.2.1']:
            self.assertNotIn(secret, clean)
        self.assertIn('Привет', clean)
        self.assertGreater(sum(counts.values()), 0)

    def test_redaction_never_overwrites(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'input'; p.write_text('password=example', encoding='utf-8')
            self.assertEqual(v.main(['redact',str(p),str(p)]), 2)
            self.assertEqual(p.read_text(), 'password=example')


if __name__ == '__main__': unittest.main()
