import re
import bisect

SEG = [0.2, 0.5, 0.8]
# 存储各字符的分类结果（'Strong', 'Medium', 'Weak'）
char_category = {}
# 存储各字符对应的模糊隶属度
char_membership = {}

def strong_membership(x, seg):
    """计算三角隶属函数值"""
    a, m, b = seg
    if x <= m:
        return 0
    elif m < x < b:
        return (x - m) / (b - m)
    else:
        return 1


def medium_membership(x, seg):
    """计算三角隶属函数值"""
    a, m, b = seg
    if x <= a or x >= b:
        return 0
    elif m < x < b:
        return (b - x) / (b - m)
    else:
        return (x - a) / (m - a)


def weak_membership(x, seg):
    """计算三角隶属函数值"""
    a, m, b = seg
    if x >= m:
        return 0
    elif a < x < m:
        return (m - x) / (m - a)
    else:
        return 1

def read_weights_file(file_path):
    """
    读取文件并转换为指定格式的字典
    :param file_path: 文件路径
    :return: 字典 weights，键为字符串格式的第一个元素，值为第二个元素
    """
    weights = {}

    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as file:
        # 按行读取并处理
        for line in file:
            # 去除换行符并分割行内容
            line = line.strip()
            if line:  # 跳过空行
                parts = line.split()
                if len(parts) == 2:  # 确保每行有两个元素
                    key = str(parts[0])  # 键转换为字符串格式
                    value = float(parts[1]) # 值转换为整数
                    weights[key] = value

    return weights

def generate_char_weights(interest_file):
    """为每个可能字符（a - f 示例，可扩展）随机生成权重"""
    # chars = 'abcdef'
    # weights = {c: random.uniform(0, 1) for c in chars}
    # weights={'a':0.3865,'b':0.4998,'c':0.1434,'d':0.4488,'e':0.7733}
    # weights = {'C': 0.25, 'e': 0.45, 'F': 0.55, 'g': 0.65, 'h': 0.75, 'I': 0.85}
    # weights = {'C': 0.25, 'e': 0.45, 'F': 0.55, 'g': 0.65, 'h': 0.74, 'I': 0.7}
    # weights = {'C': 0.25, 'e': 0.45, 'F': 0.55, 'g': 0.65, 'h': 0.7, 'I': 0.68}

    # file_path = "../datasets/SDB1_interest.txt"
    # file_path = "../datasets/SDB2_interest.txt"
    # file_path = "../datasets/SDB3_interest.txt"
    # file_path = "../datasets/SDB4_interest.txt"
    # file_path = "../datasets/SDB5_interest.txt"
    # file_path = "../datasets/SDB6_interest.txt"
    # file_path = "../datasets/SDB7_interest.txt"
    # file_path = "../datasets/SDB8_interest.txt"
    ##JL
    # file_path = "../datasets/SDB1_u_interest.txt"
    # file_path = "../datasets/SDB2_u_interest.txt"
    # file_path = "../datasets/SDB3_u_interest.txt"
    # file_path = "../datasets/SDB4_u_interest.txt"

    # lunwen
    # weights = {'a': 0.45, 'b': 0.35, 'c': 0.6, 'd': 0.7, 'e': 0.66}
    # file_path = "../datasets/SDB2_yn_interest.txt"

    # file_path = "../datasets/testshuzi_interest.txt"

    weights = read_weights_file(interest_file)

    return weights


