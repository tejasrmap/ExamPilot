"""
ExamPilot Empirical Performance Benchmark
GT InnoX LLP
Measures startup time, OCR inference latency, parser throughput, and memory consumption.
"""

import time
import os
import sys
from pathlib import Path
import psutil
from PIL import Image, ImageDraw

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

def run_performance_audit():
    proc = psutil.Process(os.getpid())
    results = {}

    # 1. Startup & Module Import Latency
    t0 = time.time()
    from desktop.config import APP_NAME
    from desktop.database.database import db_manager
    from desktop.core.question_parser import question_parser
    from desktop.core.ocr_engine import ocr_engine
    startup_sec = round(time.time() - t0, 3)
    results["module_import_time_sec"] = startup_sec

    # 2. Memory Consumption
    mem_info = proc.memory_info()
    ram_mb = round(mem_info.rss / (1024 * 1024), 1)
    results["rss_memory_mb"] = ram_mb

    # 3. Question Parser Throughput (1000 iterations)
    sample_text = """
    Which algorithm is used to find minimum spanning trees?
    A) Prim's Algorithm
    B) Bellman-Ford
    C) Floyd-Warshall
    D) Binary Search
    """
    t_parse_start = time.time()
    for _ in range(1000):
        question_parser.parse_from_text(sample_text)
    total_parse_sec = time.time() - t_parse_start
    parse_per_sec = round(1000 / total_parse_sec, 1)
    results["parser_throughput_qps"] = parse_per_sec
    results["parser_single_latency_ms"] = round((total_parse_sec / 1000) * 1000, 3)

    # 4. OCR Inference Latency on synthetic image
    img = Image.new("RGB", (640, 240), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((20, 20), "What is the capital of Japan?", fill=(0, 0, 0))
    draw.text((30, 60), "A) Kyoto", fill=(10, 10, 10))
    draw.text((30, 95), "B) Tokyo", fill=(10, 10, 10))
    draw.text((30, 130), "C) Osaka", fill=(10, 10, 10))
    draw.text((30, 165), "D) Nagoya", fill=(10, 10, 10))

    t_ocr_start = time.time()
    ocr_res = ocr_engine.extract_text(img)
    ocr_duration_sec = round(time.time() - t_ocr_start, 3)
    results["ocr_inference_latency_sec"] = ocr_duration_sec
    results["ocr_confidence"] = ocr_res.get("avg_confidence", 0.0)

    # 5. CPU Utilization
    cpu_percent = psutil.cpu_percent(interval=0.2)
    results["cpu_utilization_pct"] = cpu_percent

    return results

if __name__ == "__main__":
    res = run_performance_audit()
    print("=" * 60)
    print("EXAMPILOT PERFORMANCE AUDIT RESULTS")
    print("=" * 60)
    for k, v in res.items():
        print(f" - {k:30s}: {v}")
