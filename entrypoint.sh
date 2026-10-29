#!/bin/sh
set -e

echo "Waiting for PostgreSQL ($POSTGRES_HOST:$POSTGRES_PORT) to become available..."

python << END
import sys
import socket
import time
import os

host = os.getenv("POSTGRES_HOST", "localhost")
port = int(os.getenv("POSTGRES_PORT", 5432))

start = time.time()
while time.time() - start < 60:
    try:
        with socket.create_connection((host, port), timeout=2):
            print("PostgreSQL is reachable!")
            sys.exit(0)
    except (socket.timeout, ConnectionRefusedError, OSError):
        time.sleep(1)

print("Timed out waiting for PostgreSQL.")
sys.exit(1)
END

echo "Applying core default database migrations..."
python manage.py migrate --database=default --no-input

echo "Starting application process: $@"
exec "$@"

