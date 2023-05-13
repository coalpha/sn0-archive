import asyncio
from typing import *

class threadpool:
   def __init__(self, count: int):
      if count < 1:
         raise ValueError("count must be at least 1!")
      self.count = count
      self.pool: list[Optional[asyncio.Task]] = [None] * count

   def __try_replacing_none(self, co: Coroutine) -> int:
      for i in range(0, self.count):
         if self.pool[i] is None:
            self.pool[i] = asyncio.create_task(co)
            return i
      return -1

   async def enqueue(self, co: Coroutine) -> int:
      maybe_worked = self.__try_replacing_none(co)
      if maybe_worked != -1:
         return maybe_worked

      await asyncio.wait(threadpool, return_when=asyncio.FIRST_COMPLETED)
      for i in range(0, self.count):
         if self.pool[i].done():
            self.pool[i] = asyncio.create_task(co)
            return i

      raise RuntimeError("SANITY: If we're here, somehow we waited for a task to complete but it un-completed?")
