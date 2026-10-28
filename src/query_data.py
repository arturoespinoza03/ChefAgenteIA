"""Consultas parametrizadas y de solo lectura para integrar posteriormente con MCP."""
from pathlib import Path
import argparse, json, sqlite3
ROOT=Path(__file__).resolve().parents[1]

class ClosingConnection(sqlite3.Connection):
    def __exit__(self, *args):
        try:
            return super().__exit__(*args)
        finally:
            self.close()

def connect(name):
    c=sqlite3.connect(f'file:{ROOT}/data/{name}.sqlite?mode=ro',uri=True,factory=ClosingConnection)
    c.row_factory=sqlite3.Row
    return c

def recipes_with_ingredient(ingredient):
    with connect('recipes') as c:
        return [dict(r) for r in c.execute('''SELECT DISTINCT r.id,r.name,r.category,r.api_url FROM recipes r
        JOIN recipe_ingredients i ON i.recipe_id=r.id WHERE i.ingredient_key=? ORDER BY r.name''',(ingredient.strip().casefold(),))]

def recipe_detail(recipe_id):
    with connect('recipes') as c:
        row=c.execute('SELECT * FROM recipes WHERE id=?',(recipe_id,)).fetchone()
        if not row:return None
        result=dict(row)
        result['ingredients']=[dict(r) for r in c.execute('SELECT ingredient,measure_raw FROM recipe_ingredients WHERE recipe_id=? ORDER BY position',(recipe_id,))]
        return result

def kaggle_search(term):
    with connect('kaggle') as c:
        return [dict(r) for r in c.execute("SELECT id,name,(SELECT count(*) FROM steps WHERE recipe_id=r.id) AS step_count FROM recipes r WHERE instr(lower(name),lower(?))>0 ORDER BY name LIMIT 20", (term,))]

def kaggle_detail(recipe_id):
    with connect('kaggle') as c:
        row=c.execute('SELECT * FROM recipes WHERE id=?', (recipe_id,)).fetchone()
        if row is None:
            return None
        result=dict(row)
        result['steps']=[dict(r) for r in c.execute('SELECT position,instruction FROM steps WHERE recipe_id=? ORDER BY position',(recipe_id,))]
        result['images']=[r[0] for r in c.execute('SELECT relative_path FROM images WHERE recipe_id=? ORDER BY position',(recipe_id,))]
        return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('kind',choices=['ingredient','recipe','kaggle-search','kaggle-recipe']);p.add_argument('value');a=p.parse_args()
    f={'ingredient':recipes_with_ingredient,'recipe':recipe_detail,'kaggle-search':kaggle_search,'kaggle-recipe':kaggle_detail}[a.kind]
    print(json.dumps(f(a.value),ensure_ascii=False,indent=2))
