
import struct
import socket
import select
import time
import sys


# https://datatracker.ietf.org/doc/html/rfc1071#section-4.1
def cal_checksum(data):
    n = len(data)
    m = n % 2
    # 1 将校验和字段置为0。
    sum = 0
    for i in range(0, n - m, 2):
        # 2 先转由大端 转 小端序，
        # 然后 将每两个字节（16位）相加（二进制求和）直到最后得出结果，若出现最后还剩一个字节继续与前面结果相加。
        sum += data[i] | data[i + 1] << 8
    # 奇数时将
    if m:
        sum += data[-1]

    while sum >> 16:
        sum = (sum >> 16) + (sum & 0xffff)

    checksum = ~sum & 0xffff
    # ok 1
    # checksum = ((checksum & 0x00ff) << 8) | ((checksum & 0xff00) >> 8)

    # ok 2
    checksum = (checksum >> 8 | (checksum & 0x00ff) << 8)
    return checksum


def echo_request_pack(sequence_number):
    type, code, checksum, id = 8, 0, 0, 0
    data = b'aaaaaaaabbbbbbbbccccccccdddddddd'  # 32s
    icmp_packet = struct.pack('>BBHHH32s', type, code, checksum, id, sequence_number, data)
    checksum = cal_checksum(icmp_packet)
    icmp_packet = struct.pack('>BBHHH32s', type, code, checksum, id, sequence_number, data)
    return icmp_packet


def echo_reply_unpack(received_packet):
    ttl = received_packet[8]
    icmp_header = received_packet[20:28]
    type, code, check_sum, id, sequence_number = struct.unpack(">BBHHH", icmp_header)
    return type, ttl, sequence_number


def send_echo(sequence_number, dst_addr):
    request_packet = echo_request_pack(sequence_number)
    raw_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
    raw_socket.sendto(request_packet, (dst_addr, 80))
    return raw_socket


def wait_echo(expected_number, socket: socket.socket, timeout=2):
    while True:
        what_ready = select.select([socket], [], [], timeout)
        if what_ready[0] == []:
            return 0, -1
        received_packet, addr = socket.recvfrom(1024)
        type, ttl, sequence_number = echo_reply_unpack(received_packet)
        if type == 0 and expected_number == sequence_number:
            return 1, ttl


rtt_list = []


def rtt_summary():
    if len(rtt_list) == 0:
        return -1, -1, -1
    return int(min(rtt_list) * 1000), int(max(rtt_list) * 1000), int(1000 * (sum(rtt_list) / len(rtt_list)))


def ping(host):
    send, accept, lost = 0, 0, 0
    shortest_time, longest_time, avg_time = -1, -1, -1
    dst_addr = socket.gethostbyname(host)
    print("正在 Ping {0} [{1}] 具有 32 字节的数据:".format(host, dst_addr))
    for i in range(0, 4):
        send_time = time.time()
        send_socket = send_echo(i, dst_addr)
        result, ttl = wait_echo(i, send_socket, 2)
        send += 1
        if result:
            accept += 1
            rtt_time = time.time() - send_time
            rtt_list.append(rtt_time)
            print("来自 {0} 的回复: 字节=32 时间={1}ms TTL={2}".format(dst_addr, int(rtt_time * 1000), ttl))
        else:
            lost += 1
            print("请求超时。")
        time.sleep(1)
    print("{0} 的 Ping 统计信息:".format(dst_addr))
    print("\t数据包: 已发送 = {0}, 接收 = {1}, 丢失 = {2} ({3}% 丢失), ".format(send, accept, lost, (lost / send) * 100))

    if accept >= 1:
        print("往返行程的估计时间(以毫秒为单位):")
        shortest_time, longest_time, avg_time = rtt_summary()
        print("\t最短 = {0}ms, 最长 = {1}ms, 平均 = {2}ms".format(shortest_time, longest_time, avg_time))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit('用法: ping.py <host>')
    ping(sys.argv[1])
