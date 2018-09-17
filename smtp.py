# !/usr/bin/env python3
import base64
import re
import socket
import ssl

from errors import TransientError, ProtectedError, PermanentError
from message import Message

SMTP_PORT = 465
SMTP_SERVER = 'smtp.yandex.ru'

ENCODING = 'utf-8'
MAXLENGTH = 8192


CRLF = '\r\n'
B_CRLF = b'\r\n'


class SMTP:
    welcome = None
    closed = False

    def __init__(self, address=None, port=None):
        if not address and not port:
            self.address = None
        else:
            self.address = (address, port)
        self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.receivers = []
        self.from_ = ""
        self.subject = ""

        self.commands = {"HELO": self.hello,
                         "EHLO": self.ehllo,
                         "AUTH": self.auth,
                         "DATA": self.data_console,
                         "QUIT": self.quit,
                         "FROM": self.mail_from,
                         "TO": self.rcpt_to,
                         "HELP": self.help,
                         }

    def hello(self):
        """
        These commands are used to identify the SMTP client to the SMTP
        server.
        :return:
        """
        rep = self.send("HELO BOB" + CRLF)
        return rep

    def help(self):
        header = "List of available commands:\n"
        body = ", ".join(cmd for cmd in self.commands.keys())
        return header + body

    def ehllo(self):
        """
        Same as HELO, but also gets a list of the supported SMTP service extensions
        :return:
        """
        rep = self.send("EHLO ALICE" + CRLF)
        return rep

    def auth(self, username="inet.task@yandex.ru", password="inet.task."):
        """
        Sign in, using username and password, encoded in base64 (PLAIN)
        :param username:
        :param password:
        :return:
        """
        base64_str = ("\x00" + username + "\x00" + password).encode()
        base64_str = base64.b64encode(base64_str)
        auth_msg = "AUTH PLAIN ".encode() + base64_str + CRLF.encode()
        rep = self.send(auth_msg, False)
        return rep

    def mail_from(self, address):
        """
        This command tells the SMTP-receiver that a new mail transaction is
        starting and to reset all its state tables and buffers, including any
        recipients or mail data.
        :param address:
        :return:
        """
        self.from_ = '<' + address + '>'
        rep = self.send(f"MAIL FROM: {self.from_}" + CRLF)
        return rep

    def rcpt_to(self, address):
        """
        This command is used to identify an individual recipient of the mail data;
        multiple recipients are specified by multiple uses of this command.
        :param address:
        :return:
        """
        address = '<' + address + '>'
        self.receivers.append(address)
        rep = self.send(f"RCPT TO: {address}" + CRLF)
        return rep

    def data(self):
        """
        The receiver treats the lines following the command as mail
        data from the sender.  This command causes the mail data
        from this command to be appended to the mail data buffer.

        The mail data is terminated by a line containing only a
        period, that is the character sequence "<CRLF>.<CRLF>"
        This is the end of mail data indication.
        :return:
        """
        rep = self.send('DATA' + CRLF)
        return rep

    def data_console(self):
        """
        Forms message from the stdin text.
        :return:
        """
        print(self.data())
        line = input()
        first_iter = True
        data = []
        while line != '.' or first_iter:
            data.append(line)
            first_iter = False
            line = input()
        message = Message(self.from_, self.receivers, self.subject, data, [])
        rep = self.send(message.get_email())
        return rep

    def quit(self):
        """
        End the session
        :return:
        """
        rep = self.send("QUIT" + CRLF)
        self.closed = True
        self.control_socket.shutdown(socket.SHUT_RDWR)
        self.control_socket.close()
        return rep

    def send(self, command, text=True):
        """
        Send a command to server
        :param text:
        :param command:
        :return:
        """
        if text:
            self.control_socket.sendall(command.encode(ENCODING))
        else:
            self.control_socket.sendall(command)
        return self.get_reply()

    def connect(self, address=None, port=None):
        """
        Connect to the server and print welcome message
        :return:
        """
        if not self.address:
            self.address = (address, port)
        elif not address and not port and not self.address:
            raise Exception("Address and port must be specified in "
                            "constructor or in connect()")
        self.control_socket = ssl.wrap_socket(
            self.control_socket, ssl_version=ssl.PROTOCOL_SSLv23)
        self.control_socket.connect(self.address)
        self.welcome = self.get_reply()
        return self.welcome

    def get_reply(self):
        """
        Get a reply from server
        :return:
        """
        reply = self.__get_full_reply()
        c = reply[:1]
        if c in {'1', '2', '3'}:
            return reply
        if c == '4':
            raise TransientError(reply)
        if c == '5':
            raise PermanentError(reply)
        raise ProtectedError(reply)

    def __get_full_reply(self):
        """
        Get a long reply
        :return:
        """
        reply = ''
        tmp = self.control_socket.recv(MAXLENGTH).decode(ENCODING)
        reply += tmp
        reply_reg = re.compile(r'^\d\d\d .*$', re.MULTILINE)
        while not re.findall(reply_reg, tmp):
            try:
                tmp = self.control_socket.recv(MAXLENGTH).decode(ENCODING)
                reply += tmp
            except TimeoutError:
                print("Timeout!")
                break
        return reply

    def run_batch(self):
        """
        Runs an SMTP client in console mode
        :return:
        """
        while not self.closed:
            print("Type a command:")
            inp = input().split(' ')
            command = inp[0].upper()
            arguments = inp[1:]
            if command in self.commands:
                if arguments:
                    if len(arguments) == 1:
                        print(
                            self.commands[command](arguments[0]))
                    if len(arguments) == 2:
                        print(
                            self.commands[command](arguments[0],
                                                   arguments[1]))
                else:
                    print(self.commands[command]())
            else:
                print("UNKNOWN COMMAND")
