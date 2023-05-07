from typing import *
import praw
import json5

Models = praw.reddit.models
Comment = Models.Comment
Redditor = Models.Redditor
Submission = Models.Submission
CommentOrSubmission = Union[Comment, Submission]

betahood_auth = praw.Reddit(
   client_id="IWSgQc8hutQhcA",
   client_secret="fjQV3VNBcQR_gec_3imF8CPzeP71Rw",
   password="__aeeeieeeeeee__1",
   user_agent="snoo-archiver",
   username="Betahood",
)

print(betahood_auth.read_only)

betahood = cast(Redditor, betahood_auth.user.me())

for item in cast(Iterator[CommentOrSubmission], betahood.saved()):
   if isinstance(item, Comment):
      print(f"Comment {item.body}")
   else:
      print("Submission ", item)

def archive_comment(c: Comment):
   pass

def archive_submission(s: Submission):
   pass
