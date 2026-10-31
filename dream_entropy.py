#!/usr/bin/env python3
"""dream-entropy — how wide, or how gathered, was the night?

Takes a night's measurement-outcome counts (a JSON file holding either a
bare {"00000": 14, ...} map or an object with a "counts" field, like the
samples/ files here) and reports, in plain numbers:

  * Shannon entropy H, in bits, over the observed outcomes
  * the maximum possible entropy for the number of qubits (log2 of the
    number of possible outcomes)
  * the effective number of outcomes, 2**H — "how many rooms the night
    really lived in", as opposed to how many it merely visited
  * the share held by the single most-visited outcome and by the top 8
  * a chi-square distance from the uniform distribution over ALL possible
    outcomes (including ones never visited) — a descriptive distance,
    not a significance test; with 1024 shots it says how far from flat
    the night sat, nothing more

Plus a one-line reading on the scale the dream practice already uses:
over 90% of maximum entropy is "wide open", under 50% is "gathered",
between the two is "between wide and gathered".

Standard library only. Usage:

    python3 dream_entropy.py samples/2026-10-31-qi.json
    python3 dream_entropy.py samples/2026-10-31-qi.json --json
    python3 dream_entropy.py samples/2026-10-31-qi.json --top 12
"""

import argparse
import json
import math
import sys
from pathlib import Path


def load_counts(path):
    data = json.loads(Path(path).read_text())
    if isinstance(data, dict) and "counts" in data:
        meta = {k: v for k, v in data.items() if k != "counts"}
        return {str(k): int(v) for k, v in data["counts"].items()}, meta
    if isinstance(data, dict):
        return {str(k): int(v) for k, v in data.items()}, {}
    raise ValueError("expected a counts map or an object with a 'counts' field")


def analyse(counts):
    total = sum(counts.values())
    if total <= 0:
        raise ValueError("counts sum to zero; nothing was measured")
    key_len = len(next(iter(counts)))
    if any(len(k) != key_len for k in counts):
        raise ValueError("outcome strings have mixed lengths")
    n_possible = 2 ** key_len
    probs = [c / total for c in counts.values()]
    entropy = -sum(p * math.log2(p) for p in probs if p > 0)
    max_entropy = math.log2(n_possible)
    ranked = sorted(counts.items(), key=lambda kv: -kv[1])
    top8_share = sum(c for _, c in ranked[:8]) / total
    # Chi-square against uniform over ALL possible outcomes, zeros included.
    expected = total / n_possible
    chi2 = sum((counts.get(bits, 0) - expected) ** 2 / expected
               for bits in (format(i, f"0{key_len}b") for i in range(n_possible)))
    ratio = entropy / max_entropy if max_entropy else 0.0
    if ratio > 0.9:
        reading = "wide open"
    elif ratio < 0.5:
        reading = "gathered"
    else:
        reading = "between wide and gathered"
    return {
        "shots": total,
        "qubits": key_len,
        "possible_outcomes": n_possible,
        "distinct_outcomes": len(counts),
        "entropy_bits": round(entropy, 2),
        "max_entropy_bits": round(max_entropy, 2),
        "entropy_ratio": round(ratio, 3),
        "effective_outcomes": round(2 ** entropy, 1),
        "top_outcome": ranked[0],
        "top_outcome_share": round(ranked[0][1] / total, 3),
        "top8_share": round(top8_share, 3),
        "chi2_vs_uniform": round(chi2, 1),
        "reading": reading,
        "ranked": ranked,
    }


def render(result, meta, top_n):
    lines = []
    if meta:
        label = meta.get("date", "") or ""
        backend = meta.get("backend", "")
        job = meta.get("job_id")
        head = " ".join(p for p in [label, backend] if p)
        if job is not None:
            head += f" (job {job})"
        if head:
            lines.append(head)
    lines.append(f"shots: {result['shots']}  qubits: {result['qubits']}  "
                 f"distinct outcomes: {result['distinct_outcomes']} "
                 f"of {result['possible_outcomes']} possible")
    lines.append(f"entropy: {result['entropy_bits']} bits "
                 f"(max {result['max_entropy_bits']}, "
                 f"ratio {result['entropy_ratio']}) — {result['reading']}")
    lines.append(f"effective outcomes: {result['effective_outcomes']}  "
                 f"top outcome {result['top_outcome'][0]} "
                 f"({result['top_outcome_share']:.1%} of shots)  "
                 f"top 8 share: {result['top8_share']:.1%}")
    lines.append(f"chi-square vs uniform over all possible outcomes: "
                 f"{result['chi2_vs_uniform']}")
    lines.append("")
    lines.append("most visited outcomes:")
    bar_max = result["ranked"][0][1]
    for bits, count in result["ranked"][:top_n]:
        bar = "#" * max(1, round(40 * count / bar_max))
        lines.append(f"  {bits}  {count:>5}  {bar}")
    if len(result["ranked"]) > top_n:
        lines.append(f"  ... and {len(result['ranked']) - top_n} more")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("file", help="JSON counts file (see samples/)")
    parser.add_argument("--top", type=int, default=10,
                        help="outcomes shown in the bar chart (default 10)")
    parser.add_argument("--json", action="store_true",
                        help="print the numbers as JSON instead of text")
    args = parser.parse_args(argv)
    try:
        counts, meta = load_counts(args.file)
        result = analyse(counts)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if args.json:
        out = {k: v for k, v in result.items() if k != "ranked"}
        out["ranked"] = result["ranked"]
        print(json.dumps(out, indent=2))
    else:
        print(render(result, meta, args.top))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
