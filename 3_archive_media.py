import os
import db
import config

conn = db.open()

def escape(s: str):
   return s.replace('"', r'\"')

# archive reddit profile pictures
for (reddit_id, icon_img) in conn.execute("select id, icon_img from redditors").fetchall():
   d = f"{config.media_path}/redditors/{reddit_id}"
   if os.path.exists(d):
      print(f"^ {reddit_id}")
   else:
      os.system(f'gallery-dl -D {d} "{escape(icon_img)}"')

# archive posts
for (submission_id, permalink) in conn.execute("select id, permalink from submissions").fetchall():
   d = f"{config.media_path}/submissions/{submission_id}"
   if os.path.exists(d):
      print(f"^ {submission_id}")
   else:
      os.system(f'gallery-dl -D {d} "https://reddit.com{escape(permalink)}"')
