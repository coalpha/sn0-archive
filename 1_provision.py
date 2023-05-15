import os.path
import _config

def make_old_db(v: int) -> str:
   return f"{_config.SN0_DB_PATH}.{v}.old"

max_old_dbs = 4
def rename_version_if_exists(v: int = 1):
   maybe_old_db = make_old_db(v)
   if os.path.isfile(maybe_old_db):
      if v > max_old_dbs:
         os.unlink(maybe_old_db)
      else:
         rename_version_if_exists(v + 1)
         os.rename(maybe_old_db, make_old_db(v + 1))

if os.path.isfile(_config.SN0_DB_PATH):
   rename_version_if_exists(1)
   os.rename(_config.SN0_DB_PATH, make_old_db(1))

schema = open("schema.sql")

from bridge import bridge
conn = bridge()
conn.executescript(schema.read())
conn.close()
schema.close()
