import requests
import time
import matplotlib.pyplot as plt

# 读取IP地址列表
def read_ip_list(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]

# 发送eth_peerCount请求并获取结果
def get_peer_count(ip):
    url = f"{ip}"
    headers = {'Content-Type': 'application/json'}
    payload = '{"jsonrpc":"2.0","method":"net_peerCount","params":[],"id":1}'
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        response.raise_for_status()
        result = response.json()

        # 提取并转换peer count
        if 'result' in result and isinstance(result['result'], str):
            peer_count_hex = result['result']
            peer_count = int(peer_count_hex, 16)
            print(f"IP: {ip}, PeerCount: {peer_count}")  # 输出IP和peerCount
            return peer_count
        else:
            print(f"Invalid response from {ip}: {result}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to {ip}: {e}")
        return None

# 计算波动区间
def calculate_ranges(counts):
    if not counts:
        return []

    ranges = []
    start = counts[0]
    end = start

    for i in range(1, len(counts)):
        if counts[i] != end + 1:
            ranges.append((start, end))
            start = counts[i]
        end = counts[i]
    ranges.append((start, end))

    return ranges

# 主程序
if __name__ == "__main__":
    ip_list_file = 'wallet_ip_list.txt'  # 输入文件，包含IP地址
    output_file = 'wallet_peer_counts.txt'  # 输出文件，记录peerCount波动范围
    interval = 1  # 每隔10秒轮询一次
    duration = 96 * 3600  # 总运行时间为20分钟（以秒为单位）

    ip_list = read_ip_list(ip_list_file)
    peer_counts = {ip: [] for ip in ip_list}
    start_time = time.time()  # 记录开始时间

    try:
        while True:
            elapsed_time = time.time() - start_time  # 计算已过去的时间
            if elapsed_time >= duration:  # 如果已过去的时间超过运行总时长，则退出循环
                break

            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            for ip in ip_list:
                peer_count = get_peer_count(ip)
                if peer_count is not None:
                    peer_counts[ip].append((timestamp, peer_count))

                    # 将每次查询结果追加写入文件
                    with open(output_file, 'a') as file:
                        file.write(f"{timestamp} {ip} {peer_count}\n")

            time.sleep(interval)  # 等待interval秒后再进行下一次循环

    except KeyboardInterrupt:  # 允许使用Ctrl+C中断程序
        pass

    print("脚本结束，结果已保存到", output_file)

    # 计算并输出每个IP的peer count波动范围
    ranges_output_file = 'wallet_peer_counts_ranges.txt'
    with open(ranges_output_file, 'w') as file:
        for ip, data in peer_counts.items():
            if data:
                counts = [d[1] for d in data]
                ranges = calculate_ranges(sorted(set(counts)))
                range_str = ', '.join([f"{start}-{end}" for start, end in ranges])
                file.write(f"{ip}: {range_str}\n")
                print(f"{ip}: {range_str}")

    # 绘制折线图
    plt.figure(figsize=(14, 7))
    for ip, data in peer_counts.items():
        if data:
            times, counts = zip(*[(d[0], d[1]) for d in data])
            plt.plot(times, counts, label=ip)

    plt.xlabel('Time')
    plt.ylabel('Peer Count')
    plt.title('Peer Count Varies over Time')
    plt.legend()
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig('peer_count_plot.png')
    plt.show()
