import os
import _config
from sup import *
from bridge import bridge

db = bridge()
redditor_data = db.execute("select id, icon_img, name from redditors").fetchall()
submission_data = db.execute("select id, permalink from submissions").fetchall()
db.close()

async def gallery_dl(outdir: str, url: str, thread_id: int):
   process = await asyncio.create_subprocess_exec(
      _config.GALLERY_DL_COMMAND,
      "-D", f"{outdir}.tmp",
      url.replace('"', r'\"'),
      stdout=asyncio.subprocess.PIPE,
      stderr=asyncio.subprocess.PIPE
   )

   print(f"[{thread_id}] $ {_config.GALLERY_DL_COMMAND} {url[:80]}...")

   async def pipe_stdout():
      while True:
         line = await process.stdout.readline()
         if line:
            try:
               decoded = line.decode()
            except Exception:
               print(f"[{thread_id}]?: {str(line)[:99]}...")
            else:
               print(f"[{thread_id}] : {decoded.strip()}")
         else:
            break

   async def pipe_stderr():
      while True:
         line = await process.stderr.readline()
         if line:
            try:
               decoded = line.decode()
            except Exception:
               print(f"[{thread_id}]?! {line}")
            else:
               print(f"[{thread_id}] ! {decoded.strip()}")
         else:
            break

   await asyncio.gather(pipe_stdout(), pipe_stderr())

   code = await process.wait()

   try:
      os.rename(f"{outdir}.tmp", outdir)
   except Exception as e:
      for line in str(e).splitlines():
         print(f"[{thread_id}] ! {line}")

   print(f"[{thread_id}] = {code}")

submissions_dir = set(os.listdir(f"{_config.MEDIA_PATH}/submissions"))
async def archive_submission_media():
   pool = Threadpool(_config.SUBMISSION_MEDIA_THREADS)

   for (submission_id, permalink) in submission_data:
      if submission_id in submissions_dir:
         print(f"[*] ^ {submission_id}")
      else:
         outdir = f"{_config.MEDIA_PATH}/submissions/{submission_id}"
         reddit_link = f"https://reddit.com{permalink}"
         thread_id = await pool.next()
         pool.enqueue_at(thread_id, gallery_dl(outdir, reddit_link, thread_id))

redditors_dir = set(os.listdir(f"{_config.MEDIA_PATH}/redditors"))
async def archive_reddit_icon_img():
   pool = Threadpool(_config.ICON_IMG_THREADS)

   for (reddit_id, icon_img, name) in redditor_data:
      if reddit_id in redditors_dir:
         print(f"[*] ^ u/{name}")
      else:
         outdir = f"{_config.MEDIA_PATH}/redditors/{reddit_id}"
         thread_id = await pool.next()
         pool.enqueue_at(thread_id, gallery_dl(outdir, icon_img, thread_id + _config.SUBMISSION_MEDIA_THREADS))

async def main():
   submissions = archive_submission_media()
   icons = archive_reddit_icon_img()
   await asyncio.gather(submissions, icons)

asyncio.run(main())
print("Finished!")
