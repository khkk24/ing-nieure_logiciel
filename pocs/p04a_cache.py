"""Single-flight local : un calcul partagé par 32 requêtes simultanées."""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Lock
from .common import check


class Cache:
    def __init__(self):
        self.lock = Lock()
        self.value = None
        self.expires = 0
        self.reads = 0

    def get(self, now):
        # Verrou global acceptable pour cette clé unique de démonstration.
        with self.lock:
            if self.value is None or now >= self.expires:
                self.reads += 1
                self.value = {"catalogue_version": self.reads}
                self.expires = now + 10
            return dict(self.value)


def run():
    cache = Cache()
    start = Barrier(32)

    def request(_):
        start.wait(timeout=10)
        return cache.get(0)

    with ThreadPoolExecutor(max_workers=32) as pool:
        values = list(pool.map(request, range(32)))
    first_reads = cache.reads
    refreshed = cache.get(11)
    check(first_reads == 1 and cache.reads == 2 and len(values) == 32, "Cache stampede")
    return {"lectures_sans_cache": 32, "lectures_avec_cache": first_reads,
            "apres_expiration": refreshed, "portee": "un processus et une clé"}
