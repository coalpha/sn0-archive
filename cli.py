import praw
import config
import dbmarshal as M

from typing import *

Models = praw.reddit.models
Comment = Models.Comment
Redditor = Models.Redditor
Subreddit = Models.Subreddit
Submission = Models.Submission
CommentOrSubmission = Union[Comment, Submission]

me_client = praw.Reddit(
   username=config.username,
   password=config.password,
   client_id=config.client_id,
   user_agent=config.user_agent,
   client_secret=config.client_secret,
)
assert(me_client.read_only == False)

me = cast(Redditor, me_client.user.me())

print(f"sn0-archive: u/{me.name}")
# for item in cast(Iterator[CommentOrSubmission], betahood.saved()):
#    if isinstance(item, Comment):
#       print(f"Comment {item.body}")
#    else:
#       print("Submission ", item)

def archive_redditor(r: Redditor):
   if M.have_redditor(r.id):
      print(f"   ^ u/{r.name}")
   else:
      print(f"   + u/{r.name}")
      M.add_redditor(
         id=r.id,
         name=r.name,
         created_utc=r.created_utc,
         icon_img=r.icon_img,
      )

def archive_subreddit(s: Subreddit):
   ...

def archive_comment(c: Comment):
   pass

def archive_submission(s: Submission):
   pass

archive_redditor(me)
M.close()
