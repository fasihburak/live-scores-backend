# Remove postgres and redis containers together with any persistent volumes defined for them.
docker compose down -v
docker compose run --rm django sh -c \
"/wait-for-it.sh postgres-db:5432 -- python manage.py migrate && pytest"