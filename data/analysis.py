from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, col, lit
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

# ── config ────────────────────────────────────────────────────────────────────

HDFS_BASE   = "hdfs:///user/your-username/sim_data"
OUTPUT_DIR  = "/tmp/plots"
TRACES      = ["basic", "branch", "mixed", "random", "streaming"]
PREDICTORS  = {1: "1-bit", 2: "2-bit"}

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── spark session ─────────────────────────────────────────────────────────────

spark = SparkSession.builder.appName("cpu_sim_analysis").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

# ── load data ─────────────────────────────────────────────────────────────────

dfs = {
    t: spark.read.csv(f"{HDFS_BASE}/data_{t}.csv", header=True, inferSchema=True)
    for t in TRACES
}

combined = None
for t, df in dfs.items():
    labeled = df.withColumn("trace", lit(t))
    combined = labeled if combined is None else combined.union(labeled)

combined.cache()

# ── helpers ───────────────────────────────────────────────────────────────────

def save(name):
    path = f"{OUTPUT_DIR}/{name}.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"saved: {path}")

TRACE_COLORS = {
    "basic":       "#4C72B0",
    "branch": "#55A868",
    "mixed":     "#C44E52",
    "random":     "#8172B2",
    "streaming":     "#CCB974",
}

# ── 1. cache size vs hit rate by associativity (one subplot per trace) ────────

cache_size_assoc = (
    combined
    .groupBy("trace", "cache_size", "assoc")
    .agg(avg("cache_hitrate").alias("avg_hitrate"))
    .orderBy("trace", "assoc", "cache_size")
    .toPandas()
)

fig, axes = plt.subplots(2, 3, figsize=(16, 9), sharey=True)
axes = axes.flatten()

for i, trace in enumerate(TRACES):
    ax = axes[i]
    sub = cache_size_assoc[cache_size_assoc["trace"] == trace]
    for assoc in sorted(sub["assoc"].unique()):
        d = sub[sub["assoc"] == assoc].sort_values("cache_size")
        ax.plot(d["cache_size"], d["avg_hitrate"], marker="o", markersize=3,
                label=f"assoc={assoc}")
    ax.set_xscale("log", base=2)
    ax.set_title(trace)
    ax.set_xlabel("cache size (bytes)")
    ax.set_ylabel("avg hit rate")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

axes[-1].set_visible(False)
fig.suptitle("Cache Size vs Hit Rate by Associativity", fontsize=14)
plt.tight_layout()
save("1_cache_size_vs_hitrate_by_assoc")

# ── 2. block size vs hit rate by trace ────────────────────────────────────────

block_hitrate = (
    combined
    .groupBy("trace", "block_size")
    .agg(avg("cache_hitrate").alias("avg_hitrate"))
    .orderBy("trace", "block_size")
    .toPandas()
)

fig, ax = plt.subplots(figsize=(10, 5))
for trace in TRACES:
    sub = block_hitrate[block_hitrate["trace"] == trace].sort_values("block_size")
    ax.plot(sub["block_size"], sub["avg_hitrate"], marker="o",
            label=trace, color=TRACE_COLORS[trace])

ax.set_xscale("log", base=2)
ax.set_title("Block Size vs Cache Hit Rate")
ax.set_xlabel("block size (bytes)")
ax.set_ylabel("avg hit rate")
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
save("2_block_size_vs_hitrate")

# ── 3. predictor type vs branch hit rate by trace (grouped bar) ───────────────

branch_pred = (
    combined
    .groupBy("trace", "predictor")
    .agg(avg("branch_hitrate").alias("avg_branch_hitrate"))
    .orderBy("trace", "predictor")
    .toPandas()
)

import numpy as np
x = np.arange(len(TRACES))
width = 0.35

fig, ax = plt.subplots(figsize=(10, 5))
for i, (pred_id, pred_label) in enumerate(PREDICTORS.items()):
    vals = [
        branch_pred[(branch_pred["trace"] == t) & (branch_pred["predictor"] == pred_id)]["avg_branch_hitrate"].values
        for t in TRACES
    ]
    vals = [v[0] if len(v) else 0 for v in vals]
    ax.bar(x + (i - 0.5) * width, vals, width, label=pred_label)

ax.set_xticks(x)
ax.set_xticklabels(TRACES)
ax.set_ylim(0, 1)
ax.set_title("Predictor Type vs Branch Hit Rate by Trace")
ax.set_ylabel("avg branch hit rate")
ax.legend()
ax.grid(True, alpha=0.3, axis="y")
plt.tight_layout()
save("3_predictor_vs_branch_hitrate")

# ── 4. CPI decomposition by trace (stacked bar) ───────────────────────────────

