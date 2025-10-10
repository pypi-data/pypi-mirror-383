import os
import difflib
import sys
from colorama import Fore, init

# 初始化colorama，支持跨平台的终端颜色输出
init(autoreset=True)

def is_binary_file(file_path):
    """判断文件是否为二进制文件"""
    # 读取文件的前1024字节来检测是否包含空字节
    with open(file_path, 'rb') as f:
        chunk = f.read(1024)
        return b'\x00' in chunk  # 二进制文件通常包含空字节

def get_file_list(root_dir):
    """获取目录下所有文件的相对路径列表"""
    file_list = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            # 获取相对路径
            rel_path = os.path.relpath(os.path.join(dirpath, filename), root_dir)
            file_list.append(rel_path)
    return sorted(file_list)

def read_file(file_path):
    """读取文件内容，返回行列表"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.readlines()
    except UnicodeDecodeError:
        # 尝试其他编码
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.readlines()
        except Exception as e:
            print(f"{Fore.RED}错误：无法读取文件 {file_path} - {str(e)}", file=sys.stderr)
            return None
    except Exception as e:
        print(f"{Fore.RED}错误：读取文件 {file_path} 时出错 - {str(e)}", file=sys.stderr)
        return None

def compare_files(file1, file2):
    """比较两个文件的内容，返回差异结果"""
    # 检查是否为二进制文件
    if is_binary_file(file1) or is_binary_file(file2):
        return "binary"  # 标记为二进制文件
    
    lines1 = read_file(file1)
    lines2 = read_file(file2)
    
    if lines1 is None or lines2 is None:
        return None
    
    # 如果内容相同，返回None
    if lines1 == lines2:
        return None
    
    # 使用difflib生成差异
    diff = difflib.unified_diff(
        lines1, lines2,
        fromfile=file1,
        tofile=file2,
        lineterm=''
    )
    
    return '\n'.join(diff)

def compare_directories(dir1, dir2):
    """递归对比两个目录中的文件"""
    # 确保目录存在
    if not os.path.isdir(dir1):
        print(f"{Fore.RED}错误：目录 {dir1} 不存在", file=sys.stderr)
        return
    if not os.path.isdir(dir2):
        print(f"{Fore.RED}错误：目录 {dir2} 不存在", file=sys.stderr)
        return
    
    # 获取两个目录中的所有文件相对路径
    files1 = get_file_list(dir1)
    files2 = get_file_list(dir2)
    
    # 找到共同的文件（相同相对路径和文件名）
    common_files = set(files1) & set(files2)
    
    # 比较共同文件
    for rel_path in sorted(common_files):
        file1 = os.path.join(dir1, rel_path)
        file2 = os.path.join(dir2, rel_path)
        
        print(f"比较文件: {rel_path}")
        diff_result = compare_files(file1, file2)
        
        if diff_result == "binary":
            print(f"{Fore.CYAN}跳过二进制文件")
        elif diff_result:
            print(f"{Fore.RED}发现差异:")
            print(diff_result)
        else:
            print(f"{Fore.GREEN}内容相同")
        print("-" * 80)
    
    # 报告只在第一个目录中存在的文件（黄色标注）
    only_in_dir1 = set(files1) - set(files2)
    if only_in_dir1:
        print(f"\n{Fore.YELLOW}只在 {dir1} 中存在的文件:")
        for rel_path in sorted(only_in_dir1):
            print(f"  {rel_path}")
    
    # 报告只在第二个目录中存在的文件（黄色标注）
    only_in_dir2 = set(files2) - set(files1)
    if only_in_dir2:
        print(f"\n{Fore.YELLOW}只在 {dir2} 中存在的文件:")
        for rel_path in sorted(only_in_dir2):
            print(f"  {rel_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"{Fore.RED}用法: python dir_diff.py <目录1> <目录2>")
        sys.exit(1)
    
    dir1 = sys.argv[1]
    dir2 = sys.argv[2]
    
    compare_directories(dir1, dir2)
    