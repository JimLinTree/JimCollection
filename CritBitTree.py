class CBInternal:
    def __init__(self):
        self.diff_at = None
        self.mask = None
        self.crit_is_0 = None
        self.crit_is_1 = None

    def print(self, lv=0):
        intent = '  '
        print(intent * lv, 'diff_at: {}, mask: {}'.format(self.diff_at, bin(self.mask)))

        lv += 1
        for sub in (self.crit_is_0, self.crit_is_1):
            if isinstance(sub, CBInternal):
                sub.print(lv)
            else:
                print(intent * lv, sub)


class CBTree:
    def __init__(self):
        self.root = None

    def insert(self, new_bytes: bytes):
        if self.root is None:
            self.root = new_bytes
        else:
            grand, pa, old_bytes = self.find_best_match(new_bytes)
            # 查找哪个字节不同
            # 我在这里认为各个字符串一定会以 $ 结尾, 所以不考虑子串判断的问题
            for i in range(min(len(new_bytes), len(old_bytes))):
                if new_bytes[i] != old_bytes[i]:
                    diff_at = i
                    diff_byte = new_bytes[i] ^ old_bytes[i]
                    break
            else:
                return 'ALREADY_IN'

            # 查找哪个 bit 不同
            # 0b0100_1000 => 0b0111_1111
            diff_byte |= diff_byte >> 1
            diff_byte |= diff_byte >> 2
            diff_byte |= diff_byte >> 4

            # 结果: 0b0111_1111 => 0b1011_1111
            # 过程:
            # ~(diff_byte >> 1) = 0b1100_0000
            # diff_byte & 0b1100_0000 = 0b0111_1111 & 0b1100_0000 = 0b0100_0000
            mask = (diff_byte & ~(diff_byte >> 1)) ^ 255

            direct = (1 + (mask | new_bytes[diff_at])) >> 8
            # 生成一个新节点
            node = CBInternal()
            node.diff_at = diff_at
            node.mask = mask
            if direct == 0:
                node.crit_is_0 = new_bytes
            else:
                node.crit_is_1 = new_bytes

            # 插入节点:
            # 因为分歧点是按顺序发现的, 无论这次的分歧点在于路径上的前面还是后面
            # 都可以直接插入而保持性质不变
            # 即, 分歧顺序按照 1st 2nd 3rd 4th... 排列
            # 比如, 当前在 3rd 处分歧. 那么, 剩余所有已存在的串 3rd 必然没有分歧
            parent = None
            insert_point = self.root  # 置入 new_node 的位置
            while True:

                if isinstance(insert_point, bytes):
                    break
                elif isinstance(insert_point, CBInternal):
                    if insert_point.diff_at > diff_at:
                        break
                    elif insert_point.diff_at == diff_at and insert_point.mask > node.mask:
                        # 同一 byte, 分歧 bit 越靠后, 数值越小
                        break

                check_byte = new_bytes[insert_point.diff_at] if len(new_bytes) > insert_point.diff_at else 0
                parent = insert_point
                direct = (1 + (insert_point.mask | check_byte)) >> 8
                if direct == 0:
                    insert_point = insert_point.crit_is_0
                else:
                    insert_point = insert_point.crit_is_1

            if parent is None:
                self.root = node
            else:
                if direct == 0:
                    parent.crit_is_0 = node
                else:
                    parent.crit_is_1 = node

            if node.crit_is_0 is None:
                node.crit_is_0 = insert_point
            else:
                node.crit_is_1 = insert_point

    def find_best_match(self, src: bytes):
        q = [None] * 3

        q[-1] = cursor = self.root
        while isinstance(cursor, CBInternal):
            # 计算方向
            check_byte = src[cursor.diff_at] if len(src) > cursor.diff_at else 0
            direct = (1 + (cursor.mask | check_byte)) >> 8

            if direct == 0:
                cursor = cursor.crit_is_0
            else:
                cursor = cursor.crit_is_1

            del q[0]
            q.append(cursor)
        return q  # grand, pa, des

    def print(self):
        if self.root is None:
            print('empty')
        elif isinstance(self.root, CBInternal):
            self.root.print()
        else:
            print(self.root)