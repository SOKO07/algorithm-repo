"""삽입 정렬 — 정렬된 앞부분에 원소를 하나씩 삽입한다."""


def insertion_sort(a, stats=None):
    """a를 제자리에서 정렬한다. stats를 주면 [비교, 이동] 횟수를 기록한다."""
    for i in range(1, len(a)):
        key = a[i]
        if stats is not None:
            stats[1] += 1
        j = i - 1
        while j >= 0:
            if stats is not None:
                stats[0] += 1
            if a[j] <= key:
                break
            a[j + 1] = a[j]
            if stats is not None:
                stats[1] += 1
            j -= 1
        a[j + 1] = key
        if stats is not None:
            stats[1] += 1


if __name__ == "__main__":
    a = [6, 8, 5, 9, 10, 1, 7, 2, 4, 3]

    print("before:", *a)
    insertion_sort(a)
    print("after :", *a)
