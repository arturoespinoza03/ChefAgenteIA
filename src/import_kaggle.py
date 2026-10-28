"""Importa el archivo local de Kaggle, preservando originales y sin inferir ingredientes."""
import argparse
import hashlib
import json
import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw/kaggle'
DB = ROOT / 'data/kaggle.sqlite'
SCHEMA = '''
CREATE TABLE recipes(id TEXT PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE steps(recipe_id TEXT REFERENCES recipes(id), position INTEGER, instruction TEXT NOT NULL, PRIMARY KEY(recipe_id,position));
CREATE TABLE images(recipe_id TEXT REFERENCES recipes(id), position INTEGER, relative_path TEXT NOT NULL, PRIMARY KEY(recipe_id,position));
CREATE INDEX recipe_name_idx ON recipes(name);
'''

def load(source=None):
    RAW.mkdir(parents=True, exist_ok=True)
    if source:
        source = Path(source).resolve()
        for filename in ('data_strings_local.json', 'image_path.json'):
            shutil.copy2(source / filename, RAW / filename)
        shutil.copytree(source / 'images', RAW / 'images', dirs_exist_ok=True)
    recipes = json.loads((RAW / 'data_strings_local.json').read_text())
    images = json.loads((RAW / 'image_path.json').read_text())
    if not isinstance(recipes, dict) or not isinstance(images, dict):
        raise ValueError('Se esperaban dos objetos JSON')
    if set(images) - set(recipes):
        raise ValueError('Existen referencias a recetas desconocidas')
    for key, steps in recipes.items():
        if not isinstance(key, str) or not isinstance(steps, list) or any(not isinstance(s, str) for s in steps):
            raise ValueError('Estructura de pasos no válida')
    for paths in images.values():
        if not isinstance(paths, list):
            raise ValueError('Lista de imágenes no válida')
        for path in paths:
            target = (RAW / path).resolve()
            if not target.is_relative_to(RAW.resolve()) or not target.is_file():
                raise ValueError('Imagen ausente o ruta no válida')
    temp = DB.with_suffix('.building.sqlite')
    if temp.exists():
        temp.unlink()
    with sqlite3.connect(temp) as conn:
        conn.execute('PRAGMA foreign_keys=ON')
        conn.executescript(SCHEMA)
        for key, steps in recipes.items():
            conn.execute('INSERT INTO recipes VALUES (?,?)', (key, key.replace('_', ' ').strip()))
            conn.executemany('INSERT INTO steps VALUES (?,?,?)', [(key, i, s) for i, s in enumerate(steps, 1)])
            conn.executemany('INSERT INTO images VALUES (?,?,?)', [(key, i, s) for i, s in enumerate(images.get(key, []), 1)])
        assert conn.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
        assert not conn.execute('PRAGMA foreign_key_check').fetchall()
    temp.replace(DB)
    (ROOT / 'data/kaggle_schema.sql').write_text(SCHEMA)
    stats = dict(recipes=len(recipes), steps=sum(map(len, recipes.values())), image_references=sum(map(len, images.values())), recipes_without_images=sum(not images.get(k) for k in recipes), empty_steps=sum(not s.strip() for v in recipes.values() for s in v), recipes_without_steps=sum(not v for v in recipes.values()), duplicate_step_sequences=len(recipes)-len({tuple(v) for v in recipes.values()}), unreferenced_image_files=len({str(p.relative_to(RAW)) for p in (RAW/'images').iterdir() if p.is_file()} - {s for v in images.values() for s in v}), missing_images=0)
    manifest = dict(imported_at_utc=datetime.now(timezone.utc).isoformat(), origin='Archivo local facilitado por el usuario, descargado de Kaggle según su indicación', dataset_url=None, license='Pendiente de verificar; no incluida en el archivo', files={str(p.relative_to(RAW)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(RAW.rglob('*')) if p.is_file()}, quality=stats)
    metadata_path = ROOT / 'evidence/kaggle_metadata.json'
    if metadata_path.exists():
        metadata = json.loads(metadata_path.read_text())
        manifest.update(dataset_url=metadata['url'], license=metadata['licenseName'], publisher=metadata['ownerName'], kaggle_ref=metadata['ref'], catalog_version=metadata['currentVersionNumber'], catalog_last_updated=metadata['lastUpdated'], metadata_evidence='evidence/kaggle_metadata.json')
    (ROOT / 'data/kaggle_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    (ROOT / 'evidence/kaggle_quality.json').write_text(json.dumps(stats, indent=2))
    print(json.dumps(stats, indent=2))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', help='Carpeta descomprimida; omitir para reconstruir desde la copia incluida')
    load(parser.parse_args().source)
