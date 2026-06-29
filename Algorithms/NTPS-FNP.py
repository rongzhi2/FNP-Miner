import copy
import sys
import time
import gc
import os
import csv

# import pandas as pd

import PdataFtnpstr

pdata = PdataFtnpstr.processingData()
from memory_profiler import memory_usage

# import taichi as ti
# ti.init()
# @ti.kernel

CanNum = 0

original_sequences = []


def compute_support(pl_map, pattern):
    result = []
    n = len(pattern)
    if n == 0:
        return result


    first_char = str([pattern[0]])
    if first_char not in pl_map:
        return result
    seq_count = len(pl_map[first_char])
    result = [[] for _ in range(seq_count)]


    for seq_num in range(seq_count):
        current_pl = {}
        valid = True
        for char in pattern:
            char = str([char])
            if char not in pl_map or seq_num >= len(pl_map[char]):
                valid = False
                break
            current_pl[char] = pl_map[char][seq_num]
            if not current_pl[char]:
                valid = False
                break
        if not valid:
            continue

        ptr = [0] * n
        first_nodes = current_pl[first_char]
        if not first_nodes:
            continue

        current_level = 1
        pre_pos, pre_strong = first_nodes[ptr[0]]
        current_char = str([pattern[current_level]])
        current_nodes = current_pl[current_char]

        while current_nodes and ptr[current_level] < len(current_nodes):
            curr_pos, curr_strong = current_nodes[ptr[current_level]]


            if curr_pos <= pre_pos:
                ptr[current_level] += 1
                continue


            if pre_strong is not None and curr_pos > pre_strong:
                current_level -= 1
                ptr[current_level] += 1

                if current_level == 0 and ptr[0] >= len(first_nodes):
                    break
                if current_level == 0:
                    pre_pos, pre_strong = first_nodes[ptr[0]]
                    current_level = 1
                else:
                    pre_char = str([pattern[current_level - 1]])
                    pre_nodes = current_pl[pre_char]
                    pre_pos, pre_strong = pre_nodes[ptr[current_level - 1]]

                current_char = str([pattern[current_level]])
                current_nodes = current_pl[current_char]
                continue


            if current_level == n - 1:

                occ = tuple(current_pl[str([pattern[i]])][ptr[i]][0] for i in range(n))
                result[seq_num].append(occ)


                for i in range(n):
                    ptr[i] += 1

                if ptr[0] >= len(first_nodes):
                    break


                pre_pos, pre_strong = first_nodes[ptr[0]]
                current_level = 1
                current_char = str([pattern[current_level]])
                current_nodes = current_pl[current_char]
                continue


            pre_pos, pre_strong = curr_pos, curr_strong
            current_level += 1
            current_char = str([pattern[current_level]])
            current_nodes = current_pl[current_char]
    total_count = 0
    local_sups = [0] * SeqNum
    for i, seq_matches in enumerate(result):
        local_sups[i] = len(seq_matches)
        total_count += len(seq_matches)
    return total_count, result, local_sups


# @ti.func
def Matching_I(list1, list2, SeqNum, strong_num):
    """交集匹配（Intersection - based Matching），计算共同位置数量及新位置列表"""
    list3 = [[] for _ in range(SeqNum)]
    count = 0
    fsup = 0
    local_sups = [0] * SeqNum
    local_fsups = [0.0] * SeqNum
    for i in range(SeqNum):
        # 求集合交集并排序
        common = sorted(list(set(list1[i]) & set(list2[i])))
        list3[i] = common
        l = len(common)
        count += l
        tfsup = strong_num * l
        fsup += tfsup
        local_fsups[i] = tfsup
        local_sups[i] = l
    return count, list3, fsup, local_fsups, local_sups


def Mine_ItemS(FNP, ItemS, sm_item, SeqNum, minsup):
    global CanNum
    CanFNP = []

    for i in sm_item:  # a b c d e f
        CanNum += 1
        count = 0
        local_fsups = [0.0] * SeqNum
        local_sups = [0] * SeqNum
        for j in range(SeqNum):
            count += len(S[i][j])
            local_sups[j] = len(S[i][j])
        if count * jz_m >= minsup:  # 判断是否加入候选模式集
            p = []
            p.append(i)
            CanFNP.append([p])
            ItemS[str([p])] = [[] for k in range(SeqNum)]
            ItemS[str([p])] = S[i]
            # 计算OMV值
            fsup = 0
            for seq_idx in range(SeqNum):
                if ItemS[str([p])][seq_idx]:
                    # 单出现的隶属度
                    omv_sg = char_membership.get(i, {}).get('Strong', 0)
                    # omv_values_strong_dict[str([p])] = omv_sg
                    omv = omv_sg * len(ItemS[str([p])][seq_idx])
                    fsup += omv
                    local_fsups[seq_idx] = omv

            # if omv_values:
            #     sum_omv = sum(omv_values)

            if fsup >= minsup:  # 用minsup作为频繁模式集的阈值
                FNP.append([p])
                local_fsup_dict[str([p])] = local_fsups
                local_sup_dict[str([p])] = local_sups
                # print(p, fsup)
    return FNP, ItemS, CanFNP


