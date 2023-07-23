database=FinalProject.db
if test -e "$database"; then
    echo "database already exists, should contain default example user"
else
    echo "database does not exists, creating and populating with default example user"
    python3 db_populate.py
fi

python3 app.py