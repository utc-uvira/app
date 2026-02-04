PRAGMA foreign_keys = ON;

-- =========================
-- DROP TABLES (idempotent)
-- =========================
DROP TABLE IF EXISTS ingredient_alias;
DROP TABLE IF EXISTS warnings;
DROP TABLE IF EXISTS mix_ingredient;
DROP TABLE IF EXISTS mix_goal;
DROP TABLE IF EXISTS ingredients;
DROP TABLE IF EXISTS mixes;
DROP TABLE IF EXISTS health_goals;

-- =========================
-- TABLES
-- =========================

CREATE TABLE health_goals (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  code TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  description TEXT
);

CREATE TABLE mixes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  prep_type TEXT NOT NULL CHECK (prep_type IN ('smoothie','jus','infusion','autre')),
  description TEXT,
  instructions TEXT,
  share_slug TEXT UNIQUE,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ingredients (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL,
  type TEXT CHECK (type IN ('fruit','feuille','epice','legume','liquide','miel','autre')) DEFAULT 'autre',
  notes TEXT
);

CREATE TABLE mix_goal (
  mix_id INTEGER NOT NULL,
  goal_id INTEGER NOT NULL,
  relevance INTEGER DEFAULT 50 CHECK (relevance BETWEEN 0 AND 100),
  PRIMARY KEY (mix_id, goal_id),
  FOREIGN KEY (mix_id) REFERENCES mixes(id) ON DELETE CASCADE,
  FOREIGN KEY (goal_id) REFERENCES health_goals(id) ON DELETE CASCADE
);

CREATE TABLE mix_ingredient (
  mix_id INTEGER NOT NULL,
  ingredient_id INTEGER NOT NULL,
  quantity TEXT,
  role TEXT,
  PRIMARY KEY (mix_id, ingredient_id),
  FOREIGN KEY (mix_id) REFERENCES mixes(id) ON DELETE CASCADE,
  FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE
);

CREATE TABLE warnings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  mix_id INTEGER NOT NULL,
  level TEXT CHECK (level IN ('info','prudence','alerte')) DEFAULT 'prudence',
  message TEXT NOT NULL,
  FOREIGN KEY (mix_id) REFERENCES mixes(id) ON DELETE CASCADE
);

CREATE TABLE ingredient_alias (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ingredient_id INTEGER NOT NULL,
  alias TEXT NOT NULL,
  UNIQUE (ingredient_id, alias),
  FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE
);

-- =========================
-- HEALTH GOALS
-- =========================
INSERT INTO health_goals (code, name, description) VALUES
('DIGESTION','Digestion','Confort digestif et transit'),
('IMMUNITE','Immunité','Défenses naturelles'),
('ENERGIE','Énergie / Vitalité','Hydratation et endurance'),
('SOMMEIL','Stress & Sommeil','Relaxation et sommeil'),
('PROSTATE','Santé de la prostate','Prévention et confort urinaire'),
('CARDIO','Santé cardiovasculaire','Circulation et cœur'),
('FOIE','Foie & Détox','Soutien hépatique'),
('CERVEAU','Santé cérébrale & mémoire','Clarté mentale');

-- =========================
-- INGREDIENTS
-- =========================
INSERT INTO ingredients (name, type) VALUES
('Corossol','fruit'),
('Feuilles de corossol','feuille'),
('Banane','fruit'),
('Eau de coco','liquide'),
('Ananas','fruit'),
('Gingembre','epice'),
('Mangue','fruit'),
('Citron vert','fruit'),
('Orange','fruit'),
('Carotte','legume'),
('Avocat','fruit'),
('Lait d’amande','liquide'),
('Miel','miel');

-- Alias
INSERT INTO ingredient_alias (ingredient_id, alias)
SELECT id, 'Soursop' FROM ingredients WHERE name='Corossol';

-- =========================
-- MIXES (COROSSOL)
-- =========================
INSERT INTO mixes (name, prep_type, description, share_slug) VALUES
('Corossol – Banane – Eau de coco','smoothie','Énergie, hydratation, digestion douce','corossol-banane-eau-coco'),
('Corossol – Ananas – Gingembre','smoothie','Anti-ballonnements, digestion, fraîcheur','corossol-ananas-gingembre'),
('Corossol – Mangue – Citron vert','smoothie','Antioxydants, immunité, peau','corossol-mangue-citron-vert'),
('Corossol – Orange – Carotte','jus','Vitamine C, énergie','corossol-orange-carotte'),
('Corossol – Avocat – Lait d’amande','smoothie','Satiété, bons lipides','corossol-avocat-lait-amande'),
('Corossol – Citron – Miel','jus','Réveil digestif, détox légère','corossol-citron-miel'),
('Infusion feuilles de corossol – Gingembre','infusion','Relaxation, sommeil','infusion-feuilles-corossol-gingembre');

-- =========================
-- MIX ↔ GOAL
-- =========================
INSERT INTO mix_goal (mix_id, goal_id, relevance)
SELECT m.id, g.id, 90 FROM mixes m, health_goals g
WHERE m.share_slug='corossol-banane-eau-coco' AND g.code='ENERGIE';

INSERT INTO mix_goal
SELECT m.id, g.id, 90 FROM mixes m, health_goals g
WHERE m.share_slug='corossol-ananas-gingembre' AND g.code='DIGESTION';

INSERT INTO mix_goal
SELECT m.id, g.id, 85 FROM mixes m, health_goals g
WHERE m.share_slug='corossol-mangue-citron-vert' AND g.code='IMMUNITE';

INSERT INTO mix_goal
SELECT m.id, g.id, 80 FROM mixes m, health_goals g
WHERE m.share_slug='corossol-orange-carotte' AND g.code='IMMUNITE';

INSERT INTO mix_goal
SELECT m.id, g.id, 75 FROM mixes m, health_goals g
WHERE m.share_slug='corossol-avocat-lait-amande' AND g.code='ENERGIE';

INSERT INTO mix_goal
SELECT m.id, g.id, 88 FROM mixes m, health_goals g
WHERE m.share_slug='corossol-citron-miel' AND g.code='DIGESTION';

INSERT INTO mix_goal
SELECT m.id, g.id, 92 FROM mixes m, health_goals g
WHERE m.share_slug='infusion-feuilles-corossol-gingembre' AND g.code='SOMMEIL';

-- =========================
-- MIX ↔ INGREDIENT
-- =========================
INSERT INTO mix_ingredient
SELECT m.id, i.id, NULL, 'base'
FROM mixes m JOIN ingredients i
ON m.share_slug='corossol-banane-eau-coco' AND i.name IN ('Corossol','Banane','Eau de coco');

INSERT INTO mix_ingredient
SELECT m.id, i.id, NULL, 'actif'
FROM mixes m JOIN ingredients i
ON m.share_slug='corossol-ananas-gingembre' AND i.name IN ('Corossol','Ananas','Gingembre');

INSERT INTO mix_ingredient
SELECT m.id, i.id, NULL, 'actif'
FROM mixes m JOIN ingredients i
ON m.share_slug='infusion-feuilles-corossol-gingembre' AND i.name IN ('Feuilles de corossol','Gingembre');

-- =========================
-- WARNINGS
-- =========================
INSERT INTO warnings (mix_id, level, message)
SELECT id, 'info',
'Information éducative uniquement. Ne remplace pas un avis médical.'
FROM mixes;

INSERT INTO warnings (mix_id, level, message)
SELECT id, 'prudence',
'Utiliser avec modération. Demander conseil en cas de traitement, grossesse ou condition particulière.'
FROM mixes
WHERE share_slug='infusion-feuilles-corossol-gingembre';