cpi_decomp = (
    combined
    .withColumn("cache_cpi", col("cache_stalls") / col("instructions"))
    .withColumn("branch_cpi", col("branch_stalls") / col("instructions"))
    .withColumn("base_cpi",
                col("cpi") - col("cache_stalls") / col("instructions")
                            - col("branch_stalls") / col("instructions"))
    .groupBy("trace")
    .agg(
        avg("base_cpi").alias("base_cpi"),
        avg("cache_cpi").alias("cache_cpi"),
        avg("branch_cpi").alias("branch_cpi"),
    )
    .toPandas()
)

cpi_decomp = cpi_decomp.set_index("trace").reindex(TRACES).reset_index()

fig, ax = plt.subplots(figsize=(10, 5))
ax.bar(cpi_decomp["trace"], cpi_decomp["base_cpi"],  label="base")
ax.bar(cpi_decomp["trace"], cpi_decomp["cache_cpi"],  bottom=cpi_decomp["base_cpi"], label="cache stalls")
ax.bar(cpi_decomp["trace"], cpi_decomp["branch_cpi"],
       bottom=cpi_decomp["base_cpi"] + cpi_decomp["cache_cpi"], label="branch stalls")

ax.set_title("CPI Decomposition by Trace")
ax.set_ylabel("avg CPI")
ax.legend()
ax.grid(True, alpha=0.3, axis="y")
plt.tight_layout()
save("4_cpi_decomposition")

# ── 5. pipeline depth vs CPI by predictor (loop trace only) ──────────────────

pipeline_pred = (
    dfs["branch"]
    .groupBy("pipeline_depth", "predictor")
    .agg(avg("cpi").alias("avg_cpi"))
    .orderBy("pipeline_depth", "predictor")
    .toPandas()
)

fig, ax = plt.subplots(figsize=(8, 5))
for pred_id, pred_label in PREDICTORS.items():
    sub = pipeline_pred[pipeline_pred["predictor"] == pred_id].sort_values("pipeline_depth")
    ax.plot(sub["pipeline_depth"], sub["avg_cpi"], marker="o", label=pred_label)

ax.set_title("Pipeline Depth vs CPI by Predictor (loop trace)")
ax.set_xlabel("pipeline depth")
ax.set_ylabel("avg CPI")
ax.set_xticks(sorted(pipeline_pred["pipeline_depth"].unique()))
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
save("5_pipeline_depth_vs_cpi_by_predictor")

# ── 6. miss penalty vs CPI by cache size bucket ───────────────────────────────

from pyspark.sql.functions import when

bucketed = combined.withColumn(
    "size_bucket",
    when(col("cache_size") <= 512,   "small  (≤512)")
    .when(col("cache_size") <= 8192, "medium (≤8K)")
    .otherwise(                       "large  (>8K)")
)

miss_cpi = (
    bucketed
    .groupBy("trace", "miss_penalty", "size_bucket")
    .agg(avg("cpi").alias("avg_cpi"))
    .orderBy("trace", "size_bucket", "miss_penalty")
    .toPandas()
)

buckets = ["small  (≤512)", "medium (≤8K)", "large  (>8K)"]
fig, axes = plt.subplots(1, len(TRACES), figsize=(18, 4), sharey=True)

for ax, trace in zip(axes, TRACES):
    sub = miss_cpi[miss_cpi["trace"] == trace]
    for bucket in buckets:
        d = sub[sub["size_bucket"] == bucket].sort_values("miss_penalty")
        ax.plot(d["miss_penalty"], d["avg_cpi"], marker="o", label=bucket)
    ax.set_title(trace)
    ax.set_xlabel("miss penalty (cycles)")
    ax.set_ylabel("avg CPI")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

fig.suptitle("Miss Penalty vs CPI by Cache Size Bucket", fontsize=14)
plt.tight_layout()
save("6_miss_penalty_vs_cpi_by_cache_size")

# ── 7. assoc vs hit rate at fixed small cache (where assoc matters most) ──────

small_assoc = (
    combined
    .filter(col("cache_size") <= 1024)
    .groupBy("trace", "assoc")
    .agg(avg("cache_hitrate").alias("avg_hitrate"))
    .orderBy("trace", "assoc")
    .toPandas()
)

fig, ax = plt.subplots(figsize=(9, 5))
for trace in TRACES:
    sub = small_assoc[small_assoc["trace"] == trace].sort_values("assoc")
    ax.plot(sub["assoc"], sub["avg_hitrate"], marker="o",
            label=trace, color=TRACE_COLORS[trace])

ax.set_xscale("log", base=2)
ax.set_xticks([1, 2, 4, 8, 16])
ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
ax.set_title("Associativity vs Hit Rate (cache size ≤ 1024 bytes)")
ax.set_xlabel("associativity")
ax.set_ylabel("avg hit rate")
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
save("7_assoc_vs_hitrate_small_cache")

# ── done ──────────────────────────────────────────────────────────────────────

spark.stop()
print("all plots saved to", OUTPUT_DIR)
