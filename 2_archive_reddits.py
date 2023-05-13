import db
import sys
import praw
import config

from typing import *

Models = praw.reddit.models
Comment = Models.Comment
Redditor = Models.Redditor
Subreddit = Models.Subreddit
Submission = Models.Submission
MoreComments = Models.MoreComments
CommentForest = Iterable[Comment]
CommentOrSubmission = Union[Comment, Submission]

me_client = praw.Reddit(
   username=config.username,
   password=config.password,
   client_id=config.client_id,
   user_agent=config.user_agent,
   client_secret=config.client_secret,
)
assert(me_client.read_only == False)

if len(sys.argv) == 3 and sys.argv[1] == "and" and sys.argv[2] == "unsave":
   unsave = True
else:
   unsave = False

me = cast(Redditor, me_client.user.me())
print(f"sn0-archive: u/{me.name}")
if unsave:
   if input("Running in UNSAVE mode. Are you sure? [y/N]\n> ") != "y":
      print("Quitting...")
      exit(1)
   else:
      print("UNSAVING after archiving!")
ddepth = "   "

conn = db.open()
def have_redditor(r: Redditor) -> bool:
   try:
      return bool(
         conn
            .execute("select exists(select * from redditors where id = ?)", (r.id,))
            .fetchone()[0]
      )
   except Exception:
      return True
def add_redditor(r: Redditor):
   conn.execute(
      """
      insert into
         redditors (id, name, created_utc, icon_img)
         values (?, ?, ?, ?)
      """,
      [r.id, r.name, r.created_utc, r.icon_img],
   )
   conn.commit()

def have_subreddit(s: Subreddit) -> bool:
   return bool(
      conn
         .execute("select exists(select * from subreddits where id = ?)", (s.id,))
         .fetchone()[0]
   )
def add_subreddit(s: Subreddit) -> bool:
   conn.execute(
      """
      insert into subreddits (
         id,
         created_utc,
         description,
         display_name,
         name,
         over18,
         public_description,
         subscriber_count
      ) values (
         ?,
         ?,
         ?,
         ?,
         ?,
         ?,
         ?,
         ?
      )
      """,
      [
         s.id,
         s.created_utc,
         s.description,
         s.display_name,
         s.name,
         s.over18,
         s.public_description,
         s.subscribers,
      ],
   )
   conn.commit()

def have_submission(s: Submission) -> bool:
   return bool(
      conn
         .execute("select exists(select * from submissions where id = ?)", (s.id,))
         .fetchone()[0]
   )
def add_submission(s: Submission):
   is_gallery = False
   try:
      author_id = s.author.id
   except Exception:
      author_id = None
   try:
      if s.is_gallery:
         is_gallery = True
   except Exception:
      ...
   conn.execute(
      """
      insert into submissions (
         id,
         author,
         author_flair_text,
         created_utc,
         distinguished,
         edited,
         is_gallery,
         is_original_content,
         is_selfpost,
         link_flair_text,
         name,
         comment_count,
         over_18,
         permalink,
         saved,
         score,
         selftext,
         spoiler,
         stickied,
         subreddit,
         title,
         upvote_ratio,
         url
      ) values (
         ?,
         ?,
         ?,
         ?,
         ?,
         ?,
         ?,
         ?,
         ?,
         ?,
         ?,
         ?,
         ?,
         ?,
         ?,
         ?,
         ?,
         ?,
         ?,
         ?,
         ?,
         ?,
         ?
      )
      """,
      [
         s.id,
         author_id,
         s.author_flair_text,
         s.created_utc,
         bool(s.distinguished),
         s.edited,
         is_gallery,
         s.is_original_content,
         s.is_self,
         s.link_flair_text,
         s.name,
         s.num_comments,
         s.over_18,
         s.permalink,
         s.saved,
         s.score,
         s.selftext,
         s.spoiler,
         s.stickied,
         s.subreddit.id,
         s.title,
         s.upvote_ratio,
         s.url,
      ]
   )
   conn.commit()

