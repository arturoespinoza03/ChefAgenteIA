"""Exportación reproducible SQLite → PostgreSQL para Supabase, sin credenciales."""
import csv
import hashlib
import json
import sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'supabase'
SPECS=[
 ('kaggle','recipes','chef_kaggle_recipes','id text PRIMARY KEY, name text NOT NULL','id'),
 ('kaggle','steps','chef_kaggle_steps','recipe_id text REFERENCES public.chef_kaggle_recipes(id), position integer CHECK(position>0), instruction text NOT NULL, PRIMARY KEY(recipe_id,position)','recipe_id,position'),
 ('kaggle','images','chef_kaggle_images','recipe_id text REFERENCES public.chef_kaggle_recipes(id), position integer CHECK(position>0), relative_path text NOT NULL, PRIMARY KEY(recipe_id,position)','recipe_id,position'),
 ('recipes','recipes','chef_themealdb_recipes','id text PRIMARY KEY, name text NOT NULL, category text, area text, instructions text, source_url text, api_url text NOT NULL','id'),
 ('recipes','recipe_ingredients','chef_themealdb_ingredients','recipe_id text REFERENCES public.chef_themealdb_recipes(id), position integer CHECK(position BETWEEN 1 AND 20), ingredient text NOT NULL, ingredient_key text NOT NULL, measure_raw text, PRIMARY KEY(recipe_id,position)','recipe_id,position')]
CURATED='chef_curated_ingredients'
CURATED_SCHEMA='recipe_id text REFERENCES public.chef_kaggle_recipes(id), ingredient_key text, label_es text NOT NULL, source_step integer NOT NULL, evidence_text text NOT NULL, optional integer CHECK(optional IN (0,1)), quantity numeric, unit text, PRIMARY KEY(recipe_id,ingredient_key), FOREIGN KEY(recipe_id,source_step) REFERENCES public.chef_kaggle_steps(recipe_id,position)'

def literal(v):
    if v is None:return 'NULL'
    if isinstance(v,(int,float)):return str(v)
    if '\x00' in v:raise ValueError('PostgreSQL no admite NUL en texto')
    return "'"+v.replace("'","''")+"'"

def export():
    OUT.mkdir(exist_ok=True)
    sql=['-- Generado desde las fuentes locales. No contiene precios ni imágenes binarias.', 'BEGIN;', 'SET LOCAL standard_conforming_strings = on;']
    expected={}
    records={}
    for db,source,target,schema,order in SPECS:
        with sqlite3.connect(f'file:{ROOT}/data/{db}.sqlite?mode=ro',uri=True) as c:
            c.row_factory=sqlite3.Row
            rows=[dict(r) for r in c.execute(f'SELECT * FROM {source} ORDER BY {order}')]
        records[target]=rows
        sql.append(f'CREATE TABLE public.{target} ({schema});')
    records[CURATED]=json.loads((ROOT/'data/curated/recipe_ingredients.json').read_text())['ingredients']
    sql.append(f'CREATE TABLE public.{CURATED} ({CURATED_SCHEMA});')
    for target,rows in records.items():
        expected[target]=len(rows)
        if rows:
            columns=list(rows[0])
            with (OUT/f'{target}.csv').open('w',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=columns);writer.writeheader();writer.writerows(rows)
            for start in range(0,len(rows),100):
                values=[ '('+','.join(literal(row[k]) for k in columns)+')' for row in rows[start:start+100] ]
                sql.append(f'INSERT INTO public.{target} ({",".join(columns)}) VALUES\n'+',\n'.join(values)+';')
        sql.append(f'ALTER TABLE public.{target} ENABLE ROW LEVEL SECURITY;')
        sql.append(f'REVOKE ALL ON TABLE public.{target} FROM anon, authenticated;')
        sql.append(f"DO $$ BEGIN IF (SELECT count(*) FROM public.{target}) <> {len(rows)} THEN RAISE EXCEPTION 'Conteo incorrecto en {target}'; END IF; END $$;")
    sql.extend(['CREATE INDEX ON public.chef_kaggle_recipes(name);','CREATE INDEX ON public.chef_themealdb_ingredients(ingredient_key);','COMMIT;'])
    payload='\n'.join(sql)+'\n'
    (OUT/'01_import.sql').write_text(payload)
    check=' UNION ALL\n'.join(f"SELECT '{name}' AS tabla, count(*) AS filas, {count} AS esperado FROM public.{name}" for name,count in expected.items())+';\n'
    check+="SELECT r.id,r.name,s.position,s.instruction FROM public.chef_kaggle_recipes r JOIN public.chef_kaggle_steps s ON s.recipe_id=r.id WHERE r.id='Ground_Beef_Soup' ORDER BY s.position;\n"
    (OUT/'02_verify.sql').write_text(check)
    manifest=dict(expected_rows=expected,sql_sha256=hashlib.sha256(payload.encode()).hexdigest(),image_files_uploaded=False,remote_import_verified=False)
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
    print(json.dumps(manifest,indent=2))

if __name__=='__main__':export()
