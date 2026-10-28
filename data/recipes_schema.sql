CREATE TABLE recipe_ingredients(recipe_id TEXT REFERENCES recipes(id),position INTEGER CHECK(position BETWEEN 1 AND 20),ingredient TEXT NOT NULL,ingredient_key TEXT NOT NULL,measure_raw TEXT,PRIMARY KEY(recipe_id,position));
CREATE TABLE recipes(id TEXT PRIMARY KEY,name TEXT NOT NULL,category TEXT,area TEXT,instructions TEXT,source_url TEXT,api_url TEXT NOT NULL);
CREATE INDEX ingredient_lookup ON recipe_ingredients(ingredient_key);
