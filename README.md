A web application to manage a blog webpage made in flask
========================================================

## Environment Variables
- `DATABASE_URL` the database url
- `SECRET_KEY` self explanatory. used by flask to sign session cookies

### Example `.env`

```
POSTGRESQL_HOST=0.0.0.0
POSTGRESQL_PORT=5432

POSTGRESQL_ADMIN_USER=[[ADMIN USERNAME HERE]]
POSTGRESQL_ADMIN_PASSWORD=[[ADMIN PASSWORD HERE]]

POSTGRESQL_USER=blog_mgr
POSTGRESQL_USER_PASSWORD=password
POSTGRESQL_DB_NAME=blog_mgr_db

SECRET_KEY=[[ SECRET KEY HERE ]]
```
