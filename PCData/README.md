# PC Data

This is a project for maximizing the rationality of laptop purchase decisions based on benchmark data. It is currently Canada-only, developed for the boxing day of 2023.

## Data Sources

* [CanadaComputers](https://www.canadacomputers.com/) for product information
* [PassMark](https://www.passmark.com/) for cpu benchmark
* [NotebookCheck](https://www.notebookcheck.net/) for gpu benchmark

## View Results

There are five results generated for various users groups. They weigh cpu and gpu scores differently in their calculation of the composite benchmark. If you need it for gaming, video editing, or streaming, open the GPU-heavy benchmark. If you are an average student or officer, open the average benchmark. If you are a programmer, open the CPU-heavy benchmark.

⬇️ GPU-Heavy Side ⬇️

* [90% GPU Benchmark](https://hw.hydev.org/PCData/data/computed/canada_computers_laptops_bench_0.1.html)
* [70% GPU Benchmark](https://hw.hydev.org/PCData/data/computed/canada_computers_laptops_bench_0.3.html)
* [50% Average Benchmark](https://hw.hydev.org/PCData/data/computed/canada_computers_laptops_bench_0.5.html)
* [70% CPU Benchmark](https://hw.hydev.org/PCData/data/computed/canada_computers_laptops_bench_0.7.html)
* [90% CPU Benchmark](https://hw.hydev.org/PCData/data/computed/canada_computers_laptops_bench_0.9.html)

⬆️ CPU-Heavy Side ⬆️

## Data Format

```
./*.py: Scripts used to crawl / process data
./data/: Data files
- canada_computers_laptops.csv: Product information from CanadaComputers
- passmark/: Benchmark data from PassMark
  - cpu.csv: CPU benchmark
  - gpu.csv: GPU benchmark (not used)
- notebookcheck/: Benchmark data from NotebookCheck
  - mobile-cpu.csv: Mobile CPU data used to obtain integrated GPU  
  - mobile-gpu.csv: Mobile GPU benchmark
- computed/: Outputs of our analysis
```