def classify_characters(weights):
    """根据权重和隶属函数对字符分类"""
    max_strong_val = 0
    max_weak_val = 0
    for c, w in weights.items():
        strong_val = strong_membership(w, SEG)
        medium_val = medium_membership(w, SEG)
        weak_val = weak_membership(w, SEG)

        max_strong_val = max(strong_val, max_strong_val)
        max_weak_val = max(weak_val, max_weak_val)

        char_membership[c] = {
            'Strong': strong_val,
            'Medium': medium_val,
            'Weak': weak_val
        }

        # if strong_val >= medium_val and weak_val == 0:
        #     char_category[c] = 'Strong'
        # elif weak_val >= medium_val and strong_val == 0:
        #     char_category[c] = 'Weak'
        # else:
        #     char_category[c] = 'Medium'
        if weak_val >= medium_val and weak_val > strong_val:
            char_category[c] = 'Weak'
        elif medium_val >= strong_val and medium_val > weak_val:
            char_category[c] = 'Medium'
        else:
            char_category[c] = 'Strong'
    # 0.622233333+0.166675
    # 输出字符权重和分类结果
    print("\n字符权重和分类结果:")
    print("=" * 60)
    print(f"{'字符':<5}{'权重':<10}{'模糊强隶属度':<15}{'模糊中隶属度':<15}{'模糊弱隶属度':<15}{'分类'}")
    print("-" * 60)
    for c in sorted(weights.keys()):
        print(
            f"{c:<5}{weights[c]:<10.4f}{char_membership[c]['Strong']:<15.4f}{char_membership[c]['Medium']:<15.4f}{char_membership[c]['Weak']:<15.4f}{char_category[c]}")

    # 输出模糊强、中、弱项
    strong_chars = [c for c, cat in char_category.items() if cat == 'Strong']
    medium_chars = [c for c, cat in char_category.items() if cat == 'Medium']
    weak_chars = [c for c, cat in char_category.items() if cat == 'Weak']

    # sm_item = sorted(strong_chars + medium_chars)

    jz_m = max((max_strong_val + max_weak_val) / 2, max_strong_val)
    jz_s = max_strong_val

    print("\n模糊强项:", strong_chars)
    print("模糊中项:", medium_chars)
    print("模糊弱项:", weak_chars)
    print("=" * 60)
    return char_membership, char_category, jz_s, jz_m, strong_chars


