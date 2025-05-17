from file_io import *
from learning import *
from training import *
from utils import set_line_length
from word_adding import *
from os import system

# 定义命令与对应函数及参数格式的映射
COMMAND_MAPPING = {
    "change index": (
        change_index,
        ()
    ),
    "get words": (
        print_words,
        (
            ("file_index", int),
        )
    ),
    "set line length": (
        set_line_length,
        (
            ("input_length", int),
        )
    ),
    "add tran": (
        add_words_from_english,
        ()
    ),
    "add rtran": (
        add_words_from_chinese,
        ()
    ),
    "add tranjy": (
        add_words_from_chinese_synonyms,
        ()
    ),
    "insert": (
        insert_words_from_english,
        (
            ("file_index", int),
        )
    ),
    "save old":(
        save_old_file_by_index,
        (
            ("file_index", int),
        )
    ),
    "delete": (
        delete_words_from_file,
        (
            ("file_index", int),
        )
    ),
    "copy portion": (
        copy_portion_words,
        (
            ("original_file_index", int),
            ("begin_index", int),
            ("end_index", int),
            ("backup_old_temp_words", int),
        )
    ),
    "get length": (
        get_length_of_words,
        (
            ("file_index", int),
        )
    ),
    "learning": (
        learning,
        (
            ("file_index", int),
            ("mode", int),
        )
    ),
    "test words": (
        test_words,
        (
            ("file_index", int),
            ("test_mode", int),
            ("backup_old_wrong", int),
        )
    ),
}

# 教程字符串，用于帮助信息
TUTORIAL_DICT = {
    "change index": "\n **change index**\n   - 功能：切换当前文件索引。\n   - 用法：`change index`\n   - 参数：`file_index`（整数，表示文件索引）\n",
    "get words": "\n **get words**\n   - 功能：获取当前文件中的单词。\n   - 用法：`get words <file_index>`\n   - 参数：`file_index`（整数，表示文件索引）\n",
    "set line length": "\n **set line length**\n   - 功能：设置词义显示的每行宽度。\n   - 用法：`set line length <input_length>`\n   - 参数：`input_length`（整数，表示要设置的宽度）\n",
    "add tran": "\n **add tran**\n   - 功能：从英文添加单词。\n   - 用法：`add tran`\n",
    "add rtran": "\n **add rtran**\n   - 功能：从中文添加单词。\n   - 用法：`add rtran`\n",
    "add tranjy": "\n **add tranjy**\n   - 功能：从中文同义词添加单词。\n   - 用法：`add tranjy`\n",
    "insert": "\n **insert**\n   - 功能：从文件中插入单词。\n   - 用法：`insert <file_index>`\n   - 参数：`file_index`（整数，表示文件索引）\n",
    "save old": "\n **save old**\n   - 功能:备份单词表。\n   -用法:`save old <file_index`\n   - 参数：`file_index`（整数，表示文件索引）\n",
    "delete": "\n **delete**\n   - 功能：从文件中删除单词。\n   - 用法：`delete <file_index>`\n   - 参数：`file_index`（整数，表示文件索引）\n",
    "copy portion": "\n **copy portion**\n   - 功能：复制文件中的一部分单词。\n   - 用法：`copy portion <original_file_index> <begin_index> <end_index> <backup_old_temp_words>`\n   - 参数：\n     - `original_file_index`（整数，表示原始文件索引）\n     - `begin_index`（整数，表示开始索引，1-based）\n     - `end_index`（整数，表示结束索引）\n     - `backup_old_temp_words`（整数，是否备份旧词表）\n",
    "get length": "\n **get length**\n   - 功能：获取文件中单词的数量。\n   - 用法：`get length <file_index>`\n   - 参数：`file_index`（整数，表示文件索引）\n",
    "learning": "\n **learning**\n   - 功能：进入学习模式。\n   - 用法：`learning <file_index> <mode>`\n   - 参数：\n     - `file_index`（整数，表示文件索引）\n     - `mode`（整数，表示学习模式，0表示命令行顺序模式，1表示命令行随机模式，2表示窗体学习模式）\n",
    "test words": "\n **test words**\n   - 功能：进行单词测试。\n   - 用法：`test words <file_index> <test_mode> <backup_old_wrong>`\n   - 参数：\n     - `file_index`（整数，表示文件索引）\n     - `test_mode`（整数，表示测试模式，1表示词义，2表示英译汉，3表示听写）\n     - `backup_old_wrong`（整数，表示是否备份错误单词）\n",
    "help": "\n **help**\n    - 功能：显示本教程。\n    - 用法：`help`\n",
    "commands": "\n **commands**\n    - 功能：查看各命令。\n    - 用法：`commands`\n",
    "cls": "\n **cls**\n    - 功能：清屏。\n    - 用法：`cls`\n",
    "exit": "\n **exit**\n    - 功能：退出程序。\n    - 用法：`exit`\n",
    "advanced": "\n **advanced**\n    - 功能：进入高级模式，允许执行Python语句。\n    - 用法：`advanced`\n    - 退出高级模式：`exit advanced`\n"
}