def two_len(FNP, CanFNP, ItemS):
    '''
    生成频繁模式集size=2,[ab],[a][b]
    :return:
    '''
    global CanNum
    global GIL
    dicTwoLenPattern = {}

    Item = copy.deepcopy(CanFNP)
    CanFNP = []
    for pre in range(len(Item)):
        for suf in range(pre + 1, len(Item)):
            t = copy.deepcopy(Item[pre][0])
            t.append(Item[suf][0][0])
            p = [t]
            CanNum += 1
            # print(str(Item[pre]), str(Item[suf]), ItemS.keys())
            strong_num = 0
            for char in t:
                strong_num += char_membership.get(char, {}).get('Strong', 0)
            strong_num /= 2

            count, ItemS[str(p)], fsup, local_fsups, local_sups = Matching_I(ItemS[str(Item[pre])],
                                                                             ItemS[str(Item[suf])], SeqNum, strong_num)

            if count * jz_m >= minsup:  # 判断是否加入候选模式集
                CanFNP.append(p)

                if dicTwoLenPattern.get(str([Item[pre][0]])) is None:
                    dicTwoLenPattern[str([Item[pre][0]])] = []
                dicTwoLenPattern[str([Item[pre][0]])].append(p)

                if fsup >= minsup:  # 用minsup作为频繁模式集的阈值
                    FNP.append(p)
                    local_fsup_dict[str(p)] = local_fsups
                    local_sup_dict[str(p)] = local_sups
                    # print(p, fsup)

            else:
                del ItemS[str(p)]
    for m in Item:
        pre = copy.deepcopy(m)
        for n in Item:
            suf = copy.deepcopy(n)
            p = [pre[0], suf[0]]
            # if p==[['d'], ['d']]:
            #     ll=0
            CanNum += 1
            count, all_occ, local_sups = compute_support(ItemS, p)
            gils = 0
            local_fsups = [0.0] * SeqNum
            if count * jz_m >= minsup:  # 判断是否加入候选模式集
                CanFNP.append(p)
                if dicTwoLenPattern.get(str([pre[0]])) is None:
                    dicTwoLenPattern[str([pre[0]])] = []

                dicTwoLenPattern[str([pre[0]])].append(p)

                fsup = 0
                strong_num = 0
                cnt = 0
                for item in p:
                    for char in item:
                        strong_num += char_membership.get(char, {}).get('Strong', 0)
                        cnt += 1
                strong_num /= cnt

                for i in range(SeqNum):
                    occ_s = all_occ[i]
                    tfsup = 0
                    for j in range(len(occ_s)):
                        occ = occ_s[j]  # 单次出现的位置列表（整数）
                        weakm = 0.0  # 间隙弱成员度均值
                        gap = 0  # 间隙长度
                        gil = 0

                        # 计算当前出现的间隙弱成员度
                        for k in range(len(occ) - 1):
                            # 遍历间隙中的每个位置
                            for m in range(occ[k] + 1, occ[k + 1]):
                                # 获取对应序列
                                for char in original_sequences[i][m]:
                                    # if char_category.get(char, 'Medium') == 'Strong':
                                    #     weakm -= char_membership.get(char, {}).get('Strong', 0)
                                    # else:
                                    weakm += char_membership.get(char, {}).get('Weak', 0)
                                    gap += 1
                                    gil += weights[char]

                        # 累加当前出现的模糊支持度
                        if gap == 0:
                            fsup += strong_num
                            tfsup += strong_num
                        else:
                            weakm /= gap
                            fsup += (strong_num + weakm) / 2.0
                            gils += gil / gap
                            tfsup += (weakm + strong_num) / 2
                    local_fsups[i] = tfsup

                if fsup >= minsup:  # 用minsup作为频繁模式集的阈值
                    FNP.append(p)
                    local_sup_dict[str(p)] = local_sups
                    local_fsup_dict[str(p)] = local_fsups
                    GIL += gils / count

    return CanFNP, dicTwoLenPattern


