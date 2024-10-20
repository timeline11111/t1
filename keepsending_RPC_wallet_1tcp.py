import requests
import json
import time

def send_rpc_requests(ip):
    headers = {'Content-Type': 'application/json'}

    # 请求数据
    net_peerCount_payload = {
        "jsonrpc": "2.0",
        "method": "net_peerCount",
        "params": [],
        "id": 1
    }

    web3_clientVersion_payload = {
        "jsonrpc": "2.0",
        "method": "web3_clientVersion",
        "params": [],
        "id": 2
    }

    # 创建一个Session对象
    session = requests.Session()

    try:
        # 发送net_peerCount请求
        net_peerCount_response = session.post(ip, headers=headers, data=json.dumps(net_peerCount_payload))
        net_peerCount_result = net_peerCount_response.json()
        print(f"net_peerCount response from {ip}:", net_peerCount_result)

        # 发送web3_clientVersion请求
        web3_clientVersion_response = session.post(ip, headers=headers, data=json.dumps(web3_clientVersion_payload))
        web3_clientVersion_result = web3_clientVersion_response.json()
        print(f"web3_clientVersion response from {ip}:", web3_clientVersion_result)

        # 提取net_peerCount和web3_clientVersion的结果
        if 'result' in net_peerCount_result and 'result' in web3_clientVersion_result:
            net_peerCount = int(net_peerCount_result['result'], 16)  # 转换为整数
            web3_clientVersion = web3_clientVersion_result['result']
            return net_peerCount, web3_clientVersion

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while connecting to {ip}: {e}")

    finally:
        # 关闭Session
        session.close()

    return None, None

def read_ip_list(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def calculate_ranges(counts):
    if not counts:
        return []

    ranges = []
    sorted_counts = sorted(set(counts))
    start = sorted_counts[0]
    end = start

    for count in sorted_counts[1:]:
        if count != end + 1:
            ranges.append((start, end))
            start = count
        end = count
    ranges.append((start, end))

    return ranges

# 主程序
if __name__ == "__main__":
    ip_list_file = 'wallet_ip_list.txt'  # 输入文件，包含IP地址
    duration = 60 * 60  # 总运行时间为10分钟（以秒为单位）
    interval = 1  # 每隔30秒轮询一次

    ip_list = read_ip_list(ip_list_file)
    results = {}  # 存储结果的字典
    traverse_count = {ip: 0 for ip in ip_list}  # 存储遍历次数的字典

    start_time = time.time()  # 记录开始时间

    try:
        while True:
            elapsed_time = time.time() - start_time  # 计算已过去的时间
            if elapsed_time >= duration:  # 如果已过去的时间超过运行总时长，则退出循环
                break

            for ip in ip_list:
                traverse_count[ip] += 1  # 增加遍历次数
                net_peerCount, web3_clientVersion = send_rpc_requests(ip)
                if net_peerCount is not None and web3_clientVersion is not None:
                    if web3_clientVersion not in results:
                        results[web3_clientVersion] = []
                    results[web3_clientVersion].append(net_peerCount)

            time.sleep(interval)  # 等待interval秒后再进行下一次循环

    except KeyboardInterrupt:  # 允许使用Ctrl+C中断程序
        pass

    # 计算每个客户端版本对应的peercount范围
    version_ranges = {version: calculate_ranges(counts) for version, counts in results.items()}

    # 输出统计结果
    print("统计结果:")
    for version, ranges in version_ranges.items():
        range_str = ', '.join([f"{start}-{end}" for start, end in ranges])
        print(f"客户端版本: {version}, Peer Count 范围: {range_str}")

    print("\n遍历次数:")
    for ip, count in traverse_count.items():
        print(f"IP: {ip}, 遍历次数: {count}")
