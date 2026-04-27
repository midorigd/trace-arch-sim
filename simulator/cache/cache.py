class Cache:

    def __init__(self, size, block_size, assoc):
        self.block_size = block_size
        self.associativity = assoc

        self.sets = size // block_size
        self.rows = self.sets // assoc

        self.sets = [
            [{"tag": None, "valid": False} for _ in range(assoc)]
            for _ in range(self.rows)
        ]

        self.lru = [list(range(assoc)) for _ in range(self.rows)]

        self.hits = 0
        self.misses = 0

    def access(self, addr):
        block_id = addr // self.block_size
        index = block_id % self.rows
        tag = block_id // self.rows

        cache_row = self.sets[index]

        # check for hit
        for way, line in enumerate(cache_row):
            if line["valid"] and line["tag"] == tag:

                self.hits += 1

                self.lru[index].remove(way)
                self.lru[index].append(way)

                return True

        # miss
        self.misses += 1

        evict = self.lru[index].pop(0)

        cache_row[evict]["tag"] = tag
        cache_row[evict]["valid"] = True

        self.lru[index].append(evict)

        return False
