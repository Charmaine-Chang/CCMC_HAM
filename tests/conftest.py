"""Shared pytest fixtures.

Creates a dedicated test database (ccmc_ham_test by default), imports the
schema + seed data, and drops it after each test so tests stay isolated.
"""
import os
import sys

import pymysql
import pytest

# Make the project root importable.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Route the app to a dedicated test database (override with TEST_DB_NAME).
os.environ['DB_NAME'] = os.environ.get('TEST_DB_NAME', 'ccmc_ham_test')

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SQL_FILES = [
    os.path.join(PROJECT_ROOT, 'sql', 'ccmc_create_database.sql'),
    os.path.join(PROJECT_ROOT, 'sql', 'ccmc_populate_database.sql'),
]


def _connect(cfg, multi_statements=False):
    kwargs = {
        'host': cfg['host'],
        'port': cfg['port'],
        'user': cfg['user'],
        'password': cfg['password'],
        'charset': 'utf8mb4',
    }
    if multi_statements:
        kwargs['client_flag'] = pymysql.constants.CLIENT.MULTI_STATEMENTS
    return pymysql.connect(**kwargs)


@pytest.fixture()
def test_db():
    from CCMC_HAM.db import get_db_config
    cfg = get_db_config()
    conn = _connect(cfg, multi_statements=True)
    try:
        with conn.cursor() as cur:
            cur.execute(f"DROP DATABASE IF EXISTS `{cfg['db']}`")
            cur.execute(
                f"CREATE DATABASE `{cfg['db']}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        conn.select_db(cfg['db'])
        for sql_file in SQL_FILES:
            with open(sql_file, 'r', encoding='utf-8-sig') as f:
                sql = f.read()
            with conn.cursor() as cur:
                cur.execute(sql)
                while cur.nextset():
                    pass
        conn.commit()
    finally:
        conn.close()
    yield cfg
    conn2 = _connect(cfg)
    try:
        with conn2.cursor() as cur:
            cur.execute(f"DROP DATABASE IF EXISTS `{cfg['db']}`")
        conn2.commit()
    finally:
        conn2.close()


@pytest.fixture()
def app(test_db):
    from CCMC_HAM import create_app
    return create_app({'TESTING': True})


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def login(client):
    def _login(username, password='Password123!'):
        return client.post('/auth/login', data={'username': username, 'password': password})
    return _login