def more_len(FNP, ItemS, ExpSet, ExpSetDict):
    '''
    生成频繁模式集size>2
    :return:
    '''
    # ExpSet = Exppattern[:]
    global CanNum
    global flag_p
    global GIL
    cnt = 3
    while ExpSet != []:
        temp = ExpSet[:]
        ExpSet = []
        dictmp = copy.deepcopy(ExpSetDict)
        # dictmp = ExpSetDict.copy()
        ExpSetDict = {}
        for m in temp:
            suf = copy.deepcopy(m)
            suf[0].pop(0)
            # print(str(suf))
            # print(m)
            if suf[0] == []:
                sufstr = str(suf[1:])

            else:
                sufstr = str(suf)
            if dictmp.get(sufstr) is None:
                continue
            temp1 = dictmp[sufstr]
            for n in temp1:
                if len(n[-1]) == 1:
                    # if str(m[0][0]) in SItems.keys():  # 剪枝1
                    # if str(n[-1][0]) in SItems[str(m[0][0])].keys():  # 剪枝2
                    pattern = copy.deepcopy(m)
                    pattern.append(n[-1])
                    CanNum += 1
                    local_fsups = [0.0] * SeqNum
                    # print(pattern)
                    # if flag_p is True:
                    #     flag_p = False
                    # if pattern == [['c'], ['d'], ['d']]:
                    #     flag_p = True

                    count, all_occ, local_sups = compute_support(ItemS, pattern)
                    gils = 0

                    if count * jz_m >= minsup:  # 判断是否加入候选模式集
                        ExpSet.append(pattern)

                        if ExpSetDict.get(str(m)) is None:
                            ExpSetDict[str(m)] = []
                        ExpSetDict[str(m)].append(pattern)

                        fsup = 0
                        strong_num = 0
                        for item in pattern:
                            for char in item:
                                strong_num += char_membership.get(char, {}).get('Strong', 0)
                        strong_num /= cnt

                        for i in range(SeqNum):
                            occ_s = all_occ[i]
                            tfsup = 0
                            for j in range(len(occ_s)):
                                occ = occ_s[j]  # 单次出现的位置列表（整数）
                                weakm = 0.0  # 间隙弱成员度均值
                                gap = 0  # 间隙长度
                                gil = 0

                                # 计算当前出现的间隙弱成员度
                                for k in range(len(occ) - 1):
                                    # 遍历间隙中的每个位置
                                    for po in range(occ[k] + 1, occ[k + 1]):
                                        # 获取对应序列
                                        for char in original_sequences[i][po]:
                                            # if char_category.get(char, 'Medium') == 'Strong':
                                            #     weakm -= char_membership.get(char, {}).get('Strong', 0)
                                            # else:
                                            weakm += char_membership.get(char, {}).get('Weak', 0)
                                            gap += 1
                                            gil += weights[char]

                                # 累加当前出现的模糊支持度
                                if gap == 0:
                                    fsup += strong_num
                                    tfsup += strong_num
                                    # if flag_p is True:
                                    #     print(fsup)
                                else:
                                    weakm /= gap
                                    fsup += (strong_num + weakm) / 2.0
                                    tfsup += (strong_num + weakm) / 2.0
                                    gils += gil / gap
                                    # if flag_p is True:
                                    #     print(fsup)
                            local_fsups[i] = tfsup

                        if fsup >= minsup:  # 用minsup作为频繁模式集的阈值
                            FNP.append(pattern)
                            local_sup_dict[str(pattern)] = local_sups
                            local_fsup_dict[str(pattern)] = local_fsups
                            GIL += gils / count

                else:
                    pattern = copy.deepcopy(m)
                    # (pattern)
                    # print(pattern)
                    pattern[-1].append(n[-1][-1])
                    CanNum += 1
                    local_fsups = [0.0] * SeqNum

                    # count = 0
                    # print(pattern)
                    # print("@@@@@")
                    if len(pattern) > 1:
                        # if str(pattern[-1][-1]) in SItems[str(pattern[0][0])].keys():  # 剪枝4
                        count, all_occ, local_sups = compute_support(ItemS, pattern)
                        gils = 0

                        if count * jz_m >= minsup:  # 判断是否加入候选模式集
                            ExpSet.append(pattern)
                            if ExpSetDict.get(str(m)) is None:
                                ExpSetDict[str(m)] = []
                            ExpSetDict[str(m)].append(pattern)

                            fsup = 0
                            strong_num = 0
                            for item in pattern:
                                for char in item:
                                    strong_num += char_membership.get(char, {}).get('Strong', 0)
                            strong_num /= cnt

                            for i in range(SeqNum):
                                occ_s = all_occ[i]
                                tfsup = 0
                                for j in range(len(occ_s)):
                                    occ = occ_s[j]  # 单次出现的位置列表（整数）
                                    weakm = 0.0  # 间隙弱成员度均值
                                    gap = 0  # 间隙长度
                                    gil = 0

                                    # 计算当前出现的间隙弱成员度
                                    for k in range(len(occ) - 1):
                                        # 遍历间隙中的每个位置
                                        for po in range(occ[k] + 1, occ[k + 1]):
                                            # 获取对应序列
                                            for char in original_sequences[i][po]:
                                                # if char_category.get(char, 'Medium') == 'Strong':
                                                #     weakm -= char_membership.get(char, {}).get('Strong', 0)
                                                # else:
                                                weakm += char_membership.get(char, {}).get('Weak', 0)
                                                gap += 1
                                                gil += weights[char]

                                    # 累加当前出现的模糊支持度
                                    if gap == 0:
                                        fsup += strong_num
                                        tfsup += strong_num
                                        # if flag_p is True:
                                        #     print(fsup)
                                    else:
                                        weakm /= gap
                                        fsup += (strong_num + weakm) / 2.0
                                        tfsup += (strong_num + weakm) / 2
                                        gils += gil / gap
                                        # if flag_p is True:
                                        #     print(fsup)
                                local_fsups[i] = tfsup

                            if fsup >= minsup:  # 用minsup作为频繁模式集的阈值
                                FNP.append(pattern)
                                local_sup_dict[str(pattern)] = local_sups
                                local_fsup_dict[str(pattern)] = local_fsups
                                GIL += gils / count
                    else:
                        # print(m,n[-1])
                        # if str(pattern[-1][-1]) in SItem[str(pattern[0][0])].keys():  # 剪枝3
                        strong_num = 0
                        for item in pattern:
                            for char in item:
                                strong_num += char_membership.get(char, {}).get('Strong', 0)
                        strong_num /= cnt

                        count, ItemS[str(pattern)], fsup, local_fsups, local_sups = Matching_I(ItemS[str(m)], ItemS[
                            str([[n[-1][-1]]])], SeqNum,
                                                                                               strong_num)

                        if count * jz_m >= minsup:  # 判断是否加入候选模式集
                            ExpSet.append(pattern)

                            if ExpSetDict.get(str(m)) is None:
                                ExpSetDict[str(m)] = []
                            ExpSetDict[str(m)].append(pattern)

                            if fsup >= minsup:  # 用minsup作为频繁模式集的阈值
                                FNP.append(pattern)
                                local_fsup_dict[str(pattern)] = local_fsups
                                local_sup_dict[str(pattern)] = local_sups
                                # print(pattern, fsup)

                        else:
                            del ItemS[str(pattern)]
        cnt += 1
    return FNP


