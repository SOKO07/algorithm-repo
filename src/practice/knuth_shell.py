"""셸 정렬 — 멀리 떨어진 원소끼리 먼저 삽입 정렬해 두고, 간격을 줄여 간다.

실행: 편집기 오른쪽 위 ▶ 버튼, 또는 `python3 shell_sort.py`
"""

def knuth_gap(n):
    """Knuth 수열 1, 4, 13, 40, ... 을 n보다 작은 것까지 돌려준다."""
    gap = 1
    while gap < n:
        gap = gap * 3 + 1
    return gap

def shell_sort(a):
    """a를 제자리에서 오름차순으로 정렬하고 (비교 횟수, 이동 횟수)를 돌려준다.

    knuth_gap으로 n보다 작은 최대 Knuth 수를 처음에 쓰고, 각 단계마다 (gap - 1) // 3으로
    간격을 줄여 간다.
    """
    comparisons = 0
    moves = 0
    n = len(a)

    gap = knuth_gap(n)

    while gap >= 1:
        for i in range(gap, n):
            key = a[i]
            moves += 1
            j = i - gap
            while j >= 0:
                comparisons += 1
                if a[j] <= key:
                    break
                a[j + gap] = a[j]
                moves += 1
                j -= gap
            a[j + gap] = key
            moves += 1
        gap = (gap - 1) // 3
    return comparisons, moves

if __name__ == "__main__":
    a = [6, 8, 5, 9, 10, 1, 7, 2, 4, 3]

    print("before:", *a)
    comparisons, moves = shell_sort(a)
    print("after :", *a)
    print(f"comparisons = {comparisons}, moves = {moves}")
