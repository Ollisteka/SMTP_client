# !/usr/bin/env python3
import base64
import re
import socket
import ssl

from errors import TransientError, ProtectedError, PermanentError

SMTP_PORT = 465
SMTP_SERVER = 'smtp.yandex.ru'#'smtp-relay.gmail.com'

FROM_MAIL = "gekkelolga@gmail.com"

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
        self.sender = ""
        self.subject = ""

        self.commands = {"HELO": self.hello,
                         "EHLO": self.ehllo,
                         "AUTH": self.auth,
                         "DATA": self.data_console,
                         "QUIT": self.quit,
                         "FROM": self.mail_from,
                         "TO": self.rcpt_to,
                         }

    def hello(self):
        rep = self.send("HELO BOB" + CRLF)
        return rep

    def help(self):
        rep = self.send("HELP" + CRLF)
        return rep

    def ehllo(self):
        rep = self.send("EHLO ALICE" + CRLF)
        return rep

    def mail_from(self, address):
        self.sender = '<' + address + '>'
        rep = self.send("MAIL FROM: " + self.sender + CRLF)
        return rep

    def rcpt_to(self, address):
        address = '<' + address + '>'
        self.receivers.append(address)
        rep = self.send("RCPT TO: " + address + CRLF)
        return rep

    def data(self):
        rep = self.send('DATA' + CRLF)
        return rep

    def data_console(self):
        print(self.data())
        line = input()
        first_iter = True
        content = "Content-Type: text/plain" + CRLF
        data = []
        data.extend([self.get_sender(), self. get_recievers(), self.get_subject(), content])
        while line != '.' or first_iter:
            first_char = line[0]
            if first_char == '.':
                line = '.' + line
            data.append(line)
            first_iter = False
            line = input()
        data.append('.')
        msg = CRLF.join(data)
        rep = self.send(msg + CRLF)
        return rep

    def get_sender(self):
        return "From: " + self.sender

    def set_subject(self, topic=""):
        self.subject = topic

    def get_recievers(self):
        header = "To: "
        for receiver in self.receivers:
            header += receiver + ', '
        return header[:-2]

    def get_subject(self):
        return "Subject: " + self.subject

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

    def auth(self, username="inet.task@yandex.ru", password="inet.task."):
        base64_str = ("\x00" + username + "\x00" + password).encode()
        base64_str = base64.b64encode(base64_str)
        auth_msg = "AUTH PLAIN ".encode() + base64_str + CRLF.encode()
        rep = self.send(auth_msg, False)
        return rep

    def send_message(self, msg):
        """

        :type msg: Message
        :return:
        """
        self.mail_from(msg.sender)
        for address in msg.receivers:
            self.rcpt_to(address)

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
        Runs an ftp client in console mode
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
