# !/usr/bin/env python3

import argparse
import json
import os
import sys

import smtp
from message import Message
from smtp import SMTP, SMTP_PORT, SMTP_SERVER

SENDER = "From"
RECEIVERS = "To"
TEXT = "Text"
SUBJECT = "Subject"
ATTACHMENTS = "Attachments"


def main():
    parser = argparse.ArgumentParser(
        usage='{} [OPTIONS]'.format(os.path.basename(sys.argv[0])),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='SMTP client, with cool CUI. To')
    parser.add_argument('address', help='address to connect',
                        nargs='?', default=SMTP_SERVER)
    parser.add_argument('port', help='port', nargs='?',
                        type=int, default=SMTP_PORT)
    group = parser.add_mutually_exclusive_group()

    group.add_argument('-c', '--console', action="store_true", help="Enable console mode")
    group.add_argument('-s', '--settings', metavar="FILE", type=str, default="input.json",
                       help="JSON file with settings. MUST have following keys:\n"
                            f"{', '.join([SENDER, RECEIVERS, SUBJECT, TEXT, ATTACHMENTS])}")

    args = parser.parse_args()
    smtp_con = SMTP(args.address, args.port)
    print(smtp_con.connect())
    if args.console:
        smtp_con.run_batch()
    else:
        send_mail(smtp_con, args.settings)


def send_mail(smtp_con, settings_file):
    """

    :param settings_file:
    :type smtp_con: SMTP
    :return:
    """
    with open(settings_file, 'r', encoding=smtp.ENCODING) as f:
        config = json.loads(f.read())
    sender = config[SENDER]
    receivers = config[RECEIVERS]
    subject = config[SUBJECT]
    attachments = config[ATTACHMENTS]
    with open(config[TEXT], 'r', encoding=smtp.ENCODING) as f:
        text_lines = f.readlines()
    message = Message(sender, receivers, subject, text_lines, attachments)
    email = message.get_email()
    print(smtp_con.ehllo())
    print(smtp_con.auth())
    print(smtp_con.mail_from(sender))
    for receiver in receivers:
        print(smtp_con.rcpt_to(receiver))
    print(smtp_con.data())
    print(smtp_con.send(email))
    print(smtp_con.quit())


if __name__ == '__main__':
    sys.exit(main())
