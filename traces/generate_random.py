# Generates a random access-heavy workload, consisting of reads/writes to random addresses.

import random

N = 20000

with open("trace_random.txt", "w") as f:

    for i in range(N):

        addr = random.randint(0, 65536)

        if random.random() < 0.5:
            f.write(f"LOAD {hex(addr)}\n")
        else:
            f.write(f"STORE {hex(addr)}\n")
