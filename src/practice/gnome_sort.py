"""노움 정렬 — 인접한 원소를 비교하며 잘못된 위치에서 뒤로 돌아간다."""


def gnome_sort(a, stats=None):
    """a를 제자리에서 정렬한다. stats를 주면 [비교, 이동] 횟수를 기록한다.

    인접 원소 교환은 임시 변수 사용을 포함해 이동 3회로 센다.
    """
    index = 1
    while index < len(a):
        if index == 0:
            index += 1
        else:
            if stats is not None:
                stats[0] += 1
            if a[index - 1] <= a[index]:
                index += 1
            else:
                a[index - 1], a[index] = a[index], a[index - 1]
                if stats is not None:
                    stats[1] += 3
                index -= 1


if __name__ == "__main__":
    a = [6, 8, 5, 9, 10, 1, 7, 2, 4, 3]

    print("before:", *a)
    gnome_sort(a)
    print("after :", *a)
