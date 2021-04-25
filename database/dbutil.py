import psycopg2
from psycopg2 import sql
import sys

conn = None
current_requests = 0

USER_QUERY = """
SELECT cr.login, cr.password, u.firstname, u.lastname 
FROM {siteuser} u JOIN {sitecredential} cr ON cr.user=u.id
WHERE cr.login=%s
"""


def connect_db(config):
    global conn, current_requests
    if conn is None:
        conn = psycopg2.connect(
            host=config['DATABASE']['pgsql_host'],
            user=config['DATABASE']['pgsql_user'],
            password=config['DATABASE']['pgsql_password'],
            database=config['DATABASE']['pgsql_db'],
            port=config['DATABASE']['pgsql_port']
        )
    current_requests = current_requests + 1
    return conn


def get_user(username):
    global conn
    cursor = conn.cursor()
    query = sql.SQL(USER_QUERY).format(
        siteuser=sql.Identifier('siteuser'),
        sitecredential=sql.Identifier('sitecredential')
    )
    cursor.execute(query, [username])
    res = cursor.fetchone()
    if res is None:
        return {
            'error': 'User not found.'
        }
    return {
        'username': res[0],
        'password': res[1],
        'firstname': res[2],
        'lastname': res[3]
    }


def maybe_close_conn(config, force):
    global conn, current_requests
    if conn is not None \
            and (current_requests > int(config['DATABASE']['requests_before_close'])
                 or force):
        print("closing DB conn", file=sys.stderr)
        conn.close()
    current_requests = 0
