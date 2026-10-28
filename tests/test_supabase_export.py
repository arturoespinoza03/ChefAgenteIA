import csv,json,re,sqlite3,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from export_supabase import literal

class ExportTests(unittest.TestCase):
    def test_generated_data_roundtrip(self):
        # Comprueba todos los INSERT exportados; no sustituye una prueba remota PostgreSQL.
        with (ROOT/'supabase/01_import.sql').open(newline='') as f:
            sql=f.read()
        sql=re.sub(r'^SET LOCAL .*?;\n','',sql,flags=re.M)
        sql=re.sub(r'^ALTER TABLE .*?;\n|^REVOKE .*?;\n|^DO \$\$.*?\$\$;\n|^CREATE INDEX ON .*?;\n','',sql,flags=re.M)
        sql=sql.replace('public.','')
        c=sqlite3.connect(':memory:');c.execute('PRAGMA foreign_keys=ON')
        try:
            c.executescript(sql)
            expected=json.loads((ROOT/'supabase/manifest.json').read_text())['expected_rows']
            for name,count in expected.items():
                self.assertEqual(c.execute(f'SELECT count(*) FROM {name}').fetchone()[0],count)
                with (ROOT/f'supabase/{name}.csv').open(newline='') as f:
                    rows=list(csv.DictReader(f))
                self.assertEqual(len(rows),count)
                actual=c.execute(f'SELECT * FROM {name}').fetchall()
                normalized=[[ '' if v is None else str(v) for v in row] for row in actual]
                self.assertEqual(normalized,[list(row.values()) for row in rows])
            self.assertEqual(c.execute('PRAGMA foreign_key_check').fetchall(),[])
        finally:c.close()
    def test_literal_escaping(self):
        self.assertEqual(literal("l'oeuf"),"'l''oeuf'")
        self.assertEqual(literal(None),'NULL')
        with self.assertRaises(ValueError):literal('\x00')
