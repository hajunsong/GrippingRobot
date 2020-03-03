#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import argparse
import sys, select, termios, tty


def getKey():
    settings = termios.tcgetattr(sys.stdin)
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--HOST', type=str, default='127.0.0.1')
    parser.add_argument('--PORT', type=int, default=9999)

    args = parser.parse_args()
    HOST = args.HOST
    PORT = args.PORT

    print 'HOST : {0}, PORT : {1}'.format(HOST, PORT)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # SOCK_STREAM은 TCP socket을 뜻함
    sock.bind((HOST, 0))

    connected = False

    while ~connected:
        try:
            sock.connect((HOST, PORT))  # 서버에 연결 요청
            connected = True
            break
        except:
            connected = False

    print 'connected server'
    send_message = '0'

    while True:
        key = getKey()
        if key != '':
            if key == 'q':
                send_message = key
                sbuff = bytes(send_message)
                sock.send(sbuff)  # 메시지 송신
                print('송신:{0}'.format(send_message))
                break
            else:
                send_message = key
                sbuff = bytes(send_message)
                sock.send(sbuff)  # 메시지 송신
                print('송신:{0}'.format(send_message))
