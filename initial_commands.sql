/* Run before first run of the program */

DROP DATABASE IF EXISTS blog_mgr_db;
DROP OWNED BY blog_mgr;
DROP USER IF EXISTS blog_mgr ;

CREATE DATABASE blog_mgr_db;
CREATE USER blog_mgr WITH PASSWORD 'password'; -- Change when deploying
GRANT ALL PRIVILEGES ON DATABASE blog_mgr_db TO blog_mgr;

GRANT USAGE ON SCHEMA public TO blog_mgr;
