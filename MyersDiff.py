from math import ceil


def find_mid_snake(a: str, b: str) -> list:
    # 通过delta的奇偶性可以判断是在正方向扩张还是反方向扩张的时候overlap
    is_even = ((len(a) - len(b)) % 2 == 0)
    is_odd = not is_even
    # 分治法
    half_supply = ceil((len(a) + len(b)) / 2)
    # set用于检测扩张时是否overlap
    f_extend_s = set()
    r_extend_s = set()
    # 当前supply
    counter = [0, 0]

    # 正向扩张
    def forward():
        max_x_nth_k = {1: 0}
        for supply in range(half_supply + 1):
            counter[0] = supply

            for nth_k in range(-supply, supply + 1, 2):
                # snake: [..., point: (x, y)]
                snake = []
                is_overlap = False

                if nth_k == -supply or \
                        (nth_k != supply and max_x_nth_k[nth_k - 1] < max_x_nth_k[nth_k + 1]):
                    x = max_x_nth_k[nth_k + 1]
                    # snake起始点, x相同, y少1
                    snake.append((x, x - (nth_k + 1)))
                else:
                    # y相同, x少1
                    snake.append((max_x_nth_k[nth_k - 1], max_x_nth_k[nth_k - 1] - (nth_k - 1)))
                    x = max_x_nth_k[nth_k - 1] + 1
                y = x - nth_k
                # snake中间点
                snake.append((x, y))

                if is_odd and (x, y) in r_extend_s:
                    is_overlap = True
                while x < len(a) - 1 and y < len(b) - 1 and a[x] == b[y]:
                    x += 1
                    y += 1
                    if is_overlap and (x, y) not in r_extend_s:
                        break
                    # snake尾巴点
                    snake.append((x, y))

                    if not is_overlap and is_odd and (x, y) in r_extend_s:
                        is_overlap = True
                if is_overlap:
                    if snake[-1] == (0, 0):
                        x = y = 1
                        while (x, y) in r_extend_s:
                            snake.append((x, y))
                            x += 1
                            y += 1
                    yield snake
                max_x_nth_k[nth_k] = x
                f_extend_s.update(snake)
            # 切换到反方向的generator
            yield False
            f_extend_s.clear()

    # 反向扩张
    def reverse():
        # reverse就相当于反向扩张, 输出时再变换恢复
        reverse_a = a[::-1]
        reverse_b = b[::-1]

        def r_a(i: int) -> int:
            return i + round(((len(reverse_a) - 1) / 2 - i) * 2)

        def r_b(i: int) -> int:
            return i + round(((len(reverse_b) - 1) / 2 - i) * 2)

        def r_ab(point: tuple) -> tuple:
            a, b = point
            return r_a(a), r_b(b)

        max_x_nth_k = {1: 0}
        for supply in range(half_supply + 1):
            counter[1] = supply

            for nth_k in range(-supply, supply + 1, 2):
                snake = []
                is_overlap = False

                if nth_k == -supply or \
                        (nth_k != supply and max_x_nth_k[nth_k - 1] < max_x_nth_k[nth_k + 1]):
                    x = max_x_nth_k[nth_k + 1]
                    snake.append((x, x - (nth_k + 1)))
                else:
                    snake.append((max_x_nth_k[nth_k - 1], max_x_nth_k[nth_k - 1] - (nth_k - 1)))
                    x = max_x_nth_k[nth_k - 1] + 1
                y = x - nth_k
                snake.append((x, y))

                if is_even and r_ab((x, y)) in f_extend_s:
                    is_overlap = True
                while x < len(reverse_a) - 1 and y < len(reverse_b) - 1 and reverse_a[x] == reverse_b[y]:
                    x += 1
                    y += 1
                    if is_overlap and r_ab((x, y)) not in f_extend_s:
                        break
                    snake.append((x, y))

                    if not is_overlap and is_even and r_ab((x, y)) in f_extend_s:
                        is_overlap = True
                if is_overlap:
                    if snake[-1] == (0, 0):
                        x = y = 1
                        while r_ab((x, y)) in f_extend_s:
                            snake.append((x, y))
                            x += 1
                            y += 1
                    yield [r_ab(point) for point in snake]
                max_x_nth_k[nth_k] = x
                r_extend_s.update(r_ab(point) for point in snake)
            yield False
            r_extend_s.clear()

    # 主体调用部分
    forward_g = forward()
    reverse_g = reverse()
    for _ in range(half_supply + 1):

        snake = next(forward_g)
        if snake is not False:
            return snake, sum(counter)
        snake = next(reverse_g)
        if snake is not False:
            return snake, sum(counter)


if __name__ == '__main__':
    from random import randint, choice


    def longest_common_string(string_a: str, string_b: str):
        def get_longest_string_length(a_index: int, b_index: int):
            if a_index == -1 or b_index == -1:
                return 0
            if string_a[a_index] == string_b[b_index]:
                return get_longest_string_length(a_index - 1, b_index - 1) + 1
            else:
                longest_common_string_len_except_a = get_longest_string_length(a_index - 1, b_index)
                longest_common_string_len_except_b = get_longest_string_length(a_index, b_index - 1)
                if longest_common_string_len_except_a >= longest_common_string_len_except_b:
                    return longest_common_string_len_except_a
                else:
                    return longest_common_string_len_except_b

        return get_longest_string_length(len(string_a) - 1, len(string_b) - 1)


    ALL_CHAR = 'QWERTY'


    def main():
        for _ in range(5):
            print('--------')
            rand_a = ''.join(choice(ALL_CHAR) for _ in range(randint(3, 7)))
            rand_b = ''.join(choice(ALL_CHAR) for _ in range(randint(3, 7)))
            print('a:', rand_a)
            print('b:', rand_b)

            length = longest_common_string(rand_a, rand_b)
            print('len:', length)


    def main_2():
        # WERQQTQ
        # TEYWW
        a = 'WER'
        b = 'TEY'
        snake, supply = find_mid_snake(a, b)
        print(snake, supply)


    main_2()
