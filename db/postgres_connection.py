import os
import psycopg2
from dotenv import load_dotenv

# Do not override vars already set by Docker Compose (e.g. DB_HOST=host.docker.internal).
load_dotenv(override=False)


def get_connection():
    return psycopg2.connect(
        host=(os.getenv("DB_HOST") or "localhost").strip(),
        port=int((os.getenv("DB_PORT") or "5432").strip()),
        dbname=(os.getenv("DB_NAME") or "pawhome").strip(),
        user=(os.getenv("DB_USER") or "postgres").strip(),
        password=os.getenv("DB_PASSWORD") or "",
        connect_timeout=10,
    )
