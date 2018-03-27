from smtp import CRLF
import base64


BOUNDARY = "--===============012345678=="
UPPER_HEADER = 'Content-Type: multipart/mixed; boundary="{}"'.format(BOUNDARY[2:]) + CRLF
MIME_VERSION = "MIME-Version: 1.0" + CRLF
ATTACHMENT_TEMPLATE = 'Content-Type: application/octet-stream;\r\n' \
                          'Name="{0}"\r\n' \
                          'MIME-Version: 1.0\r\n' \
                          'Content-Transfer-Encoding: base64 \r\n' \
                          'Content-Disposition: attachment; \r\n' \
                          'filename="{0}"\r\n'

class Message:
    def __init__(self, from_, to, topic, text_lines, attachments):
        self.subject = "Subject: " + topic
        self.sender = "From: " + from_
        self.receivers = []
        self.attachments = attachments
        self.email = None
        for receiever in to:
            self.receivers.append(receiever)
        self.msg = self.parse_message(text_lines)

    def get_email(self):
        if self.email:
            return self.email
        self.email = ""
        self.email += self.fill_header()
        self.email += self.mime_message()
        for file in self.attachments:
            self.email += self.append_attachment(file)

    def mime_message(self):
        return 'Content-Type: text/plain; charset="utf-8"\r\n' \
                      'MIME-Version: 1.0\r\n' \
                      'Content-Transfer-Encoding: 8bit\r\n\r\n' \
               + self.msg

    def fill_header(self):
        return UPPER_HEADER \
               + MIME_VERSION \
               + CRLF.join([self.sender, self.get_recievers(), self.subject]) \
               + CRLF + BOUNDARY + CRLF

    def append_attachment(self, filename):
        header = BOUNDARY

    def parse_message(self, msg_lines):
        data = []
        for line in msg_lines:
            first_char = line[0]
            if first_char == '.':
                line = '.' + line
            data.append(line)
        data.append('.')
        return CRLF.join(data) + CRLF

    def get_recievers(self):
        header = "To: "
        for receiver in self.receivers:
            header += receiver + ', '
        return header[:-2]