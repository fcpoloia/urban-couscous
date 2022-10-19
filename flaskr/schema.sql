BEGIN TRANSACTION;
PRAGMA foreign_keys=OFF;
DROP TABLE IF EXISTS config;
DROP TABLE IF EXISTS models;
DROP TABLE IF EXISTS sites;
DROP TABLE IF EXISTS videos;
DROP TABLE IF EXISTS photos;
CREATE TABLE IF NOT EXISTS models (id int PRIMARY KEY NOT NULL, name text, thumb text);
CREATE TABLE IF NOT EXISTS sites  (id int PRIMARY KEY, name text, location text);
CREATE TABLE IF NOT EXISTS photos (id int NOT NULL, model_id int NOT NULL, site_id int, name text, 
  location text, thumb text, count int, PRIMARY KEY (id, model_id), FOREIGN KEY (model_id) REFERENCES models(id));
CREATE TABLE IF NOT EXISTS videos (id int NOT NULL,model_id int NOT NULL,site_id int,name text,filename text,
  thumb text,width int,height int,length double, PRIMARY KEY (id, model_id), FOREIGN KEY (model_id) REFERENCES models(id));
CREATE TABLE IF NOT EXISTS config (id int PRIMARY KEY NOT NULL, rootpath text, title text, images text, thumbs text, videos text);
COMMIT;

# config - id, rootpath, title, images, thumbs, videos
# models - id, name, thumb
# sites  - id, name, location
# photos - id, model_id, site_id, name, location, thumb, count
# videos - id, model_id, site_id, name, filename, thumb, width, height, length
