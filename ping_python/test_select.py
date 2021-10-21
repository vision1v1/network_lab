import socket
import struct
import select

# 检验和 需要加强
def get_chesksum(data):
    n = len(data)
    m = n % 2
    sum = 0
    for i in range(0, n - m, 2):
        # 传入data以每两个字节（十六进制）通过ord转十进制，第一字节在低位，第二个字节在高位
        sum += (data[i]) + ((data[i+1]) << 8)
        sum = (sum >> 16) + (sum & 0xffff)
    if m:
        sum += (data[-1])
        sum = (sum >> 16) + (sum & 0xffff)

    # 取反
    answer = ~sum & 0xffff
    #  主机字节序转网络字节序列
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer


type = 8
code = 0
checksum = 0
identifier = 0
sequence_number = 1
data = b'aaaaaaaabbbbbbbbccccccccdddddddd'  # 32s


icmp_packet = struct.pack('>BBHHH32s', type, code,
                          checksum, identifier, sequence_number, data)
icmp_checksum = get_chesksum(icmp_packet)
icmp_packet = struct.pack('>BBHHH32s', type, code,
                          icmp_checksum, identifier, sequence_number, data)

rawsocket = socket.socket(
    socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname('icmp'))
rawsocket.sendto(icmp_packet, ('220.181.38.149', 80))

block_timeout = 2
while True:
    what_ready = select.select([rawsocket], [], [], block_timeout)
    if what_ready[0] == []:
        print('超时')
        break
    received_packet, re_addr = rawsocket.recvfrom(1024)

    icmp_header = received_packet[20:28]

    r_type, r_code, r_checksum, p_id, r_sequence = struct.unpack(
        '>BBHHH', icmp_header)

    if r_type == 0 and r_sequence == sequence_number:
        print('收到回复')
        break

