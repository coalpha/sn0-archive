import os
import _config
from sup import *
from bridge import bridge

db = bridge()

async def gallery_dl(outdir: str, url: str, thread_id: int):
   process = await asyncio.create_subprocess_exec(
      _config.GALLERY_DL_COMMAND,
      "-D", outdir,
      url.replace('"', r'\"'),
      stdout=asyncio.subprocess.PIPE,
      stderr=asyncio.subprocess.PIPE
   )

   print(f"[{thread_id}] $ {_config.GALLERY_DL_COMMAND} {url}")

   async def pipe_stdout():
      while True:
         line = await process.stdout.readline()
         if line:
            print(f"[{thread_id}] : {line.decode().strip()}")
         else:
            break

   async def pipe_stderr():
      while True:
         line = await process.stderr.readline()
         if line:
            print(f"[{thread_id}] ! {line.decode().strip()}")
         else:
            break

   await asyncio.gather(pipe_stdout(), pipe_stderr())

   code = await process.wait()
   print(f"[{thread_id}] = {code}")

# archive reddit profile pictures
async def archive_reddit_icon_img():
   pool = threadpool(_config.ICON_IMG_THREADS)
   data = db.execute("select id, icon_img, name from redditors").fetchall()

   for (reddit_id, icon_img, name) in data:
      outdir = f"{_config.MEDIA_PATH}/redditors/{reddit_id}"
      if os.path.exists(outdir):
         print(f"[*] ^ u/{name}")
      else:
         thread_id = await pool.next()
         pool.enqueue_at(thread_id, gallery_dl(outdir, icon_img, thread_id))

async def archive_submission_media():
   pool = threadpool(_config.SUBMISSION_MEDIA_THREADS)
   data = db.execute("select id, permalink from submissions").fetchall()

   for (submission_id, permalink) in data:
      outdir = f"{_config.MEDIA_PATH}/submissions/{submission_id}"
      if os.path.exists(outdir):
         print(f"[*] ^ {submission_id}")
      else:
         reddit_link = f"https://reddit.com{permalink}"
         thread_id = await pool.next()
         pool.enqueue_at(thread_id, gallery_dl(outdir, reddit_link, thread_id))

async def main():
   await archive_reddit_icon_img()
   await archive_submission_media()

asyncio.run(main())
