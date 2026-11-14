"""Summarize a results CSV into tables (standard library only).

Usage (from personal_project/):

    python src/summarize.py results/main.csv [--timing results/timing.csv] [--md out.md]

Tables:
  1. per algorithm and map kind: runs, arrival / collision / timeout rate with
     95% Wilson interval
  2. path quality on maps where ALL three algorithms arrived (same maps, so the
     comparison is fair): mean distance, mean distance / A* reference, mean
     steps, mean compute time per run
  3. paired comparison of arrival between algorithms (exact McNemar test)
  4. median compute time on the timing subset, if --timing is given
  5. computation cost on ALL runs: mean steps, mean compute time per run and
     per step (total time / total steps), so a slow algorithm can be told
     apart from one that merely wandered for many steps

Rows with outcome "rejected" are counted but not analysed.
"""
import argparse
import csv
import math
import statistics
import sys
from collections import defaultdict

ALGOS = ("APF", "Bug2", "DWA")
OUTCOMES = ("arrived", "collision", "timeout")


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def mcnemar_exact(b, c):
    """Two-sided exact p for discordant counts b, c (binomial, p = 0.5)."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def load(path):
    rows, rejected = [], 0
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["outcome"] == "rejected":
                rejected += 1
            else:
                rows.append(r)
    return rows, rejected


def pct(k, n):
    lo, hi = wilson(k, n)
    return f"{100 * k / n:5.1f}% [{100 * lo:4.1f}, {100 * hi:4.1f}]" if n else "-"


def table_rates(rows, kinds):
    out = ["### 1. 결과 비율 (95% Wilson 구간)", "",
           "| 지도 유형 | 알고리즘 | 실행 수 | 도착률 | 충돌률 | 타임아웃률 |",
           "|---|---|---:|---|---|---|"]
    for kind in list(kinds) + ["전체"]:
        for a in ALGOS:
            sel = [r for r in rows if r["algo"] == a
                   and (kind == "전체" or r["kind"] == kind)]
            n = len(sel)
            cnt = {o: sum(r["outcome"] == o for r in sel) for o in OUTCOMES}
            out.append(f"| {kind} | {a} | {n} | {pct(cnt['arrived'], n)} | "
                       f"{pct(cnt['collision'], n)} | {pct(cnt['timeout'], n)} |")
    return out


def by_map(rows):
    d = defaultdict(dict)
    for r in rows:
        d[(r["kind"], int(r["seed"]))][r["algo"]] = r
    return d


def table_quality(rows, kinds):
    maps = by_map(rows)
    out = ["", "### 2. 세 알고리즘이 모두 도착한 지도에서의 경로 품질", "",
           "| 지도 유형 | 알고리즘 | 지도 수 | 평균 이동 거리 | 거리 ÷ A* 기준 | 평균 스텝 | 평균 계산 시간(s/실행) | 계산 시간/스텝(ms) |",
           "|---|---|---:|---:|---:|---:|---:|---:|"]
    for kind in list(kinds) + ["전체"]:
        common = [m for (k, _), m in maps.items()
                  if (kind == "전체" or k == kind)
                  and all(a in m and m[a]["outcome"] == "arrived" for a in ALGOS)]
        for a in ALGOS:
            if not common:
                out.append(f"| {kind} | {a} | 0 | - | - | - | - | - |")
                continue
            dist = [float(m[a]["distance"]) for m in common]
            ratio = [float(m[a]["distance"]) / float(m[a]["astar_len"])
                     for m in common if m[a]["astar_len"]]
            steps = [int(m[a]["steps"]) for m in common]
            ct = [float(m[a]["compute_time"]) for m in common]
            sd = statistics.stdev(dist) if len(dist) > 1 else 0.0
            out.append(f"| {kind} | {a} | {len(common)} | "
                       f"{statistics.mean(dist):.1f} ± {sd:.1f} | "
                       f"{statistics.mean(ratio):.3f} | {statistics.mean(steps):.0f} | "
                       f"{statistics.mean(ct):.3f} | "
                       f"{1000 * sum(ct) / sum(steps):.3f} |")
    return out


def table_cost(rows, kinds):
    out = ["", "### 5. 계산 비용 (타임아웃·충돌 포함 모든 실행)", "",
           "| 지도 유형 | 알고리즘 | 실행 수 | 평균 스텝 | 평균 계산 시간(s/실행) | 계산 시간/스텝(ms) |",
           "|---|---|---:|---:|---:|---:|"]
    for kind in list(kinds) + ["전체"]:
        for a in ALGOS:
            sel = [r for r in rows if r["algo"] == a
                   and (kind == "전체" or r["kind"] == kind)]
            if not sel:
                out.append(f"| {kind} | {a} | 0 | - | - | - |")
                continue
            steps = [int(r["steps"]) for r in sel]
            ct = [float(r["compute_time"]) for r in sel]
            out.append(f"| {kind} | {a} | {len(sel)} | {statistics.mean(steps):.0f} | "
                       f"{statistics.mean(ct):.3f} | {1000 * sum(ct) / sum(steps):.3f} |")
    return out


def table_paired(rows):
    maps = by_map(rows)
    out = ["", "### 3. 도착 여부의 짝 비교 (정확 McNemar 검정)", "",
           "| 비교 | A만 도착 | B만 도착 | p 값 |", "|---|---:|---:|---:|"]
    for i, a in enumerate(ALGOS):
        for b in ALGOS[i + 1:]:
            only_a = only_b = 0
            for m in maps.values():
                if a in m and b in m:
                    ra, rb = m[a]["outcome"] == "arrived", m[b]["outcome"] == "arrived"
                    only_a += ra and not rb
                    only_b += rb and not ra
            out.append(f"| {a} vs {b} | {only_a} | {only_b} | "
                       f"{mcnemar_exact(only_a, only_b):.4f} |")
    return out


def table_timing(path):
    sums = defaultdict(list)
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            sums[r["algo"]].append(float(r["median_compute_time"]))
    out = ["", "### 4. 계산 시간 (타이밍 부분집합, 5회 중앙값의 평균)", "",
           "| 알고리즘 | 지도 수 | 평균 계산 시간(s/실행) |", "|---|---:|---:|"]
    for a in ALGOS:
        v = sums.get(a, [])
        out.append(f"| {a} | {len(v)} | "
                   f"{statistics.mean(v):.3f} |" if v else f"| {a} | 0 | - |")
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")  # Korean headings on any console
    p = argparse.ArgumentParser()
    p.add_argument("csv")
    p.add_argument("--timing")
    p.add_argument("--md")
    args = p.parse_args()
    rows, rejected = load(args.csv)
    kinds = sorted({r["kind"] for r in rows})
    lines = [f"# 결과 요약: {args.csv}", "",
             f"분석한 행 {len(rows)}개, 풀 수 없어 제외된 지도 {rejected}개", ""]
    lines += table_rates(rows, kinds)
    lines += table_quality(rows, kinds)
    lines += table_paired(rows)
    if args.timing:
        lines += table_timing(args.timing)
    lines += table_cost(rows, kinds)
    text = "\n".join(lines)
    print(text)
    if args.md:
        with open(args.md, "w", encoding="utf-8") as f:
            f.write(text + "\n")


if __name__ == "__main__":
    main()
