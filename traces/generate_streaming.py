# Generates a streaming-heavy workflow with lots of writes to nearby memory addresses.

def generate_streaming(N = 10000, filename = "trace_streaming.txt"):

    addr = 0

    with open(filename, "w") as f:

        for i in range(N):

            f.write(f"LOAD {hex(addr)}\n")

            addr += 4

            if addr > 4096:
                addr = 0
