import db

conn = db.open()

def have_redditor(id: str) -> bool:
   return bool(
      conn
         .execute("select exists(select * from redditors where id = ?)", (id,))
         .fetchone()[0]
   )

def add_redditor(*, id: str, name: str, created_utc: int, icon_img: str):
   conn.execute("""
      insert into
         redditors (id, name, created_utc, icon_img)
         values (?, ?, ?, ?)
   """, (id, name, created_utc, icon_img))
   conn.commit()

def close():
   db.close(conn)
