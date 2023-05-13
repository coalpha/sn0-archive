import asyncio
from typing import *

class threadpool:
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

      await asyncio.wait(self.pool, return_when=asyncio.FIRST_COMPLETED)
      for i in range(0, self.count):
         if self.pool[i].done():
            return i

      raise RuntimeError("SANITY: If we're here, somehow we waited for a task to complete but it un-completed?")

   def enqueue_at(self, id: int, co: Coroutine):
      self.pool[id] = asyncio.create_task(co)
