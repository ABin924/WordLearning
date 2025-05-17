"""
单词添加模块：提供添加单词和汉语翻译的功能，支持从汉语反向查询英文单词。
实现功能包含：
1. 从英文添加单词及翻译
2. 从汉语反向查询添加英文单词
3. 支持近义词扩展查询
4. 单词本管理功能（删除、复制等）
"""
from config import config
from translate import get_translation, reverse_translate, translate_with_synonyms
from file_io import append_words, get_file_name_by_index, read_words, write_words, save_old_file
from utils import scan_and_write_to_log

# 当前选择的单词本索引（使用列表实现可变对象的引用传递）
now_index = [0]

def change_index():
    """
    修改当前操作的单词本索引（0-4）

    处理流程：
    1. 接收用户输入的数字
    2. 验证是否为0-4的整数
    3. 更新全局索引值
    """
    try:
        # 获取带日志记录的输入
        index_after_change = scan_and_write_to_log("请输入改变后的单词文件序号：")
        index_after_change = int(index_after_change)
        # 范围有效性检查
        if not 0 <= index_after_change <= 4:
            print("请输入0-4之间的数字！")
            return None
    except ValueError:
        print("请输入一个数字！")
        return None

    # 修改全局索引值（通过列表实现引用传递）
    now_index[0] = index_after_change

def print_words(file_index: int) -> None:
    """
    打印指定索引的单词本中的所有单词及其翻译
    :param file_index: 单词本索引（0-4）
    """
    # 读取指定索引的单词本文件
    words, _ = read_words(get_file_name_by_index(file_index))
    # 打印每个单词
    for i in range(len(words)):
        print(f"{i+1} : {words[i]}")

def add_words_from_english() -> None:
    """
    从英文单词添加翻译到单词本

    处理流程：
    1. 循环接收用户输入的英文单词
    2. 支持撤销操作（r_cz指令）
    3. 调用翻译API获取中文释义
    4. 批量追加到指定单词本文件
    """
    print("请输入单词（输入 'add()' 结束，输入 'r_cz' 撤销上一个单词）：")
    words = []  # 存储待添加的英文单词
    meanings = []  # 存储对应的中文翻译

    while True:
        # 获取标准化输入的单词（去除首尾空格并转小写）
        word = scan_and_write_to_log("单词：").strip().lower()

        # 处理特殊指令
        if word == "add()":  # 结束输入指令
            break
        elif word == "r_cz":  # 撤销指令
            if words:
                print(f"已撤销上一个单词：{words.pop()}")
                meanings.pop()
            else:
                print("没有可撤销的单词。")
            continue  # 跳过后续处理

        # 调用翻译函数获取中文释义
        meaning = get_translation(word)

        # 显示并存储有效结果
        print(f"翻译：{meaning}")
        words.append(word)
        meanings.append(meaning)

    # 批量追加到当前选中的单词本文件
    append_words(get_file_name_by_index(now_index[0]), words, meanings)

def add_words_from_chinese() -> None:
    """
    从汉语反向查询添加英文单词到单词本

    处理流程：
    1. 接收用户输入的汉语词汇
    2. 调用反向翻译获取对应英文单词
    3. 去重后获取所有单词的翻译
    4. 批量保存到单词本
    """
    print("请输入汉语（输入 'add()' 结束，输入 'r_cz' 撤销上一个汉语）：")
    chinese_list = []  # 存储输入的汉语词汇
    words = []  # 收集到的英文单词
    meanings = []  # 对应的中文释义

    while True:
        # 获取标准化输入的汉语（去除首尾空格）
        chinese = scan_and_write_to_log("汉语：").strip()

        # 处理特殊指令
        if chinese == "add()":  # 结束指令
            break
        elif chinese == "r_cz":  # 撤销指令
            if chinese_list:
                chinese_list.pop()
                print("已撤销上一个汉语。")
            continue

        # 调用反向翻译接口获取英文单词
        english_words = reverse_translate(chinese)
        if not english_words:  # 无结果处理
            print(f"未找到汉语 '{chinese}' 对应的英文单词。")
            continue

        # 显示并存储结果
        print(f"对应的英文单词：{', '.join(english_words)}")
        chinese_list.append(chinese)
        words.extend(english_words)  # 扩展单词列表

    # 去重处理（集合保持顺序的转换方式）
    unique_words = list(set(words))
    # 获取每个单词的标准翻译
    for word in unique_words:
        meaning = get_translation(word)
        if meaning.strip() == "?":  # 翻译失败处理
            print(f"未找到单词 '{word}' 的翻译。")
            continue
        meanings.append(meaning)

    # 批量保存到当前单词本
    append_words(get_file_name_by_index(now_index[0]), unique_words, meanings)

def add_words_from_chinese_synonyms() -> None:
    """
    从汉语及其近义词添加英文单词到单词本

    处理流程：
    1. 接收用户输入的汉语
    2. 查询包含近义词的英文翻译
    3. 去重后获取所有单词的翻译
    4. 批量保存到单词本

    与add_words_from_chinese的区别：
    使用translate_with_synonyms函数获取包含近义词的翻译结果
    """
    print("请输入汉语（输入 'add()' 结束，输入 'r_cz' 撤销上一个汉语）：")
    chinese_list = []  # 存储输入的汉语
    words = []  # 收集的英文单词（含近义词）
    meanings = []  # 对应的中文释义

    while True:
        # 获取标准化输入的汉语
        chinese = scan_and_write_to_log("汉语：").strip()

        # 处理特殊指令
        if chinese == "add()":  # 结束指令
            break
        elif chinese == "r_cz":  # 撤销指令
            if chinese_list:
                chinese_list.pop()
                print("已撤销上一个汉语。")
            continue

        # 调用带近义词的翻译函数
        english_words = translate_with_synonyms(chinese)
        if not english_words:  # 无结果处理
            print(f"未找到汉语 '{chinese}' 对应的英文单词。")
            continue

        # 显示并存储结果
        print(f"对应的英文单词：{', '.join(english_words)}")
        chinese_list.append(chinese)
        words.extend(english_words)

    # 去重处理
    unique_words = list(set(words))
    # 获取每个单词的翻译
    for word in unique_words:
        meaning = get_translation(word)
        if meaning.strip() == "?":
            print(f"未找到单词 '{word}' 的翻译。")
            continue
        meanings.append(meaning)

    # 批量保存到当前单词本
    append_words(get_file_name_by_index(now_index[0]), unique_words, meanings)

