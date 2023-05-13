import _config
import sqlite3

from sup import *

class bridge(sqlite3.Connection):
   def __init__(self):
      super(_config.SN0_DB_PATH)
      self.execute("pragma foreign_keys = on")

   def close(self):
      self.execute("pragma vacuum")
      self.execute("pragma optimize")
      super().close()

   def has_redditor(self, r: Optional[Redditor]) -> bool:
      try:
         # handles r = None
         # handles r.id missing
         reddit_id = r.id
      except Exception:
         return True
      return bool(
         self
            .execute("select exists(select * from redditors where id = ?)", (reddit_id,))
            .fetchone()[0]
      )
   def add_redditor(self, r: Redditor):
      if r is None:
         raise RuntimeError("SANITY: Cannot add None as Redditor!")
      try:
         reddit_id = r.id
         name = r.name
      except Exception as e:
         raise RuntimeError("Redditor object lacks crucial attrs!") from e
      try:
         self.execute(
            """
            insert into
               redditors (id, name, created_utc, icon_img)
               values (?, ?, ?, ?)
            """,
            [reddit_id, name, r.created_utc, r.icon_img],
         )
      except Exception as e:
         raise RuntimeError(f"Couldn't add u/{name} ({reddit_id})!") from e
   def has_subreddit(self, s: Subreddit) -> bool:
      return bool(
         self
            .execute("select exists(select * from subreddits where id = ?)", (s.id,))
            .fetchone()[0]
      )
   def add_subreddit(self, s: Subreddit) -> bool:
      self.execute(
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
   def has_submission(self, s: Submission) -> bool:
      return bool(
         self
            .execute("select exists(select * from submissions where id = ?)", (s.id,))
            .fetchone()[0]
      )
   def add_submission(self, s: Submission):
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
      self.execute(
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
   def has_comment(self, c: Comment) -> bool:
      return bool(
         self
            .execute("select exists(select * from comments where id = ?)", (c.id,))
            .fetchone()[0]
      )
   def add_comment(self, c: Comment):
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
      self.execute(
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
