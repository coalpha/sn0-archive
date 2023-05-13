import db
import os
import config
import asyncio
from typing import *
from threadpool import *

conn = db.open()

async def gallery_dl(outdir: str, url: str, thread_id: int):
   process = await asyncio.create_subprocess_exec(
      config.gallery_dl_command,
      "-D", outdir,
      url.replace('"', r'\"'),
      stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
   )

   stdout, stderr = await process.communicate()

   for line in stdout.decode().splitlines():
      print(f"[{thread_id}] {line}")
   for line in stderr.decode().splitlines():
      print(f"[{thread_id}] {line}")

   return thread_id

# archive reddit profile pictures
ICON_IMG_THREADS = 3
async def archive_reddit_icon_img():
   pool = threadpool(ICON_IMG_THREADS)
   data = conn.execute("select id, icon_img from redditors").fetchall()

   for (reddit_id, icon_img) in data:
      outdir = f"{config.media_path}/redditors/{reddit_id}"
      if os.path.exists(outdir):
         print(f"^ {reddit_id}")
      else:
         pool.enqueue(gallery_dl(outdir, icon_img, i))

asyncio.run(archive_reddit_icon_img())

# archive posts
for (submission_id, permalink) in conn.execute("select id, permalink from submissions").fetchall():
   d = f"{config.media_path}/submissions/{submission_id}"
   if os.path.exists(d):
      print(f"^ {submission_id}")
   else:
      os.system(f'gallery-dl -D {d} "https://reddit.com{escape(permalink)}"')
