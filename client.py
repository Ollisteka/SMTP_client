# !/usr/bin/env python3

import argparse
import os
import sys

import smtp
from smtp import SMTP, SMTP_PORT, SMTP_SERVER


def main():
    parser = argparse.ArgumentParser(
        usage='{} [OPTIONS]'.format(
            os.path.basename(
                sys.argv[0])),
        description='SMTP client')
    parser.add_argument('address', help='address to connect',
                        nargs='?', default=SMTP_SERVER)
    parser.add_argument('port', help='port', nargs='?',
                        type=int, default=SMTP_PORT)
    parser.add_argument('-c', '--console', action="store_true", help="Enable console mode")

    args = parser.parse_args()
    con = SMTP(args.address, args.port)
    print(con.connect())
    if args.console:
        con.run_batch()
    else:
        send_mail()


def send_mail():
    with open("input.txt") as f:
        pass

if __name__ == '__main__':
    sys.exit(main())
