"""Create the database and import schema + seed data.

Reads DB_USER / DB_PASSWORD / DB_HOST / DB_PORT / DB_NAME from the environment
(or uses sensible defaults), so the same script works locally and in CI.

Usage:
    python scripts/setup_db.py
"""
import os
import pymysql

HOST = os.environ.get('DB_HOST', '127.0.0.1')
PORT = int(os.environ.get('DB_PORT', 3306))
USER = os.environ.get('DB_USER', 'root')
PASSWORD = os.environ.get('DB_PASSWORD', '')
DB_NAME = os.environ.get('DB_NAME', 'ccmc_ham')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def run_sql_file(conn, path):
    with open(path, 'r', encoding='utf-8-sig') as f:
        sql = f.read()
    with conn.cursor() as cur:
        cur.execute(sql)
        # Consume any remaining result sets from multi-statement execution.
        while cur.nextset():
            pass


def main():
    conn_kwargs = {
        'host': HOST,
        'port': PORT,
        'user': USER,
        'password': PASSWORD,
        'charset': 'utf8mb4',
        'client_flag': pymysql.constants.CLIENT.MULTI_STATEMENTS,
    }
    ca_path = os.environ.get('DB_SSL_CA')
    if ca_path:
        conn_kwargs['ssl'] = {'ca': ca_path}
    elif os.environ.get('DB_SSL') == '1':
        conn_kwargs['ssl'] = {}
    conn = pymysql.connect(**conn_kwargs)
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        conn.select_db(DB_NAME)
        run_sql_file(conn, os.path.join(BASE_DIR, '..', 'sql', 'ccmc_create_database.sql'))
        run_sql_file(conn, os.path.join(BASE_DIR, '..', 'sql', 'ccmc_populate_database.sql'))
        conn.commit()
    finally:
        conn.close()
    print(f"Database '{DB_NAME}' is ready (schema + seed data imported).")


if __name__ == '__main__':
    main()