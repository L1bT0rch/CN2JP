# -*- coding: utf-8 -*-
# 日文文件乱码转换工具(CNtoJP)v0.2.2 by 羊君, edited by L1bT0rch
import os
import sys

# 获取当前工作目录
CWD = os.getcwd()

# 定义日志文件路径
LOG_FILE = os.path.join(CWD, "conversion_log.txt")

def ask_yes_no(prompt):
    """
    显示一个命令行提示，要求用户输入'y'或'n'。
    
    :param prompt: 提示信息
    :return: 用户输入的布尔值
    """
    while True:
        response = input(prompt + " (y/n): ").strip().lower()
        if response == 'y':
            return True
        elif response == 'n':
            return False
        print("无效输入，请输入 'y' 或 'n'.")

def log_message(message):
    """
    将日志信息写入到日志文件中。
    
    :param message: 日志信息
    """
    with open(LOG_FILE, 'a', encoding='utf-8') as log:
        log.write(message + "\n")

def safe_encode(file, encoding):
    """
    尝试使用指定的编码对文件进行编码。
    
    :param file: 文件名
    :param encoding: 编码方式
    :return: 编码后的字节串或None
    """
    try:
        return file.encode(encoding)
    except UnicodeEncodeError:
        return None

def change_code(file):
    """
    修改文件名编码，尝试将文件名从GBK编码转换到Shift-JIS编码。
    
    :param file: 文件名
    :return: 新的文件名或原文件名
    """
    if safe_encode(file, 'gb2312'):
        return None  # 表示不需要修改
    if safe_encode(file, 'Shift-JIS'):
        return None  # 表示不需要修改
    gbk_encoded = safe_encode(file, 'gbk')
    if gbk_encoded:
        try:
            return gbk_encoded.decode('Shift-JIS')
        except (UnicodeDecodeError, UnicodeEncodeError):
            return None
    return None  # 表示无法转换

def rename_files():
    """
    遍历当前目录及子目录中的所有文件和文件夹，尝试重命名文件和文件夹。
    """
    directories = []
    # List to store directories for sorting by depth

    for root, _, files in os.walk(CWD):
        if root != CWD:
            directories.append(root)
        for file in files:
            old_path = os.path.join(root, file)
            new_name = change_code(file)
            if new_name:
                new_path = os.path.join(root, new_name)
                if old_path != new_path:
                    os.rename(old_path, new_path)
                    log_message(f"Renamed: {old_path} -> {new_path}")

    sort_and_rename_directories(directories)
    print('文件/目录名乱码转换成功！')

def sort_and_rename_directories(directories):
    """
    根据目录深度排序并重命名目录。
    
    :param directories: 目录列表
    """
    directories.sort(key=lambda d: d.count('\\'), reverse=True)

    for directory in directories:
        parent, current = os.path.split(directory)
        new_name = change_code(current)
        if new_name:
            new_directory = os.path.join(parent, new_name)
            if directory != new_directory:
                os.rename(directory, new_directory)
                log_message(f"Renamed directory: {directory} -> {new_directory}")

def convert_txt_files():
    """
    查找并转换当前目录及子目录中的所有TXT文件内容编码。
    """
    txt_files = []
    for root, _, files in os.walk(CWD):
        txt_files.extend(os.path.join(root, file) for file in files if file.endswith('.txt'))
    
    if not txt_files:
        return
    
    if ask_yes_no(f'已经检测到{len(txt_files)}个txt文件，是否进行txt内容的转换？'):
        for txt_file in txt_files:
            convert_txt_file(txt_file)
        print('txt文件转换成功！')

def convert_txt_file(file_path):
    """
    转换单个文件的编码，如果转换成功则将原文件重命名为备份文件，并写入新的内容到原文件。
    
    :param file_path: 要转换的文件路径
    """
    try:
        with open(file_path, 'r', encoding='gb2312') as txtfile:
            txtfile.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='Shift-JIS') as txtfile:
                content = txtfile.read()
            # 将原文件重命名为备份文件
            backup_path = file_path + '.bak'
            os.rename(file_path, backup_path)
            log_message(f"Backup created: {file_path} -> {backup_path}")
            # 写入新的内容到原文件
            with open(file_path, 'w', encoding='utf-8') as new_file:
                new_file.write(content)
                log_message(f"Converted and replaced content: {file_path}")
        except UnicodeDecodeError:
            pass

def main():
    """
    主函数，用于执行文件和TXT文件转换操作。
    """

    # 获取并打印当前工作目录
    current_directory = os.getcwd()
    print(f"当前工作目录为: {current_directory}")

    # 确认用户是否希望继续
    if not ask_yes_no('本工具只适用于简体中文系统\n请确认当前工作目录是否是[需要转换的文件夹]\n请务必在运行本工具前备份您的原始文件！\n是否继续？'):
        sys.exit()
    else:
        if os.path.exists(LOG_FILE):
            os.remove(LOG_FILE)  # 如果日志文件已经存在，删除重新创建
        rename_files()
        convert_txt_files()
        print('转换程序运行完毕，感谢您的使用。转换日志已保存为conversion_log.txt')

if __name__ == '__main__':
    main()
