import db
import os.path

def make_old_db(v: int) -> str:
   return f"{db.sn0_path}.{v}.old"

max_old_dbs = 4
def rename_version_if_exists(v: int = 1):
   maybe_old_db = make_old_db(v)
   if os.path.isfile(maybe_old_db):
      if v > max_old_dbs:
         os.unlink(maybe_old_db)
      else:
         rename_version_if_exists(v + 1)
         os.rename(maybe_old_db, make_old_db(v + 1))

if os.path.isfile(db.sn0_path):
   rename_version_if_exists(1)
   os.rename(db.sn0_path, make_old_db(1))

schema = open("schema.sql")
conn = db.open()
conn.executescript(schema.read())
db.close(conn)
schema.close()
