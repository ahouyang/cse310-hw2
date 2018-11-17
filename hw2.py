# Andy Ouyang: 110952125
# Nick Tessier: 111081497

import socket
import sys
import struct
import os
import time
import select
import statistics


def verbose_ping(dest_addr, timeout, tries):
    icmp = socket.getprotobyname("icmp")
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
    try:
        sock.connect((dest_addr, 1))
    except Exception as e:
        print('invalid url')
        sys.exit(0)
    ICMP_TYPE = 8  # Indicates an echo request
    ICMP_CODE = 0  # Indicates a ping reply
    ID = os.getpid() & 0xFFFF  # The ID will be set the ID of your running program. Since we are only given so much space, we only use the first 2 bytes
    SEQUENCE = 1  # You don't have to continuously communicate with the server. By setting the SEQ number to 1, we can treat all attempts as separate.
    times = []
    lost = 0
    for i in range(tries):
        CHECKSUM = 0
        header = struct.pack("bbHHh", ICMP_TYPE, ICMP_CODE, CHECKSUM, ID, SEQUENCE)
        data = bytes("hii", "utf-8")
        CHECKSUM = checksum(header + data)
        header = struct.pack("bbHHh", ICMP_TYPE, ICMP_CODE, CHECKSUM, ID, SEQUENCE)
        packet = header + data
        send_time = time.time()
        # print(send_time)
        # while packet:
        print('ping {}...'.format(dest_addr), end='')
        last_byte = sock.send(packet)
        packet = packet[last_byte:]
        ready_socket = select.select([sock], [], [], timeout)
        if ready_socket[0]:
            # print("ping successful")
            response = sock.recv(1024)
            rec_time = time.time()
            rtt = round((rec_time - send_time) * 1000.0, 4)
            # print(rtt)
            times.append(rtt)
        else:
            rtt = None
            lost += 1
        # print(response)
        # print(rec_time)
        if rtt is not None:
            print('get ping in {} milliseconds'.format(rtt))
        else:
            print('failed. (timeout within {} seconds)'.format(timeout))
    min_rtt = min(times) if len(times) != 0 else 0
    max_rtt = max(times) if len(times) != 0 else 0
    mean = round(statistics.mean(times),4)
    stdev = round(statistics.stdev(times), 4)
    print('packets lost: {}, min: {}ms, max: {}ms, mean: {}ms, stdev: {}ms'.format(lost, min_rtt,
            max_rtt, mean, stdev))


def checksum(source_string):
    sum = 0
    countTo = int((len(source_string) / 2)) * 2
    # print(countTo)
    count = 0
    while count < countTo:
        # print(count)
        thisVal = source_string[count + 1] * 256 + source_string[count]
        sum = sum + thisVal
        sum = sum & 0xffffffff
        count = count + 2
    if countTo < len(source_string):
        sum = sum + source_string[len(source_string) - 1]
        sum = sum & 0xffffffff
    sum = (sum >> 16) + (sum & 0xffff)
    sum = sum + (sum >> 16)
    answer = ~sum
    answer = answer & 0xffff
    # answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer


if __name__ == '__main__':
    verbose_ping(sys.argv[1], timeout=2, tries=10)
