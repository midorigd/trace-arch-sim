# TraceArchSim

**TraceArchSim** is a trace-driven microarchitecture simulator designed for **CPU design space exploration (DSE)**. The project models key architectural components—including caches, branch predictors, and pipeline depth—and evaluates their impact on performance using synthetic instruction traces.

The simulator enables large-scale experimentation across thousands of architectural configurations and can be extended to run distributed experiments on HPC clusters using Apache Spark.

## Project Goals

- Explore how microarchitectural parameters affect CPU performance
- Analyze tradeoffs between cache design, branch prediction, and pipeline depth
- Enable large-scale architecture experiments using distributed computing

## Features

- Trace-driven instruction simulation
- Configurable cache architecture
  - cache size
  - block size
  - associativity
- Branch prediction models
  - 1-bit predictor
  - 2-bit saturating predictor
- Configurable pipeline depth
- Synthetic workload generators
  - streaming memory workloads
  - random access workloads
  - branch-heavy workloads
- Performance metrics including:
  - Instructions Per Cycle (IPC)
  - cache miss rate
  - branch misprediction rate
  - stall cycle breakdown

## Architecture Overview

The simulator processes a trace of executed instructions and evaluates how a given CPU configuration would handle them.

```
Trace Input
   │
   ▼
Instruction Parser
   │
   ▼
Simulation Engine
 ├─ Cache Model
 ├─ Branch Predictor
 └─ Pipeline Timing Model
   │
   ▼
Performance Metrics
```

Each simulation run evaluates one architecture configuration, enabling design space exploration across thousands of configurations.

## Example Simulation

### Example Trace Format

```
LOAD 0x0000
LOAD 0x0010
BRANCH T
ALU
STORE 0x0040
```

Each instruction represents a dynamic execution event used to model hardware behavior.

### Example Configuration

```
cache_size = 4096
block_size = 32
associativity = 4
pipeline_depth = 7
miss_penalty = 50
```

### Example Output

```
Instructions: 20000
Cycles: 320000
IPC: 0.0625
Cache miss rate: 18.2%
Branch misprediction rate: 7.3%
```

## Future Work

- Multi-core simulation
- More advanced branch predictors
- Memory hierarchy modeling (L1/L2)
- Machine learning guided architecture search
- Full Spark-based distributed simulation
