import os
from urllib.parse import urlparse

import psycopg2
from django.core.management.base import BaseCommand, CommandError
from dotenv import load_dotenv


class Command(BaseCommand):
    help = "Drops and recreates the entire PostgreSQL database."

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting database reset procedure...")

        # Load environment variables from .env
        env_path = os.path.join(os.getcwd(), ".env")
        load_dotenv(dotenv_path=env_path)

        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise CommandError("DATABASE_URL is not set in the .env file.")

        try:
            url = urlparse(database_url)
            db_name = url.path[1:]  # Remove leading '/'
            db_user = url.username
            db_password = url.password
            db_host = url.hostname
            db_port = url.port

            self.stdout.write(f"Target database: {db_name}")

            # Connect to the default 'postgres' database to manage the target database
            conn = psycopg2.connect(
                dbname="postgres",
                user=db_user,
                password=db_password,
                host=db_host,
                port=db_port,
            )
            conn.autocommit = True
            cursor = conn.cursor()

            # Drop the database
            self.stdout.write(
                self.style.WARNING(
                    f"Attempting to drop database '{db_name}'. "
                    "This will terminate all active connections."
                )
            )
            cursor.execute(f'DROP DATABASE IF EXISTS "{db_name}" WITH (FORCE);')
            self.stdout.write(
                self.style.SUCCESS(f"Successfully dropped database '{db_name}'.")
            )

            # Recreate the database
            self.stdout.write(f"Attempting to recreate database '{db_name}'...")
            cursor.execute(
                f'CREATE DATABASE "{db_name}" '
                f"WITH OWNER = '{db_user}' "
                f"ENCODING = 'UTF8';"
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully recreated database '{db_name}' with owner '{db_user}'."
                )
            )

        except Exception as e:
            raise CommandError(f"An error occurred: {e}")

        finally:
            if "cursor" in locals() and cursor:
                cursor.close()
            if "conn" in locals() and conn:
                conn.close()
