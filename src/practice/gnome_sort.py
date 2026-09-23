"""놈 정렬 — 인접한 원소를 비교하며 잘못된 위치에서 뒤로 돌아간다."""


def gnome_sort(a):
    """a를 제자리에서 오름차순으로 정렬한다."""
    index = 1
    while index < len(a):
        if index == 0 or a[index - 1] <= a[index]:
            index += 1
        else:
            a[index - 1], a[index] = a[index], a[index - 1]
            index -= 1


if __name__ == "__main__":
    a = [6, 8, 5, 9, 10, 1, 7, 2, 4, 3]

    print("before:", *a)
    gnome_sort(a)
    print("after :", *a)
