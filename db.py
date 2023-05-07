from sqlite3 import *
from config import sn0_path

def open() -> Connection:
   conn = connect(sn0_path)
   conn.execute("pragma synchronous = normal;")
   conn.execute("pragma foreign_keys = on;")
   return conn

def close(conn: Connection):
   conn.execute("pragma vacuum;")
   conn.execute("pragma optimize;")
   conn.close()
