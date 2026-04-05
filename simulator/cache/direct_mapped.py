class DirectMappedCache:

    def __init__(self, size, block_size):
        self.size = size
        self.block_size = block_size

        self.rows = size // block_size

        self.valid = [False] * self.rows
        self.tags = [0] * self.rows

        self.hits = 0
        self.misses = 0

    def access(self, addr):
        block_id = addr // self.block_size
        index = block_id % self.rows
        tag = block_id // self.rows

        if self.valid[index] and self.tags[index] == tag:
            self.hits += 1
            return True
        
        else:
            self.misses += 1
            self.valid[index] = True
            self.tags[index] = tag
            return False
