"""Fetch scores from an HTTP API, calculate the average, and save a bar chart."""
from __future__ import annotations
import argparse
import json
import math
import textwrap
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
    return validate_students(payload)


def validate_students(payload: Any) -> list[dict[str, Any]]:
    """Validate HTTP data and direct chart inputs using the same contract."""
    students = payload.get("students") if isinstance(payload, dict) else payload
    if not isinstance(students, list):
        raise ValueError("API response must be a list or contain a 'students' list")
    validated = []
    for index, item in enumerate(students):
        if not isinstance(item, dict) or "score" not in item:
            raise ValueError(f"Student record {index} must contain a score")
        try:
            if isinstance(item["score"], bool):
                raise ValueError("Boolean scores are not allowed")
            score = float(item["score"])
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError(f"Student record {index} has a non-numeric score") from exc
        if not math.isfinite(score) or not 0 <= score <= 100:
            raise ValueError(f"Student record {index} score must be between 0 and 100")
        name = item.get("student", f"Student {index+1}")
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"Student record {index} name must be non-empty text")
        validated.append({"student": name.strip(), "score": score})
    if not validated:
        raise ValueError("API returned no student records")
    return validated

def create_chart(students: list[dict[str, Any]], output_path: str | Path) -> float:
    students = validate_students(students)
    average_score = mean(item["score"] for item in students)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    names = [item["student"] for item in students]
    scores = [item["score"] for item in students]
    # Numeric positions keep duplicate student names as separate observations.
    horizontal = len(names) > 10
    fig, ax = plt.subplots(figsize=(10, max(5, len(names) * .35) if horizontal else 5.5))
    try:
        positions = list(range(len(names)))
        colors = ["#167d8d" if s >= average_score else "#7d96ac" for s in scores]
        labels = [textwrap.fill(name, 20) for name in names]
        if horizontal:
            bars = ax.barh(positions, scores, color=colors)
            ax.set_yticks(positions, labels)
            ax.invert_yaxis()
            ax.axvline(average_score, color="#b45b30", linestyle="--", label=f"Mean {average_score:.2f}%")
            ax.set(xlim=(0, 112), xlabel="Score (%)", ylabel="Student")
            ax.xaxis.grid(True, alpha=.15)
        else:
            bars = ax.bar(positions, scores, color=colors, width=.65)
            ax.set_xticks(positions, labels, rotation=25 if len(names) > 5 else 0)
            ax.axhline(average_score, color="#b45b30", linestyle="--", label=f"Mean {average_score:.2f}%")
            ax.set(ylim=(0, 115), xlabel="Student", ylabel="Score (%)")
            ax.yaxis.grid(True, alpha=.15)
        ax.bar_label(bars, fmt="%.1f", padding=3)
        ax.set_axisbelow(True)
        ax.spines[["top", "right"]].set_visible(False)
        ax.set_title(f"Student test scores | {len(students)} observations", loc="left", pad=18, fontweight="bold")
        ax.legend(frameon=False, loc="upper right")
        fig.tight_layout()
        fig.savefig(output, dpi=160)
    finally:
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