# @ti.kernel


def Miner():
    # global CanNum,UBP,CandiNum

    FNP = []
    ItemS = {}
    global GIL
    GIL = 0

    global local_fsup_dict
    local_fsup_dict = {}

    global local_sup_dict
    local_sup_dict = {}

    print(f"\n开始挖掘频繁模式 (最小支持度: {minsup})...")

    FNP, ItemS, CanFNP = Mine_ItemS(FNP, ItemS, sm_item, SeqNum, minsup)
    # print("\n1长度CanFNP:", CanFNP)

    twoLenPattern, dictTwoLen = two_len(FNP, CanFNP, ItemS)
    # print("\n2长度FNP:", FNP)
    # print("\n2长度CanFNP:", twoLenPattern)
    # print(len(twoLenPattern))
    FNP = more_len(FNP, ItemS, twoLenPattern, dictTwoLen)

    print("\n频繁模式及其OMV值:")

    IL = 0

    for i in range(len(FNP)):
        count = 0
        il = 0
        for j in range(len(FNP[i])):
            for char in FNP[i][j]:
                il += weights[char]
                count += 1
        il /= count
        IL += il
    if len(FNP) != 0:
        IL /= len(FNP)

    print("\n兴趣度水平:", IL)
    if len(FNP) != 0:
        GIL /= len(FNP)
    print("\n间隙兴趣度水平:", GIL)

    # 按OMV值排序输出
    # sorted_patterns = sorted(pattern_omv_map.items(), key=lambda x: x[1], reverse=True)

    print("\n统计信息:")
    print("频繁模式数量:", len(FNP))
    for c in FNP:
        print(str(c), end=',')
    print("\n候选模式数量:", CanNum)

    output_dir = "../../output/NTPS"
    os.makedirs(output_dir, exist_ok=True)

    fnp_local_path = os.path.join(output_dir, f"NTPS_local_fsup_{dataset_name}.csv")
    try:
        with open(fnp_local_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["sample_id", "pattern", "sup", "fsup"])
            # writer.writerow(["sample_id", "pattern", "sup", "fsup", "IL"])
            for pattern in FNP:
                pattern_str = str(pattern)
                local_fsups = local_fsup_dict.get(pattern_str, [0.0] * SeqNum)
                local_sups = local_sup_dict.get(pattern_str, [0] * SeqNum)
                for seq_idx in range(SeqNum):
                    local_fsup = local_fsups[seq_idx]
                    local_sup = local_sups[seq_idx]
                    if local_sup > 1e-6:
                        writer.writerow([seq_idx + 1, pattern_str, local_sup, round(local_fsup, 4)])
        print(f"✅ NTPS局部模糊支持度已写入: {fnp_local_path}")
    except Exception as e:
        print(f"写入NTPS_local_fsup.csv失败：{e}")


