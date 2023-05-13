import sys
import _config

from bridge import *

me_client = praw.Reddit(
   username=_config.USERNAME,
   password=_config.PASSWORD,
   client_id=_config.CLIENT_ID,
   user_agent=_config.USER_AGENT,
   client_secret=_config.CLIENT_SECRET,
)
assert(me_client.read_only == False)

me = cast(Redditor, me_client.user.me())
print(f"sn0-archive: u/{me.name}")

unsave = sys.argv[1:] == ["and", "unsave"]
if unsave:
   if input("Running in UNSAVE mode. Are you sure? [y/N]\n> ") != "y":
      print("Quitting...")
      exit(1)
   else:
      print("UNSAVING after archiving!")

class ambient_context:
   default_depth = "   "
   def __init__(self, depth: str):
      self.depth = depth
   def descend(self) -> Self:
      return ambient_context(self.depth + ambient_context.default_depth)
   def print(self, s: str):
      print(f"{self.depth}{s}")

db = bridge()

def archive_redditor(r: Redditor, ctx: ambient_context):
   """
   This is a leaf archiver.
   """
   if r is None:
      ctx.print("^ u/[deleted]")
      return

   if db.has_redditor(r):
      ctx.print(f"^ u/{r.name}")
      return

   ctx.print(f"+ u/{r.name}")
   db.add_redditor(r)

def archive_subreddit(s: Subreddit, ctx: ambient_context):
   """
   This is a leaf archiver.
   """
   if db.has_subreddit(s):
      ctx.print(f"^ r/{s.name}")
      return

   ctx.print(f"+ r/{s.name}")
   db.add_subreddit(s)

def archive_submission(s: Submission, ctx: ambient_context):
   if db.has_submission(s):
      ctx.print(f"^ s/{s.id}")
      return

   ctx.print(f"+ s/{s.id}")

   # foreign key requirements
   archive_redditor(s.author, ctx.descend())
   archive_subreddit(s.subreddit, ctx.descend())

   db.add_submission(s)
   s.comments.replace_more(limit=None)
   archive_comment_forest(s.comments, ctx.descend())

def archive_comment_forest(f: CommentForest, ctx: ambient_context):
   for c in f.list():
      if isinstance(c, MoreComments):
         raise RuntimeError("SANITY: MoreComments should have been replaced!")
      if isinstance(c, Comment):
         archive_comment(c, ctx)
      else:
         raise RuntimeError(f"SANITY: Unexpected non-comment {type(c).__name__}")

def archive_comment(c: Comment, ctx: ambient_context):
   # I assume the submission has already been archived
   if db.has_comment(c):
      ctx.print(f"^ c/{c.id}")
      return

   ctx.print(f"+ c/{c.id}")
   archive_redditor(c.author, ctx.descend())
   db.add_comment(c)

archive_redditor(me, ambient_context(""))

save_count = 0
for saved in cast(Iterator[comment_or_submission], me.saved(limit=None)):
   ctx = ambient_context("")
   if isinstance(saved, Comment):
      ctx.print(f"% c/{saved.id}")
      archive_submission(saved.submission, ctx.descend())
      if unsave:
         saved.unsave()
         ctx.print(f"- c/{saved.id}")
   elif isinstance(saved, Submission):
      ctx.print(f"% s/{saved.id}")
      archive_submission(saved, ctx.descend())
      if unsave:
         saved.unsave()
         ctx.print(f"- s/{saved.id}")
   else:
      raise RuntimeError(f"SANITY: Unexpected type {type(saved).__name__}")
   db.commit()
   save_count += 1

print(f"Archived {save_count} posts")
db.close()
