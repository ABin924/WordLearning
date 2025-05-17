"""
工具函数模块：提供通用的工具函数，包括日志记录、去重、字符串处理等。
"""

import re
from config import config


def scan_and_write_to_log(prompt: str = "") -> str:
    """
    打印提示信息并从用户获取输入，同时将输入内容记录到日志文件中。

    Args:
        prompt (str): 打印的提示信息。

    Returns:
        str: 用户输入的内容。
    """
    # 打印提示信息
    print(prompt, end="")

    # 获取用户输入
    user_input = input()

    # 打开日志文件并追加用户输入内容
    with open("log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(user_input + "\n")

    # 返回用户输入的内容
    return user_input

def set_line_length(input_length):
    if input_length <= 0:
        print("请输入正确的行长度！")
        return None
    config["default_line_length"] = input_length
    print(f"行宽度已设置为{config["default_line_length"]}\n\n")
    return None

def print_pron(input_pron : str) -> str:
    l = input_pron.split('美')
    s = ''
    s += ' '.join(list(l[0]))
    if len(l) == 1:
        return s
    return s + '\n' + '美 ' + ' '.join(list(l[1]))

def print_with_single_line_length(s, line_length:int=-1) -> None:
    if line_length <= 0:
        line_length = config["default_line_length"]

    line_idx:int = 0

    for ch in s:
        if ch == '\n':
            line_idx = 0
            print()
            continue
        elif ord(ch) < 256:
            line_idx += 1
        else:
            line_idx += 2

        if line_idx >= line_length:
            print()
            line_idx = 0
        print(ch, end='')
    print()

def remove_duplicates(input_list: list) -> list:
    """
    去除列表中的重复元素，保留原始顺序。

    Args:
        input_list (list): 输入的列表，可能包含重复元素。

    Returns:
        list: 去重后的列表，保留原始顺序。
    """
    # 初始化一个空列表用于存储去重后的元素
    unique_list = []

    # 遍历输入列表
    for item in input_list:
        # 如果当前元素尚未出现在结果列表中，则添加它
        if item not in unique_list:
            unique_list.append(item)

    # 返回去重后的列表
    return unique_list


def get_file_name_by_index(index: int) -> str:
    """
    根据索引获取对应的文件名。

    Args:
        index (int): 文件索引，用于标识不同的单词本。

    Returns:
        str: 对应的文件名，根据索引返回预定义的文件名。
    """
    # 根据索引返回对应的文件名
    if index == 0:
        return config["words_txt_name"]  # 新单词本
    elif index == 1:
        return config["wrong_select_means"]  # 错题本（词义选择）
    elif index == 999:
        return config["wrong_select_means_hard"]  # 错题本（词义选择，困难模式）
    elif index == 2:
        return config["wrong_select_words"]  # 错题本（英译汉）
    elif index == 3:
        return config["wrong_dictation"]  # 错题本（听写）
    elif index == 4:
        return config["words_temp_txt_name"]
    else:
        return "_wrong_index"  # 如果索引无效，返回空字符串


def filter_meanings(meanings: str) -> str:
    """
    过滤词义字符串，去除不必要的括号内容和空行。

    Args:
        meanings (str): 原始词义字符串，可能包含多余的内容。

    Returns:
        str: 过滤后的词义字符串，去除了不必要的内容。
    """
    # 分割词义字符串，去除空行和以 "#" 开头的注释行
    filtered_meanings = [line for line in meanings.split("\n") if line and not line.startswith("#")]

    # 如果有多行，去掉第一行（通常是多余的标题信息）
    if len(filtered_meanings) > 1:
        filtered_meanings = filtered_meanings[1:]

    filtered_meanings = [mean for mean in filtered_meanings if "人名" not in mean and "【名】" not in mean]
    filtered_meanings = [re.sub(r'\([^)]*[a-zA-Z][^)]*\)', '', mean) for mean in filtered_meanings]
    filtered_meanings = [re.sub(r'（[^）]*[a-zA-Z][^）]*）', '', mean) for mean in filtered_meanings]

    # 将过滤后的词义重新组合为字符串
    cleaned_meanings = "\n".join(filtered_meanings)

    # 返回清理后的词义字符串
    return cleaned_meanings


def print_meanings(meanings: str) -> None:
    """
    按分号逐个输出词义，并记录用户输入。

    Args:
        meanings (str): 词义字符串，可能包含多个词义。
    """
    # 分割词义字符串，去除空行
    lines = [line for line in meanings.split("\n") if line]

    # 进一步分割词义，按 "." 分割
    split_lines = []
    for line in lines:
        split_lines.extend(line.split("."))

    # 去除空元素
    split_lines = [item for item in split_lines if item]

    # 逐个打印词义，并记录用户输入
    for item in split_lines:
        print(item)
        scan_and_write_to_log()  # 记录用户输入


def split_meanings(meanings: str) -> list:
    """
    将词义字符串分割为单独的词义列表。

    Args:
        meanings (str): 原始词义字符串，可能包含多个词义。

    Returns:
        list: 分割后的词义列表，每个元素是一个独立的词义。
    """
    # 调用 filter_meanings 函数清理词义字符串
    cleaned_meanings = filter_meanings(meanings)

    # 分割词义字符串，去除空行
    lines = [line for line in cleaned_meanings.split("\n") if line]

    # 进一步分割词义，按 "." 分割
    split_lines = []
    for line in lines:
        split_lines.extend(line.split("."))

    # 去除空元素和纯字母行（可能是无意义的词性标记）
    split_lines = [item for item in split_lines if item and not re.match(r"^[A-Za-z ]+$", item)]

    # 返回分割后的词义列表
    return split_lines