import asyncio
import inspect

class Multiverse:
    def __init__(self):
        self.Universes = []

    async def _run_universe(self, universe, shared):
        if "Shared" in universe.__code__.co_varnames:
            if inspect.iscoroutinefunction(universe):
                return await universe(shared)
            else:
                return await asyncio.to_thread(universe, shared)
        else:
            if inspect.iscoroutinefunction(universe):
                return await universe()
            else:
                return await asyncio.to_thread(universe)

    async def _run_all(self):
        class Shared:
            pass

        shared = Shared()
        tasks = [self._run_universe(u, shared) for u in self.Universes]
        results = await asyncio.gather(*tasks)
        return tuple(results)

    def run(self):
        return asyncio.run(self._run_all())
