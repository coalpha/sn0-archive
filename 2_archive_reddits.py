import sys
import _config
from bridge import *

class sleeping_printer_stream:
   def __init__(self, stream = sys.stdout):
      self.stream = stream
      self.linebuffer = ""

   def write(self, s: str):
      lines = s.split("\n")
      for line in lines[:-1]:
         to_be_printed = self.linebuffer + line + "\n"
         if to_be_printed.startswith("Sleeping:"):
            self.stream.write("PRAW " + to_be_printed)
         self.linebuffer = ""
      self.linebuffer = lines[-1]

import logging
handler = logging.StreamHandler(sleeping_printer_stream())
handler.setLevel(logging.DEBUG)
logger = logging.getLogger("prawcore")
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

reddit = praw.Reddit(
   username=_config.USERNAME,
   password=_config.PASSWORD,
   client_id=_config.CLIENT_ID,
   user_agent=_config.USER_AGENT,
   client_secret=_config.CLIENT_SECRET,
)
assert(reddit.read_only == False)

me = cast(Redditor, reddit.user.me())
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
   archive_comment_forest(s.comments, ctx.descend())

def fetch_comment_forest(f: CommentForest, ctx: ambient_context) -> list[Comment]:
   requests_made = 0
   comments_fetched = 0

   if _config.MORECOMMENTS_LIMIT is None:
      request_limit = float("inf")
      should_print_request = True
   else:
      request_limit = _config.MORECOMMENTS_LIMIT
      should_print_request = True

   if _config.COMMENT_LIMIT is None:
      comment_limit = float("inf")
      should_print_comment_fetch = False
   else:
      comment_limit = _config.COMMENT_LIMIT
      should_print_comment_fetch = True

   mixed_queue: list[Commenty] = f._comments[:]
   output: list[Comment] = []

   while mixed_queue:
      mixed = mixed_queue.pop(0)
      if isinstance(mixed, MoreComments):
         m = mixed
         requests_made += 1
         if requests_made > request_limit:
            continue
         if should_print_request:
            ctx.print(f"| m/{requests_made}/{request_limit}")
         for subcomment in cast(Iterable[Commenty], m.comments()):
            mixed_queue.append(subcomment)
      elif isinstance(mixed, Comment):
         c = mixed
         comments_fetched += 1
         if comments_fetched > comment_limit:
            break
         if should_print_comment_fetch:
            ctx.print(f"| c/{comments_fetched}/{comment_limit}")
         output.append(c)
         for reply in cast(Iterable[Commenty], c.replies):
            mixed_queue.append(reply)
      else:
         raise TypeError(f"SANITY: Unexpected non-comment {type(mixed).__name__}")

   return output

# breadth first archiving... sorta
def archive_comment_forest(f: CommentForest, ctx: ambient_context):
   comments_archived = 0
   comments = fetch_comment_forest(f, ctx)
   ctx.print(f"| q/{len(comments)}")

   unarchived_comments = [c for c in comments if not db.has_comment(c)]
   for c in unarchived_comments:
      if not c._fetched:
         raise RuntimeError("SANITY: All comments should be fetched")
   comments_archived = len(comments) - len(unarchived_comments)

   author_fullnames = set()
   for c in unarchived_comments:
      try:
         if not db._has_redditor(c.author_fullname[3:]):
            author_fullnames.add(c.author_fullname)
      except Exception:
         ...

   author_fullnames = [*author_fullnames]
   while author_fullnames:
      # batch fetch. reddit only lets me send 100 at a time
      authors = [*reddit.redditors.partial_redditors(author_fullnames[:100])]
      for author in authors:
         ctx.print(f"+ u/{author.name}")
      db.add_partial_redditors(authors)
      author_fullnames = author_fullnames[100:]

   for c in unarchived_comments:
      comments_archived += 1
      ctx.print(f"+ c/{c.id}*{comments_archived}/{len(comments)}")
      db.add_comment(c)

# archive a comment and it's parent
def archive_comment_and_parent(c: Comment, ctx: ambient_context):
   try:
      parent = c.parent()
      if isinstance(parent, Comment):
         parent_comment = parent
      else:
         parent_comment = None
   except Exception:
      parent_comment = None
   if parent_comment is not None:
      archive_comment_and_parent(parent_comment, ctx.descend())
   archive_single_comment(c, ctx.descend())

def archive_single_comment(c: Comment, ctx: ambient_context):
   # I assume the submission has already been archived
   if db.has_comment(c):
      ctx.print(f"^ c/{c.id}")
      return

   ctx.print(f"+ c/{c.id}")
   archive_redditor(c.author, ctx.descend())
   db.add_comment(c)

archive_redditor(me, ambient_context(""))

save_count = 0
for saved in cast(Iterator[CommentOrSubmission], me.saved(limit=None)):
   ctx = ambient_context("")
   if isinstance(saved, Comment):
      ctx.print(f"% c/{saved.id}")
      archive_submission(saved.submission, ctx.descend())
      # archive submission doesn't necessarily archive all the comments
      archive_comment_and_parent(saved, ctx.descend())
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
      raise TypeError(f"SANITY: Unexpected type {type(saved).__name__}")
   db.commit()
   save_count += 1

print(f"Archived {save_count} posts")
db.close()
