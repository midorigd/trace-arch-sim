from trace_parser import parse_trace
from cache.cache import Cache
from branch_predictor.one_bit import OneBitPredictor
from branch_predictor.two_bit import TwoBitPredictor

PIPELINE_DEPTH = 10
MISS_PENALTY = 50
BRANCH_PENALTY = 10

def run_simulation(trace_file):
    cache = Cache(size=1024, block_size=16, assoc=1)
    predictor = OneBitPredictor()

    cycles = 0
    instructions = 1

    for inst, arg in parse_trace(trace_file):

        cycles += 1
        if cycles >= PIPELINE_DEPTH:
            instructions += 1

        if inst in ("LOAD", "STORE"):
            hit = cache.access(arg)
            if not hit:
                cycles += MISS_PENALTY

        elif inst == "BRANCH":
            actual = (arg == "T")
            if not predictor.step(actual):
                cycles += BRANCH_PENALTY

    cpi = cycles / instructions

    return {
        "instructions": instructions,
        "cycles": cycles,
        "CPI": round(cpi, 3),
        "cache hitrate": None if cache.total == 0 else round(cache.hits / cache.total, 3),
        "branch hitrate": None if predictor.total == 0 else round(predictor.mispredictions / predictor.total, 3)
    }



if __name__ == "__main__":
    results = run_simulation("traces/trace_streaming.txt")

    for k, v in results.items():
        print(k, v)
