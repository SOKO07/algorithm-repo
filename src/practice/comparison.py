"""삽입 정렬, 버블 정렬, 노움 정렬의 실행 시간을 비교한다."""

import random
import statistics
import tracemalloc
import time

from bubble_stop import bubble_sort
from gnome_sort import gnome_sort
from insertion_sort import insertion_sort


def measure(sort, values):
    """계측 없이 다섯 번 정렬하고 실행시간 중앙값을 밀리초로 돌려준다."""
    elapsed_samples = []
    for _ in range(5):
        candidate = list(values)
        start = time.perf_counter()
        sort(candidate)
        elapsed_samples.append(time.perf_counter() - start)
        assert candidate == sorted(values)
    return statistics.median(elapsed_samples) * 1000


def count_operations(sort, original):
    """별도 실행에서 비교와 이동 횟수를 센다."""
    values = list(original)
    stats = [0, 0]
    sort(values, stats)
    assert values == sorted(original)
    return stats


def measure_peak_memory(sort, original):
    """입력 리스트를 제외하고 정렬 중 추가된 Python 메모리의 peak를 잰다."""
    values = list(original)
    tracemalloc.start()
    baseline, _ = tracemalloc.get_traced_memory()
    try:
        sort(values)
        _, peak = tracemalloc.get_traced_memory()
        return max(0, peak - baseline)
    finally:
        tracemalloc.stop()


def compare_case(name, original, algorithms):
    """하나의 입력 유형에서 시간, 연산 횟수, 추가 메모리를 출력한다."""
    print(f"\n[{name}]")
    print(f"{'n':>7} {'알고리즘':>12} {'시간(ms)':>10} {'비교':>12} "
          f"{'이동':>12} {'추가 메모리(B)':>16}")
    for size, values in original:
        for algorithm_name, sort in algorithms:
            elapsed = measure(sort, values)
            comparisons, moves = count_operations(sort, values)
            peak_memory = measure_peak_memory(sort, values)
            print(f"{size:>7} {algorithm_name:>12} {elapsed:>10.6f} "
                  f"{comparisons:>12} {moves:>12} {peak_memory:>16}")


class StabilityItem:
    """항목은 key로만 비교하고, label은 동등 키의 원래 순서를 식별한다."""

    def __init__(self, key, label):
        self.key = key
        self.label = label

    def __gt__(self, other):
        return self.key > other.key

    def __le__(self, other):
        return self.key <= other.key


def check_stability(sort):
    """같은 key를 가진 항목들이 입력 순서를 유지하는지 확인한다."""
    values = [
        StabilityItem(2, "a"),
        StabilityItem(1, "b"),
        StabilityItem(2, "c"),
        StabilityItem(1, "d"),
        StabilityItem(2, "e"),
    ]
    sort(values)
    return [(item.key, item.label) for item in values] == [
        (1, "b"), (1, "d"), (2, "a"), (2, "c"), (2, "e")
    ]


if __name__ == "__main__":
    random.seed(2026)

    algorithms = (
        ("삽입 정렬", insertion_sort),
        ("버블 정렬", bubble_sort),
        ("노움 정렬", gnome_sort),
    )

    sizes = (20, 40, 1000, 3000)
    random_inputs = [
        (size, [random.randrange(size * 10) for _ in range(size)])
        for size in sizes
    ]
    sorted_inputs = [(size, sorted(values)) for size, values in random_inputs]
    reversed_inputs = [(size, list(reversed(values)))
                       for size, values in sorted_inputs]

    compare_case("정렬된 배열", sorted_inputs, algorithms)
    compare_case("역순 배열", reversed_inputs, algorithms)
    compare_case("무작위 배열", random_inputs, algorithms)

    print("\n[안정성]")
    for name, sort in algorithms:
        print(f"{name}: {'안정' if check_stability(sort) else '불안정'}")
