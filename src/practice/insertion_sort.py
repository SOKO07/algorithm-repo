"""삽입 정렬 — 정렬된 앞부분에 원소를 하나씩 삽입한다."""


def insertion_sort(a):
    """a를 제자리에서 오름차순으로 정렬한다."""
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key


if __name__ == "__main__":
    a = [6, 8, 5, 9, 10, 1, 7, 2, 4, 3]

    print("before:", *a)
    insertion_sort(a)
    print("after :", *a)
