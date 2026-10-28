import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from query_data import connect, recipes_with_ingredient, recipe_detail

class DataTests(unittest.TestCase):
    def test_database_integrity(self):
        for db in ('recipes',):
            with connect(db) as c:self.assertEqual(c.execute('PRAGMA integrity_check').fetchone()[0],'ok')
    def test_recipe_foreign_keys(self):
        with connect('recipes') as c:self.assertEqual(c.execute('PRAGMA foreign_key_check').fetchall(),[])
    def test_ingredient_search_and_detail_agree(self):
        with connect('recipes') as c:
            key=c.execute('SELECT ingredient_key FROM recipe_ingredients ORDER BY recipe_id,position LIMIT 1').fetchone()[0]
        found=recipes_with_ingredient(key)
        self.assertTrue(found)
        for recipe in found:
            detail=recipe_detail(recipe['id'])
            self.assertIn(key,[i['ingredient'].casefold() for i in detail['ingredients']])
    def test_unknown_and_sql_injection_inputs(self):
        self.assertEqual(recipes_with_ingredient("' OR 1=1 --"),[])
        self.assertIsNone(recipe_detail('NONEXISTENT'))
    def test_read_only_connection(self):
        import sqlite3
        with connect('recipes') as c:
            with self.assertRaises(sqlite3.OperationalError):c.execute("DELETE FROM recipes")

if __name__=='__main__':unittest.main(verbosity=2)
