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
    parser.add_argument('-e', '--encoding', type=str, help="Choose server's "
                                                           "encoding")

    args = parser.parse_args()
    if args.encoding:
        smtp.ENCODING = args.encoding
    con = SMTP(args.address, args.port)
    print(con.connect())
    con.run_batch()


if __name__ == '__main__':
    sys.exit(main())
