"""삽입 정렬, 버블 정렬, 놈 정렬의 실행 시간을 비교한다."""

import random
import time

from bubble_stop import bubble_sort
from gnome_sort import gnome_sort
from insertion_sort import insertion_sort


def measure(sort, values):
    """정렬 한 번에 걸린 초를 돌려준다."""
    start = time.perf_counter()
    sort(values)
    return time.perf_counter() - start


def compare_case(name, original, algorithms):
    """하나의 입력 유형에서 세 정렬의 시간을 출력한다."""
    print(f"\n[{name}]")
    print(f"{'n':>7} {'삽입 정렬(s)':>15} "
          f"{'버블 정렬(s)':>15} {'놈 정렬(s)':>15}")
    for size, values in original:
        times = []
        for algorithm_name, sort in algorithms:
            candidate = list(values)
            elapsed = measure(sort, candidate)
            assert candidate == sorted(values), algorithm_name
            times.append(elapsed)
        print(f"{size:>7} {times[0]:>15.6f} "
              f"{times[1]:>15.6f} {times[2]:>15.6f}")


if __name__ == "__main__":
    random.seed(2026)

    algorithms = (
        ("삽입 정렬", insertion_sort),
        ("버블 정렬", bubble_sort),
        ("놈 정렬", gnome_sort),
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
