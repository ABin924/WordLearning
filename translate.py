"""
翻译模块：提供与翻译相关的功能，包括单词和短语的翻译查询。
"""

import requests
from bs4 import BeautifulSoup
from time import sleep
import re

from utils import remove_duplicates

headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Host": "httpbin.org",
        "Referer": "https://link.zhihu.com/?target=https%3A//httpbin.org/headers",
        "Sec-Ch-Ua": "\"Chromium\";v=\"122\", \"Not(A:Brand\";v=\"24\", \"Microsoft Edge\";v=\"122\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "\"Windows\"",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
        "X-Amzn-Trace-Id": "Root=1-66018ce8-055841b966fc9e9c2e084edc"
}


def get_translation(word: str) -> str:
    """
    查询单词的翻译信息。

    Args:
        word (str): 需要查询的单词。

    Returns:
        str: 单词的翻译结果，包括音标和词义。
    """
    # 构造翻译查询的 URL
    url = f"https://dict.youdao.com/result?word={word}&lang=en"

    # 发起 HTTP 请求获取网页内容
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # 初始化翻译结果字符串
    translation_result = ""

    # 尝试获取音标信息
    try:
        phonetics = soup.find_all("div", attrs={"class": "phone_con"})
        for phonetic in phonetics:
            translation_result += phonetic.get_text() + "\n"
    except Exception as e:
        # 如果获取音标失败，记录错误并继续
        translation_result += "?\n"
        print(f"获取音标时出错：{e}")

    # 如果音标信息为空，添加占位符
    if not translation_result.strip():
        translation_result += "?\n"

    # 尝试获取词义信息
    try:
        meanings = soup.find_all("li", attrs={"class": "word-exp"})
        for meaning in meanings:
            translation_result += meaning.get_text() + "\n"
    except Exception as e:
        # 如果获取词义失败，记录错误并继续
        translation_result += "?\n"
        print(f"获取词义时出错：{e}")

    # 休眠 1 秒，避免频繁请求导致的 IP 封禁
    sleep(1)

    # 返回翻译结果
    return translation_result


def reverse_translate(chinese: str) -> list:
    """
    查询汉语对应的英文单词。

    Args:
        chinese (str): 需要查询的汉语。

    Returns:
        list: 对应的英文单词列表。
    """
    # 构造翻译查询的 URL
    url = f"https://dict.youdao.com/result?word={chinese}&lang=en"

    # 发起 HTTP 请求获取网页内容
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # 初始化结果列表
    english_words = []

    # 尝试获取所有可能的英文单词
    try:
        links = soup.find_all("a", attrs={"class": "point"})
        for link in links:
            text = link.get_text()
            # 使用正则表达式过滤非字母字符
            if re.fullmatch(r"[0-9a-zA-Z- ]+", text):
                english_words.append(text.lower())
    except Exception as e:
        # 如果获取失败，记录错误
        print(f"获取英文单词时出错：{e}")

    # 返回去重后的单词列表
    return remove_duplicates(english_words)


def translate_with_synonyms(chinese: str) -> list:
    """
    查询汉语词语的近义词，并为每个近义词查询对应的英文翻译。

    Args:
        chinese (str): 需要查询的汉语词语。

    Returns:
        list: 所有近义词对应的英文单词列表。
    """
    # 构造查询近义词的 URL
    url = f"https://hanyu.baidu.com/s?wd={chinese}&ptype=zici"

    # 发起 HTTP 请求获取网页内容
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # 初始化结果列表
    all_english_words = []

    # 尝试获取近义词列表
    try:
        blocks = soup.find_all("div", attrs={"class": "block"})
        synonyms = blocks[0].get_text().split("\n")[1:-1]  # 提取近义词部分
        for synonym in synonyms:
            # 对每个近义词查询对应的英文翻译
            english_words = reverse_translate(synonym)
            all_english_words.extend(english_words)
            sleep(1)  # 休眠 1 秒，避免频繁请求
    except Exception as e:
        # 如果获取失败，记录错误
        print(f"获取近义词或翻译时出错：{e}")

    # 返回去重后的单词列表
    return remove_duplicates(all_english_words)