def insert_words_from_english(file_index: int) -> None:
    """
    从英文单词添加翻译到单词本
    处理流程：
    1. 循环接收用户输入的英文单词
    2. 支持撤销操作（r_cz指令）
    3. 调用翻译API获取中文释义
    4. 批量追加到指定单词本文件
    """

    words, meanings = read_words(get_file_name_by_index(file_index))
    input_indexes = [] # 存储待添加的各英文单词的位置
    while True:
        for i in range(len(words)):
            print(f"单词{i+1}：{words[i]}")
        print("请输入序号和单词，单词会插入到输入的序号的后面，0表示最前面。（输入 'add()' 结束，输入 'r_cz' 撤销上一个单词）：")
        # 获取标准化输入的单词（去除首尾空格并转小写）
        user_input_str = scan_and_write_to_log("输入序号和单词，以空格分隔：")
        if user_input_str == "add()":  # 结束指令
            break
        elif user_input_str == "r_cz":  # 撤销指令
            if input_indexes:
                print(f"已撤销上一个插入的单词：{words.pop(input_indexes[-1])}")
                meanings.pop(input_indexes[-1])
                input_indexes.pop()
            continue
        user_input = user_input_str.split(' ') # 分割输入
        word = ' '.join(user_input[1:]).strip().lower() # 以第二个之后的为单词或短语
        index = user_input[0].strip() # 第一个为序号
        try:
            index = int(index)
            if index < 0 or index > len(words):
                print("\n\n请输入0-单词表长度之间的数字！")
                input("按回车继续...")
                print('\n\n\n')
                continue
        except ValueError:
            input_forward_word = index
            if input_forward_word in words:
                index = words.index(input_forward_word) + 1
            else:
                print("\n\n请输入一个数字或已存在的单词！")
                input("按回车继续...")
                print('\n\n\n')
                continue
        # 调用翻译函数获取中文释义
        meaning = get_translation(word)
        # 显示并存储有效结果
        print(f"\n\n插入的单词：{word}\n翻译：{meaning}\n\n")
        input("按回车继续...")
        print('\n\n\n')
        words.insert(index, word)
        meanings.insert(index, meaning)
        input_indexes.append(index)
    write_words(get_file_name_by_index(file_index), words, meanings, False)

def delete_words_from_file(file_index: int) -> None:
    """
    从指定单词本中删除单词

    Args:
        file_index (int): 单词本索引（0-4对应不同文件）

    处理流程：
    1. 读取指定单词本内容
    2. 显示当前所有单词及编号
    3. 接收用户输入的删除序号
    4. 过滤保留的单词并保存文件
    """
    # 根据索引获取文件名
    file_name = get_file_name_by_index(file_index)
    # 读取现有数据
    words, meanings = read_words(file_name)

    if not words or not meanings:  # 空文件处理
        print("单词本为空！")
        return

    # 显示当前内容（带1-based编号）
    print("\n当前单词本内容：")
    for i, (word, meaning) in enumerate(zip(words, meanings), start=1):
        print(f"单词{i}：{word}")

    indices_to_delete = []  # 待删除的索引（0-based）
    while True:
        user_input = scan_and_write_to_log("请输入要删除的单词序号（输入 'delete()' 结束）：")

        if user_input == "delete()":  # 结束指令
            break

        # 输入有效性检查
        if not user_input.isdigit() or int(user_input) < 1 or int(user_input) > len(words):
            print("无效输入，请输入1-单词表长度之间的序号！")
            continue

        # 转换为0-based索引并记录
        indices_to_delete.append(int(user_input) - 1)

    # 列表推导式过滤保留项
    words = [word for i, word in enumerate(words) if i not in indices_to_delete]
    meanings = [meaning for i, meaning in enumerate(meanings) if i not in indices_to_delete]

    # 覆盖写入文件（False表示不备份）
    write_words(file_name, words, meanings, False)
    print("单词删除成功！")

def copy_portion_words(original_file_index: int,
                       begin_index: int, end_index:int,
                       backup_old_temp_words: bool) -> str:
    """
    复制指定范围的单词到临时文件

    Args:
        original_file_index (int): 源文件索引
        begin_index (int): 起始位置（1-based）
        end_index (int): 结束位置（包含）
        backup_old_temp_words (bool): 是否备份旧数据

    Returns:
        str: 临时文件的时间戳

    处理流程：
    1. 读取源文件内容
    2. 切片获取指定范围的单词
    3. 写入临时文件（覆盖模式）
    """
    if backup_old_temp_words:
        save_old_file(get_file_name_by_index(original_file_index))
    # 读取源文件数据
    words, meanings = read_words(get_file_name_by_index(original_file_index))
    # 列表切片（begin_index-1转换为0-based，end_index不包含所以不需要-1）
    words = words[begin_index-1:end_index]
    meanings = meanings[begin_index-1:end_index]
    # 写入临时文件并返回时间戳（config["words_temp_txt_name"]为配置的临时文件名）
    return write_words(
        config["words_temp_txt_name"], words, meanings, False)  # True表示备份