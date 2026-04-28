def parse_trace(filename):

    with open(filename) as f:
        for line in f:
            parts = line.strip().split()

            inst = parts[0]

            if inst in ("LOAD", "STORE"):
                addr = int(parts[1], 16)
                yield (inst, addr)

            elif inst == "BRANCH":
                outcome = parts[1]
                yield (inst, outcome)

            else:
                yield (inst, None)