class processingData(object):
    def read_file(self, readfilename):
        # 读取的文件名字
        # readFileName = "../dateset/demo.txt"
        lines_s = []
        with open(readfilename, 'r') as f:
            lines = f.readlines()
            for line in lines:
                lines_s.append(line.strip())
        return lines_s  # 返回数组

    # 将数组写入文件
    def write_file(self, lines_s, filename):
        with open(filename, 'w') as f:
            for i in range(len(lines_s)):
                f.writelines(str(i) + "\t" + lines_s[i])
                f.write("\n")

    # 项集去重 排序
    # sort_items  去重排序后的项集数组
    # items_no_repeat  存在重复的未排序的项集数组
    def item_sotrd(self, items):
        items_no_repeat = []
        for item in items:
            if item not in items_no_repeat:
                items_no_repeat.append(item)
        # self.write_file(items_no_repeat, 'item_norepeat.txt')
        sort_items = list(sorted(items_no_repeat))
        # 去重排序后的项集
        # print(sort_items)
        # print(type(sort_date))
        return sort_items, items_no_repeat

    # 定义空的数据字典
    '''
    S =
    {
    'a': [[0, 1, 3], [1], [0, 2, 4], [0, 1], [1, 3]],
    'b': [[], [0], [2], [0], [4]],
    'c': [[0, 1, 2, 3, 4], [1, 2], [0, 2, 3, 4, 5], [0, 1, 2, 3], [0, 1, 2, 3, 5]],
    'd': [[], [3], [0], [], [0, 3]],
    'e': [[], [1, 3], [4, 5], [3, 4], [5]],
    'f': [[], [0], [1, 4], [4], []]
    }
    '''

    def item_to_dict(self, sort_items, len_lines, S):
        # sort_items 排序去重之后的项
        # len_lines 序列数
        # S = {}
        for i in sort_items:
            # S[i] = {}
            S[i] = [[] for i in range(len_lines)]
            # S[str(i)]['mul'] = [[] for i in range(len_lines)]
        # print (S)
        return S

    # 替换字符串为项集(按字符串的大小)
    def replace_seq(self, lines_s, sort_item):
        # print(sort_item)
        # print(lines_s)
        flag = 1
        for i in range(len(sort_item)):
            for j in range(len(lines_s)):
                if flag == 1:
                    lines_s[j] = lines_s[j] + " "
                # lines_s[j] = lines_s[j].replace(sort_item[i], str(i))
                p1 = re.compile(" " + sort_item[i] + " ")
                lines_s[j], number = re.subn(p1, " " + str(i) + "* ", lines_s[j])
            # print(lines_s)
            # print(number)
            # print_array(lines_s)
            flag = 0
        for i in range(len(lines_s)):
            lines_s[i] = lines_s[i].replace('*', '')
        return lines_s

    # 分割字符串数组返回[]和[[],[],[]]
    def split_array(self, lines):
        # lines =  0 2 -1 0 2 -1 2 -1 0 2 -1 2
        lines = lines.replace('  ', ' ')
        # print(lines)
        items_array = lines.strip().split(' ')  # 按空格分隔成一个一个的项和-1
        # print(items_array)
        s_array = [[]]  # 二维数组
        i = 0
        for item in items_array:
            if item != '-1':
                s_array[i].append(item)
            else:
                i = i + 1
                s_array.append([])
        # print(s_array)
        return items_array, s_array

    #  lines  0 2 -1 0 2 -1 2 -1 0 2 -1 2
    #  items_array  ['0', '2', '-1', '0', '2', '-1', '2', '-1', '0', '2', '-1', '2']
    #  s_array  [['0', '2'], ['0', '2'], ['2'], ['0', '2'], ['2']]

    def Statistics_items(self, lines, items):
        # lines =  "177 179 410 454 468 470 474 475 513 588 871 872 873 1142 1011 1107  -1 854 854 854  -1 730 761 859 861 864 870 918 919 927  -1 436 1199  -1 859  -1 919  -1 70 153 217 235 255 256 283 318 360 361 376 436 464 464 693 736 736 736 737 751 775 776 777 800 801 871 872 881 888 900 910 916 940 1039 1094 1116  -1 139 262 301 325 452 477 497 711 1034 1097 1099 1179 1107 1154  -1 119 120 121 548 642 691 776 817 837 848 910 911 912 917 919 966 1099 966B  -1 248 362 427 451 460 470 494 495 588 594 595 659 660 662 663 664 665 666 667 679 680 691 691 692 693 694 695 696 699 704 708 708 708 761 775 776 777 778 799 840 841 871 872 873 887 888 909 912 1088 1095 1135  -1 17 43 118 119 190 269 453 529 633 708 708 708 736 784 785 787 826 826 833 863 887 908 920 1096 1096 1011 1011 1041 1055 1055 1060 1130 1157  -1 307 308 715 716 718 819  -1 301 489 1154  -1 34 152 191 238 309 371 471 612 634 635 684 750 759 827 977 1026 1028 1097 1098 1163 975 1030  -1 44 90 104 319 338 373 555 585 634 661 662 665 666 666 667 675 749 1179 13 1062 1107"
        lines = lines.replace('  ', ' ')  # 将两个空格替换成一个空格 所有项之间都保持一个空格
        items_array = lines.strip().split(' ')  # 按空格分隔序列 收集所有的项 包含重复
        for item in items_array:
            if item != '-1' and item not in items:  # 如果项不是项集分隔符并且没有在items中重复就将项保存在items
                items.append(item)
        # print_array(items)
        return items  # 返回不重复的项的集合(无序的 按照在序列中出现先后的顺序)

    # 生成数据字典格式
    def General_Se(self, lines_s):
        # print('&'+str(sort_item))
        # 数据处理后的最终结果
        # itemcount = 0
        # original_sequences = []
        sequences = []
        valid_chars = []

        for i in range(len(lines_s)):
            # print(lines_s)
            items_array, s_array = self.split_array(lines_s[i])

            sequences.append(s_array)
            # original_sequences.append(s_array)
            # for j in s_array:
            #     itemcount += len(j)
            #  lines_s[i]  0 2 -1 0 2 -1 2 -1 0 2 -1 2
            #  items_array  ['0', '2', '-1', '0', '2', '-1', '2', '-1', '0', '2', '-1', '2']
            #  s_array  [['0', '2'], ['0', '2'], ['2'], ['0', '2'], ['2']]
            sort_item, items_no_repeat = self.item_sotrd(items_array)

            for c in sort_item:
                if c != '-1' and char_category[c] in ['Strong', 'Medium'] and c not in valid_chars:
                    valid_chars.append(c)

            # print('$',sort_item)
            # sort_item 第i条序列去重排序之后的项 ['-1', '0', '2']
            # print(sort_item)
            # for item in sort_item:
            #     if item != '-1':
            #         for k in range(len(s_array)):
            #             if item in s_array[k] and item in valid_chars:
            # index = str(sort_item.index(item))
            # print(item)
            # print(i)
            # print(k)
            # print('$$$$$$$$$$$$$$$')
            # S[item][i].append(k)
            # if len(s_array[k]) > 1:
            #     S[item]['mul'][i].append(k)
        # print(itemcount)
        return sequences,valid_chars

    def build_pl_map(self, sequences, S, sm_chars, strong_chars):
        num_seqs = len(sequences)  # 序列总数，seq_num范围：0 ~ num_seqs-1

        # 1. 收集每个序列（按seq_num）中所有强字符的位置（按项集索引排序）
        strong_pos = []  # 索引=seq_num，值=当前序列中所有强字符出现的项集索引列表（升序）
        for seq_num in range(num_seqs):
            itemsets = sequences[seq_num]
            # 记录当前序列中包含任意强字符的项集索引
            s_pos = []
            for itemset_idx, itemset in enumerate(itemsets):
                # 检查当前项集是否包含任何强字符
                if any(char in itemset for char in strong_chars):
                    s_pos.append(itemset_idx)
            strong_pos.append(s_pos)  # 已按项集索引顺序添加，天然有序

        # 2. 收集每个字符在各序列（按seq_num）中的出现位置
        char_info = {}  # {字符: [ [seq0中出现的项集索引], [seq1中出现的项集索引], ... ]}
        # all_chars = set()
        for seq_num in range(num_seqs):
            itemsets = sequences[seq_num]
            for itemset_idx, itemset in enumerate(itemsets):
                for char in itemset:
                    # all_chars.add(char)
                    if char in sm_chars:
                        if char not in char_info:
                            # 初始化每个序列的位置列表（用空列表占位）
                            char_info[char] = [[] for _ in range(num_seqs)]
                        # 记录当前字符在当前序列中的位置
                        char_info[char][seq_num].append(itemset_idx)

        # 3. 生成结果：按字符整理，每个字符的列表按seq_num顺序排列子列表
        result = {}
        for char in sorted(sm_chars):  # 按字符字母序排序
            # char_result = []
            # 按序列编号遍历（0,1,...）
            for seq_num in range(num_seqs):
                # 当前字符在当前序列中的所有出现位置
                pos_list = char_info[char][seq_num]
                if not pos_list:  # 若当前序列中无该字符，跳过
                    continue
                # 获取当前序列的所有强字符位置列表
                s_pos = strong_pos[seq_num]
                # 计算每个位置对应的下一个强字符（任意强字符）位置
                seq_tuples = []
                for pos in pos_list:
                    # 二分查找第一个大于当前位置的强字符索引
                    idx = bisect.bisect_right(s_pos, pos)
                    next_s_pos = s_pos[idx] if idx < len(s_pos) else None
                    seq_tuples.append((pos, next_s_pos))
                S[char][seq_num]=seq_tuples
            # result[char] = char_result
        return S

    def datap(self, readFileName, S,interest_file):
        # S = {}
        # 读取的文件名字
        # readFileName = "../dataset/online-fin.txt"
        # readFileName = "../dataset/demo/test.txt"
        # 文件读取后的字符串数组 序列集合S
        lines_s = self.read_file(readFileName)
        # print(lines_s)

        # items 项集 统计后的项集(序列中出现的字符集 按照在序列中出现的次序)
        items = []
        for lines in lines_s:
            items = self.Statistics_items(lines, items)
        # print(items)

        # sort_item 排序后的项集字符串数组
        # date_no_repeat 未排序的项 在序列中出现的次序
        sort_item, items_no_repeat = self.item_sotrd(items)
        # 输出 sort_item
        # print_array(sort_item)
        # print_array(items_no_repeat)
        # 将sort_item数组写入文件sort_item.txt
        # self.write_file(sort_item, 'sort_item.txt')
        #
        # 替换数据集中的字符串lines_s 替换后的字符串数组
        # print(lines_s)
        # lines_s = self.replace_seq(lines_s, sort_item)
        # print(lines_s)
        # self.write_file(lines_s, "demo2.txt")
        # print(lines_s)
        # print_array(lines_s)
        # print(len(lines_s))
        weights = generate_char_weights(interest_file)
        char_membership, char_category, jz_s, jz_m, strong_item = classify_characters(weights)

        self.item_to_dict(sort_item, len(lines_s), S)  # 排序后的项 和 序列数
        # print(lines_s)

        sequences,sm_item = self.General_Se(lines_s)

        S = self.build_pl_map(sequences, S, sm_item, strong_item)

        return sequences,len(lines_s), S, sm_item, char_membership, char_category, jz_m,weights

    def utilityp(self, readFileName, U):
        lines_s = self.read_file(readFileName)
        for lines in lines_s:
            key_value = lines.strip().split(' ')
            U[key_value[0]] = key_value[1]
        # print(U)

    def __del__(self):
        pass
