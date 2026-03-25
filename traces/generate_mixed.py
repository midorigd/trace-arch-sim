# Generates a mixed-use workload for more realistic simulation of real-world workloads.

import random

N = 20000

with open("trace_mixed.txt", "w") as f:

    addr = 0

    for i in range(N):

        r = random.random()

        if r < 0.4:

            addr += 4
            f.write(f"LOAD {hex(addr)}\n")

        elif r < 0.6:

            addr = random.randint(0, 8192)
            f.write(f"STORE {hex(addr)}\n")

        elif r < 0.85:

            if i % 8 != 7:
                f.write("BRANCH T\n")
            else:
                f.write("BRANCH N\n")

        else:

            f.write("ALU\n")
