import praw
from praw.models import Comment, Redditor, Subreddit, Submission, MoreComments
from praw.models.comment_forest import CommentForest
from typing import *

comment_or_submission = Union[Comment, Submission]
