"""
文件操作模块：提供与文件读写相关的功能，包括创建文件、读取和写入单词本等。
"""

from os import listdir, chdir, mkdir
from os.path import join, abspath
from time import time, strftime, localtime, sleep
import re

from config import config
from utils import scan_and_write_to_log, get_file_name_by_index, remove_duplicates


def create_text_file(file_name: str) -> None:
    """
    创建一个空的文本文件，如果文件已存在则不操作。

    Args:
        file_name (str): 要创建的文件名。
    """
    # 获取当前目录下的文件列表
    existing_files = listdir()

    # 如果文件已存在，直接返回
    if file_name in existing_files:
        return
    elif file_name.lower() in [s0.lower() for s0 in existing_files]:
        print("警告：存在大小写冲突，跳过文件的创建")
        return

    # 创建新文件并写入空内容
    with open(file_name, "a", encoding="utf-8") as file:
        file.write("")


def initialize_files() -> None:
    """
    初始化单词本文件夹和文件，根据用户输入创建必要的目录和文件。
    """
    # 切换到基础路径
    chdir(config["base_path"])

    # 用户输入文件夹和文件名称
    config["folder_name"] = scan_and_write_to_log("请输入文件夹名称：").strip()
    config["words_txt_name"] = scan_and_write_to_log("请输入单词本名称：").strip()
    config["wrong_txt_name"] = scan_and_write_to_log("请输入错词本名称：").strip()

    # 生成单词本的派生文件名
    config["words_temp_txt_name"] = f"{config['words_txt_name']}_copy"
    config["words_ebbinghaus_txt_name"] = f"{config['words_txt_name']}_Ebbinghaus"

    # 生成错题本的派生文件名
    config["wrong_select_means"] = f"{config['wrong_txt_name']}_词义"
    config["wrong_select_means_hard"] = f"{config['wrong_txt_name']}_词义（难）"
    config["wrong_select_words"] = f"{config['wrong_txt_name']}_英译汉"
    config["wrong_dictation"] = f"{config['wrong_txt_name']}_听写"

    # 创建文件夹
    try:
        mkdir(join(abspath("."), config["folder_name"]))
    except Exception:
        pass

    # 切换到新创建的文件夹
    chdir(join(abspath("."), config["folder_name"]))

    # 创建单词本文件
    file_names = [
        config["words_txt_name"],
        config["wrong_select_means"],
        config["wrong_select_means_hard"],
        config["wrong_select_words"],
        config["wrong_dictation"],
        config["words_temp_txt_name"],
        config["words_ebbinghaus_txt_name"],
    ]
    for file_name in file_names:
        create_text_file(f"{file_name}.txt")
        create_text_file(f"{file_name}$" ".txt")


