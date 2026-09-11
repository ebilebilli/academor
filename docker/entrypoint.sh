#!/bin/bash
set -e

echo "Waiting for PostgreSQL to be ready..."
while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  sleep 0.1
done
echo "PostgreSQL is ready!"

# Run migrations
echo "Running migrations..."
python academor/manage.py migrate --noinput

# Hashed names (ManifestStaticFilesStorage) must exist before compress
# resolves {% static %} in offline templates — otherwise compress looks for
# academor-lazy-brand.<hash>.js that is not in staticfiles/ yet.
echo "Collecting static files..."
python academor/manage.py collectstatic --noinput

# Offline compressor manifest + CACHE/* (needs collectstatic output above)
echo "Compressing static assets..."
python academor/manage.py compress --force

# Execute the command passed to the container
exec "$@"