if __name__ == '__main__':

    dataset_config = [
        ("../../datasets/SDB1.txt", 300, "../../datasets/SDB1_interest.txt"),
        ("../../datasets/SDB2.txt", 500, "../../datasets/SDB2_interest.txt"),
        ("../../datasets/SDB3.txt", 100, "../../datasets/SDB3_interest.txt"),
        ("../../datasets/SDB4.txt", 200, "../../datasets/SDB4_interest.txt"),
        ("../../datasets/SDB5.txt", 700, "../../datasets/SDB5_interest.txt"),
        ("../../datasets/SDB6.txt", 70, "../../datasets/SDB6_interest.txt"),
        ("../../datasets/SDB7.txt", 100, "../../datasets/SDB7_interest.txt"),
        ("../../datasets/SDB8.txt", 800, "../../datasets/SDB8_interest.txt")
    ]


    class Logger(object):
        def __init__(self, filename="运行结果.txt"):
            self.terminal = sys.stdout
            self.log = open(filename, "w", encoding="utf-8")

        def write(self, message):
            self.terminal.write(message)
            self.log.write(message)

        def flush(self):
            pass


    sys.stdout = Logger("NTPS-FNP实验结果.txt")

    print("=" * 80)
    print("           开始执行模糊序列模式挖掘算法（结果已保存到文件）")
    print("=" * 80)


    for readFileName, minsup, interest_file in dataset_config:
        gc.collect()
        # global CanNum
        CanNum = 0
        # flag_p = False
        dataset_name = os.path.basename(readFileName).split(".")[0]

        for var in ['SeqNum', 'S', 'sm_item', 'original_sequences',
                    'char_membership', 'char_category', 'jz_m', 'weights']:
            if var in globals():
                del globals()[var]
        gc.collect()

        print("\n" + "=" * 90)
        print(f" 正在运行 → 数据集：{readFileName}")
        print(f"           最小支持度：{minsup}")
        print(f"           兴趣度文件：{interest_file}")
        print("=" * 90)

        starttime = time.time()
        S = {}

        # 运行预处理 + 内存监控
        mem_pdata, (
            original_sequences, SeqNum, S, sm_item, char_membership, char_category, jz_m, weights) = memory_usage(
            (pdata.datap, (readFileName, S, interest_file)),
            max_iterations=1,
            retval=True
        )

        flag_p = False

        # 运行挖掘算法
        mem_miner = memory_usage((Miner,), max_iterations=1)
        total_mem = mem_pdata + mem_miner
        endtime = time.time()

        # 输出结果
        print(f"\n 运行完成：")
        print(f" 数据集：{readFileName}")
        print(f" 支持度：{minsup}")
        print(f" 运行时间：{int(round(endtime * 1000)) - int(round(starttime * 1000))} ms")
        print(f" 总内存消耗：{max(total_mem) - min(total_mem)} MB")
        print("=" * 90 + "\n\n")
