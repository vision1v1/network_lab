

# https://blog.csdn.net/zhj082/article/details/80531628
def checksum1(data):
    """
    校验
    """
    n = len(data)
    m = n % 2
    sum = 0
    for i in range(0, n - m, 2):
        # 传入data以每两个字节（十六进制）通过ord转十进制，第一字节在低位，第二个字节在高位
        sum += (data[i]) + ((data[i+1]) << 8)
    if m:
        sum += (data[-1])
    # 将高于16位与低16位相加
    sum = (sum >> 16) + (sum & 0xffff)
    sum += (sum >> 16)  # 如果还有高于16位，将继续与低16位相加
    answer = ~sum & 0xffff
    # 主机字节序转网络字节序列（参考小端序转大端序）
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

# https://www.jianshu.com/p/14113212cd18
def checksum2(data):
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

# 1 将校验和字段置为0。
# 2 将每两个字节（16位）相加（二进制求和）直到最后得出结果，若出现最后还剩一个字节继续与前面结果相加。
# 3 (溢出)将高16位与低16位相加，直到高16位为0为止。
# 4 将最后的结果（二进制）取反。

# https://datatracker.ietf.org/doc/html/rfc1071#section-4.1
def checksum3(data):
    n = len(data)
    m = n % 2

    # 1 将校验和字段置为0。
    sum = 0
    for i in range(0, n-m, 2):

        # 2 先转由大端 转 小端序，
        # 然后 将每两个字节（16位）相加（二进制求和）直到最后得出结果，若出现最后还剩一个字节继续与前面结果相加。
        sum += data[i] | data[i+1] << 8
    
    # 奇数时将
    if m:
        sum += data[-1]
    
    while sum >> 16:
        sum = (sum >> 16) + (sum & 0xffff)

    checksum = ~sum & 0xffff

    # checksum = (checksum << 8) | ((checksum & 0xff00) >> 8)

    # ok 1
    # checksum = ((checksum & 0x00ff) << 8) | ((checksum & 0xff00) >> 8)

    # ok 2
    checksum = (checksum >> 8 | (checksum & 0x00ff) << 8)

    return checksum 



if __name__ == "__main__":
    data = b"\x08\x00\x00\x00\x00\x00\x00\x01\x61\x61\x61\x61\x61\x61\x61\x61" \
        b"\x62\x62\x62\x62\x62\x62\x62\x62\x63\x63\x63\x63\x63\x63\x63\x63" \
        b"\x64\x64\x64\x64\x64\x64\x64\x64"

    # 正确的是 0xc9d0

    # 0xc9d0
    print(hex(checksum1(data)))

    # 0xc9d0
    print(hex(checksum2(data)))

    print(hex(checksum3(data)))