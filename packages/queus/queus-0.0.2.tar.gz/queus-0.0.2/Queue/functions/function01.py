import asyncio
from .function02 import Queues
from ..exceptions import QueuedAlready
#================================================================================================

class Queue:

    def __init__(self, **kwargs):
        self.waiting = kwargs.get("wait", 1)
        self.workers = kwargs.get("workers", 1)
        self.maxsize = kwargs.get("maxsize", 100)
        self.storage = kwargs.get("storage", Queues)

#================================================================================================

    async def total(self):
        return len(self.storage)

    async def remove(self, uid):
        self.storage.remove(uid) if uid in self.storage else 0

    async def clean(self, uid=None):
        self.storage.remove(uid) if uid else self.storage.clear()

    async def position(self, uid):
        return self.storage.index(uid) - self.workers + 1 if uid in self.storage else 0
    
    async def add(self, uid, priority=-1):
        if uid in self.storage: raise QueuedAlready()
        self.storage.append(uid) if priority == -1 else self.storage.insert(priority, uid)

#================================================================================================
    
    async def message(self, uid, imog, text, button=None):
        if self.storage.index(uid) >= self.workers:
            try: await imog.edit(text=text, reply_markup=button)
            except Exception: pass

#================================================================================================

    async def queue(self, uid):
        while uid in self.storage:
            if self.storage.index(uid) >= self.workers: await asyncio.sleep(self.waiting)
            else: break

#================================================================================================
