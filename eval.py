import os
import sys
import json
import time
import asyncio
from typing import List, Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))
from app.services.topology_agent import build_topology
from app.services.validator import validate_topology

async def run_evaluation(num_tests: int = 50):
    val_file = os.path.join(os.path.dirname(__file__), "dataset", "val.jsonl")
    if not os.path.exists(val_file):
        print("Validation dataset not found. Generating it first...")
        from dataset.generate_dataset import generate_datasets
        generate_datasets(100, 50)

    test_cases = []
    with open(val_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                user_msg = next((m["content"] for m in data["messages"] if m["role"] == "user"), "")
                if user_msg:
                    test_cases.append(user_msg)
            if len(test_cases) >= num_tests:
                break

    print("=" * 65)
    print(f" TopoGemma Evaluation Harness - Running {len(test_cases)} Test Prompts")
    print("=" * 65)

    valid_json_count = 0
    zero_error_count = 0
    total_latency_ms = 0
    results_detail = []

    for idx, prompt in enumerate(test_cases, 1):
        t0 = time.time()
        topo, val = await build_topology(prompt)
        elapsed_ms = int((time.time() - t0) * 1000)
        total_latency_ms += elapsed_ms

        is_valid_json = (topo is not None)
        has_zero_errors = (val.is_valid and len(val.errors) == 0)

        if is_valid_json:
            valid_json_count += 1
        if has_zero_errors:
            zero_error_count += 1

        status_str = "PASS" if has_zero_errors else ("WARN" if is_valid_json else "FAIL")
        print(f"[{idx:02d}/{len(test_cases)}] {status_str} | {elapsed_ms:4d}ms | {prompt[:45]}...")

        results_detail.append({
            "test_id": idx,
            "prompt": prompt,
            "latency_ms": elapsed_ms,
            "valid_json": is_valid_json,
            "zero_errors": has_zero_errors,
            "errors": val.errors,
            "warnings": val.warnings
        })

    json_rate = (valid_json_count / len(test_cases)) * 100
    val_rate = (zero_error_count / len(test_cases)) * 100
    avg_latency = total_latency_ms / len(test_cases)

    print("\n" + "=" * 65)
    print(" EVALUATION RESULTS SUMMARY")
    print("=" * 65)
    print(f" Total Tests Run:              {len(test_cases)}")
    print(f" Valid JSON Output Rate:       {json_rate:.1f}% ({valid_json_count}/{len(test_cases)})")
    print(f" Zero-Error Validation Rate:   {val_rate:.1f}% ({zero_error_count}/{len(test_cases)})")
    print(f" Average Latency per Request:  {avg_latency:.1f} ms")
    print("=" * 65)

    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_tests": len(test_cases),
        "valid_json_rate_pct": json_rate,
        "zero_error_rate_pct": val_rate,
        "avg_latency_ms": avg_latency,
        "results": results_detail
    }
    with open("evaluation_report.json", "w", encoding="utf-8") as rf:
        json.dump(report, rf, indent=2)
    print("Detailed evaluation report written to evaluation_report.json")

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    asyncio.run(run_evaluation(n))
