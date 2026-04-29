from itertools import product
from simulator import run_simulation

traces = ["basic", "branch", "mixed", "random", "streaming"]

sizes = [64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536, 131072, 262144, 524288, 1048576]
block_sizes = [8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096]
assocs = [1, 2, 4, 8, 16]
predictors = [1, 2]
miss_penalties = [25, 50, 75, 100]
pipeline_depths = [1, 5, 9, 13]

# sizes = [64, 256, 4096]
# block_sizes = [8, 64, 256, 1024]
# assocs = [1, 2, 4, 8, 16]
# predictors = [1, 2]
# miss_penalties = [50, 100]
# pipeline_depths = [1, 5]


def valid_configs(sizes, block_sizes, assocs, predictors, miss_penalties, pipeline_depths):
    for size, block_size, assoc, predictor, miss_penalty, pipeline_depth, in product(
        sizes, block_sizes, assocs, predictors, miss_penalties, pipeline_depths
    ):
        # block must fit in cache
        if block_size >= size:
            continue

        # cache must hold at least one full set
        if (size // block_size) < assoc:
            continue

        yield {
            "cache_size": size,
            "block_size": block_size,
            "assoc": assoc,
            "predictor": predictor,
            "miss_penalty": miss_penalty,
            "pipeline_depth": pipeline_depth,
        }

def sim_configs():
    headers = "size,block_size,assoc,predictor,miss_penalty,pipeline_depth,instructions,cycles,CPI,cache_stalls,cache_hitrate,branch_stalls,branch_hitrate"

    handles = {trace: open(f"data/data_{trace}.csv", 'w') for trace in traces}
    for f in handles.values():
        print(headers, file=f)

    try:
        for config in valid_configs(sizes, block_sizes, assocs, predictors, miss_penalties, pipeline_depths):
            for trace in traces:
                result = run_simulation(f"traces/trace_{trace}.txt", config)
                row = [
                    config["cache_size"], config["block_size"], config["assoc"],
                    config["predictor"], config["miss_penalty"], config["pipeline_depth"],
                    result["instructions"], result["cycles"], result["CPI"],
                    result["cache_stalls"], result["cache_hitrate"],
                    result["branch_stalls"], result["branch_hitrate"],
                ]
                print(','.join(map(str, row)), file=handles[trace])
    finally:
        for f in handles.values():
            f.close()

if __name__ == '__main__':
    sim_configs()
