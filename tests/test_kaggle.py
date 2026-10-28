import json
import sqlite3
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from query_data import connect,kaggle_search,kaggle_detail

class KaggleTests(unittest.TestCase):
    def test_import_matches_original_steps_and_images(self):
        original=json.loads((ROOT/'data/raw/kaggle/data_strings_local.json').read_text())
        images=json.loads((ROOT/'data/raw/kaggle/image_path.json').read_text())
        with connect('kaggle') as c:
            self.assertEqual(c.execute('SELECT count(*) FROM recipes').fetchone()[0],len(original))
            self.assertEqual(c.execute('PRAGMA integrity_check').fetchone()[0],'ok')
            self.assertEqual(c.execute('PRAGMA foreign_key_check').fetchall(),[])
        for key,steps in original.items():
            detail=kaggle_detail(key)
            self.assertEqual([s['instruction'] for s in detail['steps']], steps)
            self.assertEqual(detail['images'],images.get(key,[]))
            for image in detail['images']:
                self.assertTrue((ROOT/'data/raw/kaggle'/image).is_file())
    def test_search_and_detail(self):
        rows=kaggle_search('chicken')
        self.assertTrue(rows)
        self.assertTrue(all('chicken' in r['name'].lower() for r in rows))
        self.assertEqual(kaggle_search("' OR 1=1 --"),[])
        self.assertIsNone(kaggle_detail('does-not-exist'))
    def test_readonly(self):
        with connect('kaggle') as c:
            with self.assertRaises(sqlite3.OperationalError):
                c.execute('DELETE FROM recipes')
