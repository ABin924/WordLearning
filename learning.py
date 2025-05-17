"""
学习模块：提供单词学习功能，支持控制台学习和图形界面学习。
"""
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.shortcuts import clear
import sys
import os
import random
import time

from config import config
from utils import *
from file_io import read_words, write_words


def console_learning(file_index: int, cycle_random_mode: bool=False) -> None:
    file_name = get_file_name_by_index(file_index)
    words, meanings = read_words(file_name)
    
    if len(words) != len(meanings):
        print("错误: 单词列表和词义列表长度不匹配!")
        return None
    if len(words) == 0:
        print("错误:无单词!")
        return None

    print("操作: j-下一个, k-上一个, n+j/k-跳转n个, r-刷新, h-获取帮助, q-退出, 随机模式下, j为随机单词")
    input("按回车键继续...")

    current_idx = 0
    line_length = config["default_line_length"]
    total_words = len(words)
    input_buffer = ""
    kb = KeyBindings()

    random_indexes = [i for i in range(total_words)] * 3
    total_random_words = total_words * 3
    random.shuffle(random_indexes)
    current_idx_of_random_list = 0
    if cycle_random_mode:
        current_idx = random_indexes[0]

    @kb.add("j")
    def _(event):
        nonlocal state
        state = "word"
        try:
            if cycle_random_mode:
                nonlocal random_indexes, current_idx_of_random_list
                current_idx_of_random_list += 1
                if current_idx_of_random_list >= total_random_words:
                    random.shuffle(random_indexes)
                    current_idx_of_random_list = 0
                new_idx = random_indexes[current_idx_of_random_list]
            else:
                nonlocal current_idx, input_buffer
                n = int(input_buffer) if input_buffer else 1
                new_idx = current_idx + n
                if new_idx >= total_words:
                    new_idx = total_words - 1
                    state = "over_next"
            current_idx = new_idx
        except ValueError:
            state = "unknown"
        input_buffer = ""
        event.app.exit(result=False)

    @kb.add("k")
    def _(event):
        nonlocal state
        state = "word"
        nonlocal current_idx, input_buffer
        try:
            if cycle_random_mode:
                nonlocal random_indexes, current_idx_of_random_list
                current_idx_of_random_list -= 1
                if current_idx_of_random_list < 0:
                    current_idx_of_random_list = 0
                new_idx = random_indexes[current_idx_of_random_list]
            else:
                n = int(input_buffer) if input_buffer else 1
                new_idx = current_idx - n
                if new_idx < 0:
                    new_idx = 0
                    state = "over_last"
            current_idx = new_idx
        except ValueError:
            state = "unknown"
        input_buffer = ""
        event.app.exit(result=False)

    @kb.add("q")
    def _(event):
        event.app.exit(result=True)

    @kb.add("r")
    def _(event):
        nonlocal state, input_buffer
        state = "word"
        input_buffer = ""
        event.app.exit(result=False)

    @kb.add("h")
    def _(event):
        nonlocal state
        state = "help"
        os.system("cls" if sys.platform == 'win32' else "clear")
        event.app.exit(result=False)

    @kb.add(Keys.Any)
    def _(event):
        nonlocal input_buffer
        if event.key_sequence[0].key.isdigit():
            input_buffer += event.key_sequence[0].key
            print(f"\n输入数字: {input_buffer}")

    @kb.add("a")
    def _(event):
        nonlocal line_length
        line_length += 1
        event.app.exit(result=False)

    @kb.add("s")
    def _(event):
        nonlocal line_length
        line_length -= 1
        if line_length < 1:
            line_length = 1
        event.app.exit(result=False)


    session = PromptSession(key_bindings=kb)
    state = 'word'

    with patch_stdout():
        while True:
            time.sleep(0.04)
            os.system("cls" if sys.platform == 'win32' else "clear")
            clear()
            if state == "help":
                print(f"{current_idx + 1}/{total_words}    w")
                if cycle_random_mode:
                    print(f"{current_idx_of_random_list + 1}/{total_random_words}    r")
                print(f"行长度 : {line_length}")
                print('\n')
                print(
                    "操作: \n***  j-下一个, k-上一个, n+j/k-跳转n个, \n***  a-增加行长度, s-减小行长度, \n***  h-获取帮助, q-退出, r-刷新并显示当前单词, \n***  随机模式下, j为随机单词, k为上一个随机单词")
                print("按r键刷新...")
            elif state == "over_last":
                print("已是第一个单词")
                print("按r键刷新...")
            elif state == "over_next":
                print("已是最后一个单词")
                print("按r键刷新...")
            elif state == "unknown":
                print("出现未知错误...")
                print("按r键刷新...")
            else:
                print(f"单词: {words[current_idx]}")
                print('\n')
                l = meanings[current_idx].split('\n')
                print(print_pron(l[0]))
                print('\n')
                s = "词义: \n" + '\n'.join(l[1:])
                print_with_single_line_length(s, line_length)

            if session.prompt("", is_password=False):
                return None


def form_learning(file_index: int) -> None:
    """
    图形界面学习模式：通过外部程序显示单词和词义。

    Args:
        file_index (int): 文件索引，指定学习的单词本。
    """
    file_name = get_file_name_by_index(file_index)
    words, meanings = read_words(file_name)
    
    if not words or not meanings:
        print("单词本为空！")
        return

    # 准备数据文件路径
    data_file_path = os.path.join(config["base_path"], config["folder_name"], f"{file_name}$.txt")

    #目前在单词本目录，先返回上级目录
    os.chdir(config["base_path"])
    #窗体程序路径
    exe_file_path = os.path.join("net8.0-windows_WordShow", "单词显示.exe")

    # 调用外部程序进行学习
    try:
        print(f"{exe_file_path} {data_file_path}")
        os.system(f"{exe_file_path} {data_file_path}")
    except Exception as e:
        print(f"启动学习程序时出错：{e}")

    #重新回到单词本文件夹
    os.chdir(os.path.join(config["base_path"], config["folder_name"]))
    # 重新读取窗体程序修改后的单词本，并重新保存单词本，确保数据一致性
    words, meanings = read_words(file_name)
    write_words(file_name, words, meanings, False)


def learning(file_index: int, mode: int = 0) -> None:
    """
    学习功能入口：根据模式选择学习方式。

    Args:
        file_index (int): 文件索引，指定学习的单词本。
        mode (int): 学习模式（0: 控制台普通模式，1: 控制台困难模式，2: 图形界面模式）。
    """
    if mode == 0:
        console_learning(file_index)
    elif mode == 1:
        console_learning(file_index, cycle_random_mode=True)
    elif mode == 2:
        if sys.platform == 'win32':
            form_learning(file_index)
        else:
            print("窗口模式仅支持Windows系统。")
    else:
        print("无效的学习模式，请选择 0、1 或 2。")
