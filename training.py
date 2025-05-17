"""
训练模块：提供单词学习和测试功能，支持选择题、填空题等多种测试模式。
模块包含核心测试逻辑、输入校验及不同测试模式的入口函数。
"""

import random
from collections import deque

from file_io import read_words, write_words, save_old_file
from utils import *

def check_if_right_num(input_str: str) -> int | None:
    """
    校验用户输入是否为1-4之间的有效数字

    :param input_str: 用户输入的字符串
    :return:
        int - 解析后的有效数字(1-4)
        None - 无效输入时的返回结果
    """
    try:
        input_num = int(input_str)
        # 检查数字范围是否合法
        if not 1 <= input_num <= 4:
            print("输入数字大小错误！")
            return None
        return input_num
    except ValueError:
        print("请输入1-4之间的数字！")
        return None


def conduct_test(words: list[str], meanings: list[str], test_mode: int) -> None:
    """
    测试执行核心逻辑，支持三种测试模式：
    1. 单词到释义（选择题）
    2. 释义到单词（选择题）
    3. 释义到默写（填空题）

    :param words: 单词列表（包含占位符）
    :param meanings: 释义列表（包含占位符）
    :param test_mode: 测试模式标识(1/2/3)
    """

    # 确保测试词库至少有5个条目（不足时填充占位符）
    length = len(words)
    while length < 5:
        words.append(f"####{length}")
        meanings.append(f"#@#@{length}\n#@#@{length}\n#@#@{length}")
        length += 1

    original_meanings = meanings.copy()

    if test_mode == 1:
        for changing_idx in range(length):
            if words[changing_idx].startswith('#'):
                continue
            words[changing_idx] += '\n' + print_pron(meanings[changing_idx].split('\n')[0])


    meanings = [filter_meanings(meaning) for meaning in meanings]

    # 根据测试模式确定问题和答案的对应关系
    questions = words
    answers = meanings

    # 创建双重随机队列实现题目轮询机制
    shuffled_indices = list(range(length))
    random.shuffle(shuffled_indices)
    shuffled_indices = deque(shuffled_indices)

    if test_mode in (2, 3):
        questions, answers = answers, words  # 交换问题和答案

    wrong_words = []  # 记录错误单词
    wrong_meanings = []  # 记录错误释义
    is_choice_question = (test_mode != 3)  # 模式3为填空题

    # 遍历所有题目进行测试
    for num_tested_words in range(length):
        # 环形队列操作保证题目循环
        current_index = shuffled_indices[-1]
        shuffled_indices.pop()
        shuffled_indices.appendleft(current_index)

        # 跳过占位符题目（格式为####开头）
        if questions[current_index].startswith('#'):
            continue

        # 展示进度
        print(f"\n\n\n{num_tested_words+1}/{length}")
        # 展示当前问题
        print_with_single_line_length(f'\n{questions[current_index]}\n')

        # 处理选择题模式
        if is_choice_question:
            # 生成包含正确答案的选项列表
            shuffled_indices.popleft()  # 临时移除当前索引
            options = random.sample(shuffled_indices, 3)  # 随机选取3个干扰项
            shuffled_indices.appendleft(current_index)  # 恢复当前索引

            options.append(current_index)  # 加入正确答案
            random.shuffle(options)  # 打乱选项顺序
            correct_answer = options.index(current_index)  # 记录正确答案位置

            # 显示所有选项
            for i, option_index in enumerate(options):
                print_with_single_line_length(f"{i+1}:\n{answers[option_index]}\n")
        else:
            # 填空题模式直接记录正确答案
            correct_answer = answers[current_index]

        # 用户答题处理（最多3次尝试）
        remain_chance = 3
        while remain_chance > 0:
            prompt = "请输入选项数字：" if is_choice_question else "请输入单词："
            user_input = scan_and_write_to_log(prompt)

            if user_input == '0':
                print("已跳过")
                remain_chance = 0
                break
            if user_input == 'quit()':
                print("已退出")
                write_words(
                    get_file_name_by_index(test_mode)+"__quited",
                    wrong_words, wrong_meanings,
                    False)
                return None

            # 选择题模式需要校验输入格式
            if is_choice_question:
                processed_input = check_if_right_num(user_input)
                if processed_input is None:
                    continue  # 输入无效时重新提示
                processed_input -= 1  # 转换为0-based索引
            else:
                processed_input = user_input.strip()

            # 答案校验
            if processed_input == correct_answer:
                print("√答案正确！")
                break
            else:
                remain_chance -= 1
                print(f"×答案错误，剩余尝试次数：{remain_chance}")

        # 记录错误答案
        if remain_chance == 0:
            print("已加入错题本")
            current_word = words[current_index]
            if test_mode == 1:
                current_word = current_word.split('\n')[0]
            wrong_words.append(current_word)
            wrong_meanings.append(original_meanings[current_index])

    # 将错误记录写入对应文件
    write_words(get_file_name_by_index(test_mode),
                wrong_words,
                wrong_meanings,
                False)

def test_words(file_index: int, test_mode: int, backup_old_wrong: bool) -> None:
    """
    测试执行入口函数，根据测试模式调用相应的测试函数
    :param file_index: 词库文件索引
        0 - 默认词库
        1 - 自定义词库
        2 - 错误记录词库
        3 - 默写测试词库
        4 - 临时单词本
    :param test_mode: 测试模式标识(1/2/3)
        1 - 单词到释义测试
        2 - 释义到单词测试
        3 - 释义到默写测试
    :param backup_old_wrong: 是否备份旧错误记录
    """
    if file_index not in (0, test_mode, 4, 5):
        print("文件索引错误，有效值为0、4或测试模式对应的单词本！")
        return None
    if test_mode not in (1, 2, 3):
        print("测试模式错误，有效值为1、2或3！")
        return None
    output_megssage = {
        1: "单词到释义测试",
        2: "释义到单词测试",
        3: "释义到默写测试"
    }

    print(f"\n=== {output_megssage[test_mode]}开始 ===")
    # 读取测试词库
    target_file = get_file_name_by_index(file_index)
    words, meanings = read_words(target_file)
    # 备份旧错误记录
    if backup_old_wrong:
        save_old_file(target_file)
    # 进行测试
    conduct_test(words, meanings, test_mode)


if __name__ == '__main__':
    test_words = [f"word_{i}" for i in range(10)]
    test_meanings = [f"meaning_{i}" for i in range(10)]

    conduct_test(test_words, test_meanings, 3)