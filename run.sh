#!/bin/sh
# Run inside the container

export FLASK_APP=blog_mgr
source .env
connection_string=postgresql://$POSTGRESQL_ADMIN_USER:$POSTGRESQL_ADMIN_PASSWORD@$POSTGRESQL_HOST:$POSTGRESQL_PORT

if test ! -f 'db-created'; then
    psql $connection_string < initial_commands.sql
    python3 -m flask init-db
fi

python3 -m flask run --host=0.0.0.0