
CREATE TABLE recipes(id TEXT PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE steps(recipe_id TEXT REFERENCES recipes(id), position INTEGER, instruction TEXT NOT NULL, PRIMARY KEY(recipe_id,position));
CREATE TABLE images(recipe_id TEXT REFERENCES recipes(id), position INTEGER, relative_path TEXT NOT NULL, PRIMARY KEY(recipe_id,position));
CREATE INDEX recipe_name_idx ON recipes(name);
