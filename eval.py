import os
import sys
import json
import time
import asyncio
from typing import List, Dict, Any

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from backend.services.topology_agent import generate_topology
from backend.services.validator import validate_topology
from backend.database import repo

VAL_PATH = os.path.join(os.path.dirname(__file__), "dataset", "val.jsonl")
RESULTS_PATH = os.path.join(os.path.dirname(__file__), "evaluation_results.json")


async def run_evaluation(max_samples: int = 20):
    repo.init_db()
    print("=" * 65)
    print("TopoGemma / Net-Pilot-AI: Quantitative Model & System Evaluation")
    print("=" * 65)

    if not os.path.exists(VAL_PATH):
        print(f"Error: Validation dataset not found at {VAL_PATH}. Run dataset/generate_dataset.py first.")
        return

    test_prompts: List[str] = []
    with open(VAL_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                item = json.loads(line)
                for msg in item.get("messages", []):
                    if msg.get("role") == "user":
                        test_prompts.append(msg.get("content"))
                        break

    samples = test_prompts[:max_samples]
    print(f"Loaded {len(samples)} evaluation test prompts.\n")

    valid_json_count = 0
    zero_error_count = 0
    latencies: List[float] = []

    print(f"{'Idx':<4} | {'Latency':<8} | {'JSON Valid':<10} | {'Validator Pass':<14} | Prompt Preview")
    print("-" * 65)

    for idx, prompt in enumerate(samples, 1):
        t0 = time.time()
        topo, val_res = await generate_topology(prompt, max_retries=2)
        elapsed_ms = (time.time() - t0) * 1000
        latencies.append(elapsed_ms)

        is_valid_json = topo is not None
        is_zero_error = is_valid_json and len(val_res.errors) == 0

        if is_valid_json:
            valid_json_count += 1
        if is_zero_error:
            zero_error_count += 1

        json_badge = "[PASS]" if is_valid_json else "[FAIL]"
        val_badge = "[PASS]" if is_zero_error else "[FAIL]"
        preview = (prompt[:30] + "...") if len(prompt) > 30 else prompt

        print(f"{idx:<4} | {elapsed_ms:>6.1f}ms | {json_badge:^10} | {val_badge:^14} | {preview}")

    total = len(samples)
    json_rate = (valid_json_count / total) * 100 if total else 0.0
    val_rate = (zero_error_count / total) * 100 if total else 0.0
    avg_latency = sum(latencies) / len(latencies) if latencies else 0.0

    print("=" * 65)
    print("EVALUATION SUMMARY RESULTS (JUDGES SLIDE METRICS):")
    print(f"Total Test Prompts Evaluated: {total}")
    print(f"JSON Syntax & Schema Accuracy: {json_rate:.1f}% ({valid_json_count}/{total})")
    print(f"Deterministic Network Validation Pass Rate: {val_rate:.1f}% ({zero_error_count}/{total})")
    print(f"Average System Latency: {avg_latency:.1f} ms")
    print("=" * 65)

    results_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_evaluated": total,
        "json_parse_rate_percent": json_rate,
        "validator_zero_error_rate_percent": val_rate,
        "average_latency_ms": avg_latency
    }
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(results_data, f, indent=2)
    print(f"Saved evaluation metrics to {RESULTS_PATH}\n")


if __name__ == "__main__":
    asyncio.run(run_evaluation(max_samples=10))
