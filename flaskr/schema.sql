BEGIN TRANSACTION;
PRAGMA foreign_keys=OFF;
DROP TABLE IF EXISTS models;
DROP TABLE IF EXISTS sites;
DROP TABLE IF EXISTS videos;
DROP TABLE IF EXISTS photos;
CREATE TABLE IF NOT EXISTS models (id int PRIMARY KEY NOT NULL, name text, thumb text);
CREATE TABLE IF NOT EXISTS sites  (id int PRIMARY KEY, name text);
CREATE TABLE IF NOT EXISTS photos (id int NOT NULL, model_id int NOT NULL, site_id int, name text, 
  location text, thumb text, count int, PRIMARY KEY (id, model_id), FOREIGN KEY (model_id) REFERENCES models(id));
CREATE TABLE IF NOT EXISTS videos (id int NOT NULL,model_id int NOT NULL,site_id int,name text,filename text,
  thumb text,width int,height int,length double, PRIMARY KEY (id, model_id), FOREIGN KEY (model_id) REFERENCES models(id));
COMMIT;

