import os
from urllib.parse import urlparse

import psycopg2
from django.core.management.base import BaseCommand, CommandError
from dotenv import load_dotenv


def _get_db_config(database_url):
    """Extract database configuration from database URL."""
    url = urlparse(database_url)
    return {
        "name": url.path[1:],  # Remove leading '/'
        "user": url.username,
        "password": url.password,
        "host": url.hostname,
        "port": url.port,
    }


def _connect_to_postgres(db_config):
    """Connect to the default 'postgres' database."""
    return psycopg2.connect(
        dbname="postgres",
        user=db_config["user"],
        password=db_config["password"],
        host=db_config["host"],
        port=db_config["port"],
    )


def _drop_database(cursor, db_name):
    """Drop the specified database."""
    cursor.execute(f'DROP DATABASE IF EXISTS "{db_name}" WITH (FORCE);')


def _create_database(cursor, db_name, db_user):
    """Create the specified database."""
    cursor.execute(
        f'CREATE DATABASE "{db_name}" '
        f"WITH OWNER = '{db_user}' "
        f"ENCODING = 'UTF8';"
    )


class Command(BaseCommand):
    help = "Drops and recreates the entire PostgreSQL database."

    def _get_database_url(self):
        """Get and validate database URL from environment."""
        # Load environment variables from .env
        env_path = os.path.join(os.getcwd(), ".env")
        load_dotenv(dotenv_path=env_path)

        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise CommandError("DATABASE_URL is not set in the .env file.")
        return database_url

    def _setup_connection(self, db_config):
        """Setup database connection."""
        conn = _connect_to_postgres(db_config)
        conn.autocommit = True
        cursor = conn.cursor()
        return conn, cursor

    def _perform_operations(self, db_config, cursor):
        """Perform the actual database operations."""
        self.stdout.write(f"Target database: {db_config['name']}")

        # Drop the database
        self.stdout.write(
            self.style.WARNING(
                f"Attempting to drop database '{db_config['name']}'. "
                "This will terminate all active connections."
            )
        )
        _drop_database(cursor, db_config["name"])
        self.stdout.write(
            self.style.SUCCESS(f"Successfully dropped database '{db_config['name']}'.")
        )

        # Recreate the database
        self.stdout.write(f"Attempting to recreate database '{db_config['name']}'...")
        _create_database(cursor, db_config["name"], db_config["user"])
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully recreated database '{db_config['name']}' with owner '{db_config['user']}'."
            )
        )

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting database reset procedure...")

        database_url = self._get_database_url()
        db_config = _get_db_config(database_url)
        conn = None
        cursor = None

        try:
            conn, cursor = self._setup_connection(db_config)
            self._perform_operations(db_config, cursor)
        except Exception as e:
            raise CommandError(f"An error occurred: {e}")

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
