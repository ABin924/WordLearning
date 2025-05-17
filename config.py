"""
配置文件：用于存储全局变量和路径信息。
"""

from os.path import abspath

config = {
    "base_path": abspath('.'),  # 当前工作目录的绝对路径
    "folder_name": "",  # 存储单词本的文件夹名称
    "words_txt_name": "",  # 新单词本的名称
    "words_temp_txt_name": "", #临时单词本的名称
    "words_ebbinghaus_txt_name": "", #艾宾浩斯单词本的名称
    "wrong_txt_name": "",  # 错题单词本的名称
    "wrong_select_means": "",  # 错题本（词义选择）
    "wrong_select_means_hard": "",  # 错题本（词义选择，困难模式）
    "wrong_select_words": "",  # 错题本（英译汉）
    "wrong_dictation": "",  # 错题本（听写）
    "default_line_length": 50
}
