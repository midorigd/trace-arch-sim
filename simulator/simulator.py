from trace_parser import parse_trace
from cache.cache import Cache
from branch_predictor.one_bit import OneBitPredictor
from branch_predictor.two_bit import TwoBitPredictor

def run_simulation(trace_file, config):
    cache = Cache(
        config["cache_size"],
        config["block_size"],
        config["assoc"]
    )

    predictor = OneBitPredictor() if config["predictor"] == 1 else TwoBitPredictor()

    cycles = 0
    instructions = 1 if config["pipeline_depth"] > 1 else 0

    for inst, arg in parse_trace(trace_file):

        cycles += 1
        if cycles >= config["pipeline_depth"]:
            instructions += 1

        if inst in ("LOAD", "STORE"):
            hit = cache.access(arg)
            if not hit:
                cycles += config["miss_penalty"]

        elif inst == "BRANCH":
            actual = (arg == "T")
            if not predictor.step(actual):
                cycles += config["pipeline_depth"]

    cpi = cycles / instructions

    return {
        "instructions": instructions,
        "cycles": cycles,
        "CPI": round(cpi, 3),
        "cache_stalls": (cache.total - cache.hits) * config["miss_penalty"],
        "cache_hitrate": None if cache.total == 0 else round(cache.hits / cache.total, 3),
        "branch_stalls": predictor.mispredictions * config["pipeline_depth"],
        "branch_hitrate": None if predictor.total == 0 else round((predictor.total - predictor.mispredictions) / predictor.total, 3)
    }


if __name__ == "__main__":
    config = {
        "cache_size": 1024,
        "block_size": 16,
        "assoc": 1,
        "predictor": 1,
        "miss_penalty": 50,
        "pipeline_depth": 5
    }

    results = run_simulation("traces/trace_streaming.txt", config)

    for k, v in results.items():
        print(k, v)
