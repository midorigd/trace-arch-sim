# Generates a streaming-heavy workflow with lots of writes to nearby memory addresses.

N = 20000
addr = 0

with open("trace_stream.txt", "w") as f:

    for i in range(N):

        f.write(f"LOAD {hex(addr)}\n")

        addr += 4

        if addr > 4096:
            addr = 0
