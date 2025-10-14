# chamfer-metal

Chamfer distance computation with a Metal/MPS-accelerated kd-tree (macOS) and CPU fallback.

## Features

- kd-tree search on Apple Silicon GPUs via Metal
- CPU fallback for all platforms
- PyTorch autograd support
- Benchmarks comparing Metal, CPU kd-tree, and brute force
