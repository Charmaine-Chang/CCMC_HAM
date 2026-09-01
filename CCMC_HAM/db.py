"""MySQL database connection (PyMySQL)."""
import os
import pymysql
from flask import g

try:
    from . import connect_local as connect
except ImportError:
    connect = None

DatabaseError = pymysql.err.DatabaseError
IntegrityError = pymysql.err.IntegrityError


def _cfg(env_name, attr, default):
    """Read a setting from the environment, falling back to connect_local / default."""
    value = os.environ.get(env_name)
    if value is not None:
        return value
    if connect is not None:
        return getattr(connect, attr, default)
    return default


def _ssl_config():
    """Optional TLS settings for managed/cloud MySQL (e.g. TiDB Cloud Serverless)."""
    ca_path = os.environ.get('DB_SSL_CA')
    if ca_path:
        return {'ca': ca_path}
    if os.environ.get('DB_SSL') == '1':
        return {}
    return None


def get_db_config():
    """Return database connection settings (env vars > connect_local.py > defaults)."""
    cfg = {
        'user': _cfg('DB_USER', 'dbuser', 'root'),
        'password': _cfg('DB_PASSWORD', 'dbpass', ''),
        'host': _cfg('DB_HOST', 'dbhost', '127.0.0.1'),
        'port': int(_cfg('DB_PORT', 'dbport', 3306)),
        'db': _cfg('DB_NAME', 'dbname', 'ccmc_ham'),
    }
    ssl = _ssl_config()
    if ssl is not None:
        cfg['ssl'] = ssl
    return cfg


def get_db():
    if 'db' not in g:
        cfg = get_db_config()
        conn_kwargs = {
            'user': cfg['user'],
            'password': cfg['password'],
            'host': cfg['host'],
            'port': cfg['port'],
            'db': cfg['db'],
            'cursorclass': pymysql.cursors.DictCursor,
            'autocommit': False,
            'charset': 'utf8mb4',
        }
        if 'ssl' in cfg:
            conn_kwargs['ssl'] = cfg['ssl']
        g.db = pymysql.connect(**conn_kwargs)
    return g.db


def get_cursor():
    return get_db().cursor()


from contextlib import contextmanager


@contextmanager
def get_cursor_context():
    conn = get_db()
    cur = conn.cursor()
    try:
        yield cur
    finally:
        cur.close()


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_app(app):
    app.teardown_appcontext(close_db)