"""Descarga muestras públicas y construye la base SQLite de recetas; solo biblioteca estándar."""
from pathlib import Path
import argparse, datetime, hashlib, json, sqlite3, urllib.parse, urllib.request
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw'

def download(name, url, offline):
    path = RAW / name
    if not offline:
        req = urllib.request.Request(url, headers={'User-Agent': 'ChefControlEducational/0.1', 'Accept':'application/json'})
        with urllib.request.urlopen(req, timeout=60) as response:
            payload = response.read()
        json.loads(payload)
        path.write_bytes(payload)
    return json.loads(path.read_text()), {'url':url, 'file':str(path.relative_to(ROOT)), 'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

def build(offline=False):
    RAW.mkdir(parents=True, exist_ok=True)
    meals, ms = download('themealdb.json', 'https://www.themealdb.com/api/json/v1/1/search.php?s=', offline)
    c=sqlite3.connect(ROOT/'data/recipes.sqlite'); c.execute('PRAGMA foreign_keys=ON')
    c.executescript('''DROP TABLE IF EXISTS recipe_ingredients; DROP TABLE IF EXISTS recipes;
    CREATE TABLE recipes(id TEXT PRIMARY KEY,name TEXT NOT NULL,category TEXT,area TEXT,instructions TEXT,source_url TEXT,api_url TEXT NOT NULL);
    CREATE TABLE recipe_ingredients(recipe_id TEXT REFERENCES recipes(id),position INTEGER CHECK(position BETWEEN 1 AND 20),ingredient TEXT NOT NULL,ingredient_key TEXT NOT NULL,measure_raw TEXT,PRIMARY KEY(recipe_id,position));
    CREATE INDEX ingredient_lookup ON recipe_ingredients(ingredient_key);''')
    for m in meals['meals']:
        c.execute('INSERT INTO recipes VALUES(?,?,?,?,?,?,?)',(m['idMeal'],m['strMeal'],m.get('strCategory'),m.get('strArea'),m.get('strInstructions'),m.get('strSource'),f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={m['idMeal']}"))
        for pos in range(1,21):
            ingredient=(m.get(f'strIngredient{pos}') or '').strip()
            if ingredient: c.execute('INSERT INTO recipe_ingredients VALUES(?,?,?,?,?)',(m['idMeal'],pos,ingredient,ingredient.casefold(),(m.get(f'strMeasure{pos}') or '').strip()))
    c.commit()
    report={'recipes':c.execute('SELECT count(*) FROM recipes').fetchone()[0], 'recipe_ingredients':c.execute('SELECT count(*) FROM recipe_ingredients').fetchone()[0], 'recipes_integrity':c.execute('PRAGMA integrity_check').fetchone()[0], 'recipe_fk_errors':c.execute('PRAGMA foreign_key_check').fetchall()}
    (ROOT/'evidence/quality.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
    manifest_path=ROOT/'data/manifest.json'
    if not offline:
        manifest_path.write_text(json.dumps({'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sources':[ms]},indent=2))
    schema='\n'.join(row[0]+';' for row in c.execute("SELECT sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY type DESC,name"))
    (ROOT/'data/recipes_schema.sql').write_text(schema+'\n')
    c.close()
    print(json.dumps(report,indent=2,ensure_ascii=False))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--offline',action='store_true');build(parser.parse_args().offline)