def have_comment(c: Comment) -> bool:
   return bool(
      conn
         .execute("select exists(select * from comments where id = ?)", (c.id,))
         .fetchone()[0]
   )
def add_comment(c: Comment):
   parent_comment = c.parent()
   if isinstance(parent_comment, Comment):
      parent_id = parent_comment.id
   else:
      parent_id = None
   author_id = None
   try:
      author_id = c.author.id
   except Exception:
      ...
   conn.execute(
      """
      insert into comments (
         id,
         author,
         author_flair_text,
         created_utc,
         body,
         distinguished,
         edited,
         is_op,
         parent_comment,
         permalink,
         saved,
         score,
         stickied,
         submission
      ) values (
         ?,
         ?,
         ?,
         ?,
         ?,
         ?,
         ?,
         ?,
         ?,
         ?,
         ?,
         ?,
         ?,
         ?
      )
      """,
      [
         c.id,
         author_id,
         c.author_flair_text,
         c.created_utc,
         c.body,
         bool(c.distinguished),
         c.edited,
         c.is_submitter,
         parent_id,
         c.permalink,
         c.saved,
         c.score,
         c.stickied,
         c.submission.id
      ]
   )
   conn.commit()

def archive_redditor(r: Redditor, depth: str):
   if r is None:
      print(f"{depth}^ u/[deleted]")
   elif have_redditor(r):
      print(f"{depth}^ u/{r.name}")
   else:
      print(f"{depth}+ u/{r.name}")
      try:
         add_redditor(r)
      except Exception as e:
         print(f"Couldn't add u/{r.name}!")
         raise e

def archive_subreddit(s: Subreddit, depth: str):
   if have_subreddit(s):
      print(f"{depth}^ r/{s.name}")
   else:
      print(f"{depth}+ r/{s.name}")
      try:
         add_subreddit(s)
      except Exception as e:
         print(f"Couldn't add u/{s.name}!")
         raise e

def archive_submission(s: Submission, depth: str):
   if have_submission(s):
      print(f"{depth}^ s/{s.id}")
   else:
      print(f"{depth}+ s/{s.id}")
      depth += ddepth
      archive_redditor(s.author, depth)
      archive_subreddit(s.subreddit, depth)
      try:
         add_submission(s)
      except Exception as e:
         print(f"Couldn't add s/{s.id}!")
         raise e
      archive_comment_forest(s.comments, depth)

def archive_comment_forest(f: CommentForest, depth: str):
   for c in f:
      archive_comment(c, depth)

def archive_comment(c: Union[Comment, MoreComments], depth: str):
   # I assume the submission has already been archived
   if isinstance(c, Comment):
      if have_comment(c):
         print(f"{depth}^ c/{c.id}")
      else:
         print(f"{depth}+ c/{c.id}")
         depth += ddepth
         archive_redditor(c.author, depth)
         try:
            add_comment(c)
         except Exception as e:
            print(f"Couldn't add c/{c.id}!")
            raise e
         archive_comment_forest(c.replies, depth)

archive_redditor(me, ddepth)

for item in cast(Iterator[CommentOrSubmission], me.saved()):
   depth = ddepth
   if isinstance(item, Comment):
      print(f"{depth}% c/{item.id}")
      archive_submission(item.submission, depth + ddepth)
      # sometimes archiving the entire submission won't get the comment
      # because of the MoreComments thing
      archive_comment(item, depth + ddepth)
      if unsave:
         item.unsave()
         print(f"{depth}- c/{item.id}")
   elif isinstance(item, Submission):
      print(f"{depth}% s/{item.id}")
      archive_submission(item, depth + ddepth)
      if unsave:
         item.unsave()
         print(f"{depth}- s/{item.id}")
   else:
      print(f"{ddepth}???/{type(item).__name__}")
   conn.commit()

db.close(conn)
