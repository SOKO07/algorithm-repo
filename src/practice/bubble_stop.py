"""버블 정렬 — 이웃끼리 비교해서 큰 것을 뒤로 보낸다.

실행: 편집기 오른쪽 위 ▶ 버튼, 또는 `python3 bubble_sort.py`
"""


def bubble_sort(a, stats=None):
    """a를 제자리에서 정렬한다. stats를 주면 [비교, 이동] 횟수를 기록한다.

    교환 한 번은 임시 변수 사용을 포함해 이동 3회로 센다.
    """
    n = len(a)
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            if stats is not None:
                stats[0] += 1
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                if stats is not None:
                    stats[1] += 3
                swapped = True
        if not swapped:  # flag: 이번 회전에 교환이 없었으면 break
            break


if __name__ == "__main__":
    a = [2, 1, 3, 4, 5, 6, 7, 8, 9, 10]

    print("before:", *a)
    stats = [0, 0]
    bubble_sort(a, stats)
    print("after :", *a)
    print(f"comparisons = {stats[0]}, moves = {stats[1]}")
