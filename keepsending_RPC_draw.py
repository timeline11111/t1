import re
import matplotlib.pyplot as plt
from collections import Counter


def read_file(file_path):
    """
    读取文件内容并返回每一行的列表
    :param file_path: 文件路径
    :return: 每行内容的列表
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return lines


def extract_numbers(line):
    """
    从行中提取max和min后面的数字
    :param line: 输入行
    :return: (max_num, min_num) 元组
    """
    max_match = re.search(r'max\s*=\s*(\d+)', line)
    min_match = re.search(r'min\s*=\s*(\d+)', line)

    if max_match and min_match:
        max_num = int(max_match.group(1))
        min_num = int(min_match.group(1))
        return max_num, min_num
    return None, None


def calculate_counts(lines):
    """
    计算每行的count值，并统计每个count出现的次数
    :param lines: 每行内容的列表
    :return: count值的Counter对象
    """
    counts = []
    for line in lines:
        max_num, min_num = extract_numbers(line)
        if max_num is not None and min_num is not None:
            count = max_num - min_num
            counts.append(count)
    return Counter(counts)


def plot_counts(counts):
    """
    绘制count值的统计图
    :param counts: count值的Counter对象
    """
    count_values = list(counts.keys())
    frequencies = list(counts.values())

    # 设置条形图的宽度
    bar_width = 1.0

    plt.bar(count_values, frequencies, width=bar_width)
    plt.xlabel('Interval Length')
    plt.ylabel('Frequency')
    plt.title('Interval Length Frequency Distribution')

    # 设置更细的横轴刻度，并旋转刻度标签
    plt.xticks(range(min(count_values), max(count_values) + 1, 10), rotation=90)
    plt.grid(axis='y')

    plt.tight_layout()  # 调整子图参数以给刻度标签更多空间
    plt.show()


# 示例文件路径
file_path = 'peer_counts.txt'

# 读取文件内容
lines = read_file(file_path)

# 计算count值并统计出现次数
counts = calculate_counts(lines)

# 统计count值小于等于10的IP数量
counts_le_10 = sum(freq for count, freq in counts.items() if count <= 10)
print(f"Count <= 10 的IP数量: {counts_le_10}")

# 绘制统计结果
plot_counts(counts)
