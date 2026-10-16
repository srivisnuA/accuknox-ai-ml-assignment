"""Fetch scores from an HTTP API, calculate the average, and save a bar chart."""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
from statistics import mean
from typing import Any
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import requests

def fetch_students(api_url: str, timeout: int = 10) -> list[dict[str, Any]]:
    response = requests.get(api_url, timeout=timeout)
    response.raise_for_status()
    payload = response.json()
    students = payload.get("students") if isinstance(payload, dict) else payload
    if not isinstance(students, list):
        raise ValueError("API response must be a list or contain a 'students' list")
    validated = []
    for index, item in enumerate(students):
        if not isinstance(item, dict) or "score" not in item:
            raise ValueError(f"Student record {index} must contain a score")
        try:
            score = float(item["score"])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Student record {index} has a non-numeric score") from exc
        if not math.isfinite(score) or not 0 <= score <= 100:
            raise ValueError(f"Student record {index} score must be between 0 and 100")
        validated.append({"student": str(item.get("student", f"Student {index+1}")), "score": score})
    if not validated:
        raise ValueError("API returned no student records")
    return validated

def create_chart(students: list[dict[str, Any]], output_path: str | Path) -> float:
    average_score = mean(item["score"] for item in students)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    names = [item["student"] for item in students]
    scores = [item["score"] for item in students]
    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(names, scores)
    ax.axhline(average_score, linestyle="--", label=f"Average: {average_score:.2f}")
    ax.bar_label(bars, fmt="%.0f", padding=3)
    ax.set(title="Student Test Scores", xlabel="Student", ylabel="Score (%)", ylim=(0, 110))
    ax.legend()
    fig.tight_layout()
    fig.savefig(output, dpi=150)
    plt.close(fig)
    return average_score

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-url", default="http://127.0.0.1:8000/students")
    parser.add_argument("--chart", default="outputs/student_scores.png")
    parser.add_argument("--json-output", default="outputs/student_scores_summary.json")
    args = parser.parse_args()
    try:
        students = fetch_students(args.api_url)
        average_score = create_chart(students, args.chart)
        summary = {"student_count": len(students), "average_score": round(average_score, 2),
                   "scores": students, "chart": args.chart}
        json_path = Path(args.json_output)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(f"Students processed: {len(students)}")
        print(f"Average score: {average_score:.2f}")
        print(f"Bar chart saved to: {args.chart}")
        print(f"Summary saved to: {args.json_output}")
        return 0
    except (requests.RequestException, ValueError, OSError) as exc:
        print(f"Error: {exc}")
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
