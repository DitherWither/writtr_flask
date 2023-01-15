if test ! -f $HOME/.postgresql/root.crt; then
    curl --create-dirs -o $HOME/.postgresql/root.crt -O $DATABASE_CERT
fi