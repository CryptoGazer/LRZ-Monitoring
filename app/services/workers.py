import asyncio
from typing import Iterable, List, Optional, Callable, Awaitable
from datetime import datetime, timedelta, timezone


class Workers:
    def __init__(
        self,
        tags: Iterable[str],
        parse_fn: Callable[[str], Awaitable[object]],  # function to get stats from HTML-tags
        save_fn: Callable[[str, object], Awaitable[None]],  # function to save data to the db
    ):
        self.tags = list(tags)
        self.parse_fn = parse_fn
        self.save_fn = save_fn

        self._tasks: List[asyncio.Task] = []
        self._stop = asyncio.Event()

    async def start(self) -> None:
        self._stop.clear()
        for tag in self.tags:
            t = asyncio.create_task(self._worker_loop(tag), name=f"parser:{tag}")
            self._tasks.append(t)

    async def stop(self) -> None:
        self._stop.set()
        for t in self._tasks:
            t.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()

    async def _worker_loop(self, tag: str) -> None:
        while not self._stop.is_set():
            now = datetime.now(timezone.utc)
            ts_slot = now.replace(second=0, microsecond=0)

            try:
                data = await self.parse_fn(tag)
                await self.save_fn(tag, data, ts_slot)  # TODO: implement save_fn(tag, data, ts_slot)
            except Exception as e:
                print(f"[{tag}] worker error: {e}")

            now2 = datetime.now(timezone.utc)
            next_minute = now2.replace(second=0, microsecond=0) + timedelta(minutes=1)
            sleep_sec = (next_minute - now2).total_seconds()

            try:
                await asyncio.wait_for(self._stop.wait(), timeout=sleep_sec)
            except asyncio.TimeoutError:
                pass