COMMANDS = [
    "change index",
    "get words",
    "set line length",
    "add tran",
    "add rtran",
    "add tranjy",
    "insert",
    "save old",
    "delete",
    "copy portion",
    "get length",
    "learning",
    "test words",
    "help",
    "commands",
    "cls",
    "exit",
    "advanced"
]

def advanced_mode():
    """高级模式，允许用户输入并执行Python语句"""
    while True:
        command = scan_and_write_to_log("输入python语句：")
        if command == "exit advanced":
            return None
        try:
            exec(command)
        except Exception as e:
            print(e)


def main():
    """主函数，初始化文件并处理用户命令"""
    initialize_files()
    print(f"以下为教程：\n{''.join([TUTORIAL_DICT[command] for command in COMMANDS])}")

    while True:
        print('\n\n')
        command = scan_and_write_to_log(f"{config["folder_name"]} > ")
        if command == "exit":
            return None
        if command == "help":
            print(f"以下为教程：\n{''.join([TUTORIAL_DICT[command] for command in COMMANDS])}")
            continue
        if command == "commands":
            print("\n" + "\n".join(COMMANDS))
            continue
        if command == "cls":
            system("cls")
            continue
        if command == "advanced":
            advanced_mode()
            continue
        if not COMMAND_MAPPING.get(command):
            print("命令错误，输入help查看命令")
            continue

        # 获取命令对应的函数和参数格式
        function, arg_formats = COMMAND_MAPPING[command]

        # 如果命令不需要参数，直接调用函数
        if len(arg_formats) == 0:
            try:
                function()
            except Exception as e:
                print("函数调用出错：", e)
            continue

        # 获取用户输入的参数
        print(f"参数格式：{TUTORIAL_DICT[command]}")
        input_args = scan_and_write_to_log("输入参数：").split(' ')
        num_required_args = len(arg_formats)

        # 检查参数个数是否正确
        if len(input_args) != num_required_args:
            print(f"参数个数错误，需输入{num_required_args}个，你输入了{len(input_args)}个")
            continue

        # 转换参数类型并存储到字典中
        converted_args = {}
        all_args_valid = True
        for i in range(num_required_args):
            arg_name, arg_type = arg_formats[i]
            try:
                converted_args[arg_name] = arg_type(input_args[i])
            except Exception as e:
                all_args_valid = False
                print(f"参数{i + 1}类型错误：", e)
                continue

        # 如果参数类型转换失败，跳过本次循环
        if not all_args_valid:
            continue

        # 调用函数并传入转换后的参数
        try:
            if sys.platform == 'win32':
                system('cls')
            else:
                system('clear')
            print(f"\n\n正在执行命令：{command}\n\n")
            function(**converted_args)
        except Exception as e:
            print("函数调用出错：", e)


if __name__ == '__main__':
    main()