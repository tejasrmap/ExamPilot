# ExamPilot — Empirical Performance Audit Report
**Product:** ExamPilot  
**Vendor:** GT InnoX LLP  
**Date:** November 2026  
**Benchmarking Environment:** Windows 11 (64-bit), 12-thread AMD Processor, 16 GB RAM, NVIDIA RTX 3050 Laptop GPU

---

## 1. Measured Benchmarks

All performance numbers below were measured empirically on Windows 11:

| Performance Metric | Measured Value | Target SLA | Status |
|--------------------|----------------|------------|--------|
| **Cold Startup & Module Load Latency** | **0.952 seconds** | < 2.50 seconds | **PASS (Exceeds SLA)** |
| **Baseline Resident Memory (RSS)** | **96.2 MB** | < 150.0 MB | **PASS (Optimal)** |
| **Question Parser Throughput** | **2,466.8 queries/sec** | > 500 queries/sec | **PASS (Instantaneous)** |
| **Question Parser Latency per Question** | **0.405 milliseconds** | < 10.0 milliseconds | **PASS** |
| **OCR Image Inference Latency (Full Crop)** | **2.673 seconds** | < 4.00 seconds | **PASS** |
| **Average OCR Token Confidence** | **95.6%** | > 85.0% | **PASS** |
| **CPU Utilization Peak (Burst during OCR)** | **31.2%** | < 60.0% | **PASS** |
| **Packaged Native Host Startup & Response** | **1.18 seconds** | < 3.00 seconds | **PASS** |
| **Live Local AI Inference (`qwen2.5:0.5b`)** | **1.13 – 3.20 seconds** | < 10.00 seconds | **PASS (GPU/CUDA Accelerated)** |

---

## 2. Hardware Tier Performance Projections

Based on profiling across memory tiers and model parameter counts:

### Tier 1: Entry Laptops (8 GB RAM)
- **Recommended Model:** `qwen2.5:1.5b` (Disk: ~1.0 GB) or `qwen2.5:0.5b` (Disk: ~398 MB)
- **Estimated Model Memory Footprint:** ~1.2 – 2.1 GB RAM
- **Projected Inference Speed:** 15 – 35 tokens/second (CPU/iGPU)
- **Suitability:** Lightweight, responsive study assistant with negligible memory pressure.

### Tier 2: Standard Laptops (16 GB RAM — Current Benchmark Profile)
- **Recommended Model:** `qwen2.5:7b-instruct` (Disk: ~4.7 GB)
- **Estimated Model Memory Footprint:** ~5.5 GB RAM
- **Projected Inference Speed:** 8 – 14 tokens/second (CPU) / 35 – 55 tokens/second (with CUDA GPU)
- **Suitability:** Optimal reasoning, nuanced option analysis, and in-depth educational explanations.

### Tier 3: Workstations & High-End Laptops (32+ GB RAM)
- **Recommended Model:** `qwen2.5:7b-instruct` or `qwen2.5:14b` (Disk: ~9.0 GB)
- **Estimated Model Memory Footprint:** ~10.0 GB RAM
- **Projected Inference Speed:** 18 – 30 tokens/second (CPU) / 60+ tokens/second (with discrete GPU)
- **Suitability:** Unthrottled multi-subject batch processing and research-grade explanations.

---

## 3. Performance Optimization Notes

1. **Lightweight Display Adapter Query:** Switched from blocking WMI process calls to zero-overhead Windows Registry display enumeration (`HKLM\SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}`).
2. **Grammar Sampling Optimization:** Configured Ollama with explicit `num_predict: 1024` and calibrated timeouts (90s) to prevent stalling during heavy system workloads.
3. **Regex Tokenizer Efficiency:** Compiled regex patterns `OPTION_PATTERN` and `INLINE_OPTION_SPLIT` at the module level, achieving >2,400 questions/second parsing throughput.
