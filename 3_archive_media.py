import os
import _config
import asyncio
from typing import *
from threadpool import *

conn = db.open()

async def gallery_dl(outdir: str, url: str, thread_id: int):
   process = await asyncio.create_subprocess_exec(
      _config.gallery_dl_command,
      "-D", outdir,
      url.replace('"', r'\"'),
      stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
   )

   stdout, stderr = await process.communicate()

   for line in stdout.decode().splitlines():
      print(f"[{thread_id}] {line}")
   for line in stderr.decode().splitlines():
      print(f"[{thread_id}] {line}")

# archive reddit profile pictures
async def archive_reddit_icon_img():
   pool = threadpool(_config.ICON_IMG_THREADS)
   data = conn.execute("select id, icon_img from redditors").fetchall()

   for (reddit_id, icon_img) in data:
      outdir = f"{_config.media_path}/redditors/{reddit_id}"
      if os.path.exists(outdir):
         print(f"^ {reddit_id}")
      else:
         thread_id = await pool.next()
         pool.enqueue_at(thread_id, gallery_dl(outdir, icon_img, thread_id))

async def archive_submission_media():
   pool = threadpool(_config.SUBMISSION_MEDIA_THREADS)
   data = conn.execute("select id, permalink from submissions").fetchall()

   for (submission_id, permalink) in data:
      outdir = f"{_config.media_path}/submissions/{submission_id}"
      if os.path.exists(outdir):
         print(f"^ {submission_id}")
      else:
         reddit_link = f"https://reddit.com{permalink}"
         thread_id = await pool.next()
         pool.enqueue_at(thread_id, gallery_dl(outdir, reddit_link, thread_id))

async def main():
   await archive_reddit_icon_img()
   await archive_submission_media()

asyncio.run(main())
