# Simple synthetic workload generator.

import random

def generate_basic(N = 100, filename = "trace_basic.txt"):

    with open(filename, "w") as f:
        for i in range(N):

            r = random.random()

            if r < 0.4:
                addr = random.randint(0, 1024) * 4
                f.write(f"LOAD {hex(addr)}\n")

            elif r < 0.6:
                addr = random.randint(0, 1024) * 4
                f.write(f"STORE {hex(addr)}\n")

            elif r < 0.8:
                outcome = random.choice(["T", "N"])
                f.write(f"BRANCH {outcome}\n")

            else:
                f.write("ALU\n")
