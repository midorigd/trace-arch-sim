# Generates a branch-heavy synthetic workflow, consisting of a mix of predictable and random patterns.

import random

N = 20000

with open("trace_branch.txt", "w") as f:

    for i in range(N):

        if random.random() < 0.7:

            # predictable loop-like pattern
            if i % 10 != 9:
                f.write("BRANCH T\n")
            else:
                f.write("BRANCH N\n")

        else:
            # random branch
            outcome = random.choice(["T", "N"])
            f.write(f"BRANCH {outcome}\n")