def read_words(file_name: str) -> tuple[list, list]:
    """
    从指定的文件中读取单词和词义。

    Args:
        file_name (str): 文件名。

    Returns:
        tuple[list, list]: 单词列表和词义列表。
    """
    # 读取文件内容
    with open(f"{file_name}$.txt", "r", encoding="utf-8") as file:
        content = file.read().split("$")

    # 解析单词和词义
    words = []
    meanings = []
    for i in range(len(content) // 2):
        words.append(content[2 * i].strip())
        meanings.append(content[2 * i + 1])

    # 利用re分别去掉words中元素的开头和结尾的特殊符号
    words = [re.sub(r'^\W+|\W+$', '', word) for word in words]

    return words, meanings


def append_words(file_name: str, words: list, meanings: list) -> None:
    """
    将单词和词义追加到指定的文件中。

    Args:
        file_name (str): 文件名。
        words (list): 单词列表。
        meanings (list): 词义列表。
    """
    # 追加到普通文件
    with open(f"{file_name}.txt", "a", encoding="utf-8") as file:
        for word, meaning in zip(words, meanings):
            file.write(f"{word}：\n{meaning}\n\n")

    # 追加到辅助文件
    with open(f"{file_name}$.txt", "r", encoding="utf-8") as file:
        content = file.read()
    for word, meaning in zip(words, meanings):
        content += f"{word.strip()}${meaning}$"

    with open(f"{file_name}$" ".txt", "w", encoding="utf-8") as file:
        file.write(content)


def save_old_file(file_name: str) -> str:
    """
    将当前文件的内容保存为一个新的备份文件，文件名包含时间戳。

    :args:
        file_name (str): 文件名。
    :returns:
        timestamp: 时间戳
    """
    # 读取当前文件内容
    words, meanings = read_words(file_name)

    # 生成备份文件名
    time_us = (str(time()).split('.'))[1]
    timestamp = f"{strftime('%Y-%m-%d__%H_%M_%S', localtime())}.{time_us}"
    backup_name = f"{file_name}_backed_up_at_{timestamp}"

    # 创建备份文件
    create_text_file(f"{backup_name}.txt")
    create_text_file(f"{backup_name}$" ".txt")

    # 将内容追加到备份文件
    append_words(backup_name, words, meanings)

    sleep(0.001)
    return timestamp

def save_old_file_by_index(file_index:int)->None:
    save_old_file(get_file_name_by_index(file_index))

def write_words(file_name: str, words: list, meanings: list, user_call: bool = True) -> str:
    """
    将单词和词义写入指定的文件中，可以选择是否保存旧文件。

    :args:
        file_name (str): 文件名。
        words (list): 单词列表。
        meanings (list): 词义列表。
        user_call (bool): 是否由用户调用，如果是，则保存旧文件。
    :returns:
        timestamp: 时间戳
    """
    timestamp = ''
    if user_call:
        # 如果由用户调用，先保存旧文件
        timestamp = save_old_file(file_name)

    # 清空普通文件内容
    with open(f"{file_name}.txt", "w", encoding="utf-8") as file:
        file.write("")
    # 清空辅助文件内容
    with open(f"{file_name}$.txt", "w", encoding="utf-8") as file:
        file.write("")

    # 写入新内容
    append_words(file_name, words, meanings)
    return timestamp


def add_word(file_name: str, word: str, meaning: str) -> None:
    """
    将一个单词及其词义添加到指定的文件中。

    Args:
        file_name (str): 文件名。
        word (str): 单词。
        meaning (str): 词义。
    """
    # 追加到普通文件
    with open(f"{file_name}.txt", "a", encoding="utf-8") as file:
        file.write(f"{word}：\n{meaning}\n\n")

    # 追加到辅助文件
    with open(f"{file_name}$" ".txt", "a", encoding="utf-8") as file:
        file.write(f"{word}${meaning}$")


def clear_words(file_name: str) -> None:
    """
    清空指定文件中的所有内容，提示用户确认。

    Args:
        file_name (str): 文件名。
    """
    # 如果由用户调用，提示用户确认
    confirm = scan_and_write_to_log("确认清空？请输入 'I determined'：")
    if confirm != "I determined":
        return
    confirm = scan_and_write_to_log("再次确认？请输入 'I determined again'：")
    if confirm != "I determined again":
        return
    confirm = scan_and_write_to_log("最后确认？请输入 'I finally determined'：")
    if confirm != "I finally determined":
        return
    # 保存旧文件
    save_old_file(file_name)

    # 清空文件内容
    with open(f"{file_name}.txt", "w", encoding="utf-8") as file:
        file.write("")
    with open(f"{file_name}$" ".txt", "w", encoding="utf-8") as file:
        file.write("")


def remove_duplicates_from_file(file_index: int) -> None:
    """
    从指定的文件中移除重复的单词和词义。

    Args:
        file_index (int): 文件索引。
    """
    # 获取文件名
    file_name = get_file_name_by_index(file_index)

    # 读取文件内容
    words, meanings = read_words(file_name)

    # 合并单词和词义为一个列表，用于去重
    combined = [(words[i], meanings[i]) for i in range(len(words))]
    unique_combined = remove_duplicates(combined)

    # 分离去重后的单词和词义
    unique_words = [item[0] for item in unique_combined]
    unique_meanings = [item[1] for item in unique_combined]

    # 生成新的文件名
    new_file_name = f"{file_name}_del_re"

    # 清空新文件内容
    with open(f"{new_file_name}.txt", "w", encoding="utf-8") as file:
        file.write("")
    with open(f"{new_file_name}$.txt", "w", encoding="utf-8") as file:
        file.write("")

    # 将去重后的内容追加到新文件
    append_words(new_file_name, unique_words, unique_meanings)

def get_length_of_words(file_index:int):
    words, _ = read_words(get_file_name_by_index(file_index))
    length = len(words)
    print(length)

    return length