import sys
import praw
import asyncio

from typing import *
from praw.models import Comment, Redditor, Subreddit, Submission, MoreComments
from praw.models.redditors import PartialRedditor
from praw.models.comment_forest import CommentForest

CommentOrSubmission = Union[Comment, Submission]
Commenty = Union[Comment, MoreComments]

class Threadpool:
   """
   It's not *actually* a thread pool, I don't think but it sorta feels like one?
   """
   def __init__(self, count: int):
      if count < 1:
         raise ValueError("count must be at least 1!")
      self.count = count
      self.pool: list[Optional[asyncio.Task]] = [None] * count

   def __try_free_none(self) -> int:
      for i in range(0, self.count):
         if self.pool[i] is None:
            return i
      return -1

   # returns the next free thread_id
   async def next(self) -> int:
      maybe_worked = self.__try_free_none()
      if maybe_worked != -1:
         return maybe_worked

      await asyncio.wait(self.pool, return_when="FIRST_COMPLETED")
      for i in range(0, self.count):
         if self.pool[i].done():
            return i

      raise RuntimeError("SANITY: If we're here, somehow we waited for a task to complete but it un-completed?")

   def enqueue_at(self, id: int, co: Coroutine):
      self.pool[id] = asyncio.create_task(co)

   async def close(self):
      remaining_tasks = [task for task in self.pool if task is not None and not task.done()]
      if remaining_tasks:
         await asyncio.wait(remaining_tasks, return_when="ALL_COMPLETED")
      for i in range(0, self.count):
         self.pool[i] = None

class SleepingPrinterStream:
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
