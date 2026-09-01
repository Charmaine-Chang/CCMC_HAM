"""MySQL 数据库连接 (PyMySQL)"""
import pymysql
from flask import g
from . import connect_local as connect

DatabaseError = pymysql.err.DatabaseError
IntegrityError = pymysql.err.IntegrityError


def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(
            user=connect.dbuser,
            password=connect.dbpass,
            host=connect.dbhost,
            port=int(connect.dbport),
            db=connect.dbname,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,
            charset='utf8mb4',
        )
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

