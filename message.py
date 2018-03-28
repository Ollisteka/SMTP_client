import base64

from smtp import CRLF

BOUNDARY = "--===============012345678=="
UPPER_HEADER = 'Content-Type: multipart/mixed; boundary="{}"\r\n'.format(BOUNDARY[2:])
MIME_VERSION = "MIME-Version: 1.0" + CRLF
ATTACHMENT_TEMPLATE = '\r\nContent-Type: application/octet-stream;\r\n' \
                      'MIME-Version: 1.0\r\n' \
                      'Name="{0}"\r\n' \
                      'Content-Transfer-Encoding: base64 \r\n' \
                      'Content-Disposition: attachment; filename="{0}"\r\n\r\n'

class Message:
    def __init__(self, from_, to, topic, text_lines, attachments):
        self.subject = "Subject: " + topic
        self.sender = "From: <" + from_ + ">"
        self.receivers = to[:]
        self.attachments = attachments
        self.email = None
        self.msg = self.parse_message(text_lines)

    def get_email(self):
        if self.email:
            return self.email
        self.email = ""
        self.email += self.fill_header() + CRLF
        self.email += BOUNDARY + CRLF
        self.email += self.mime_message() + CRLF
        for file in self.attachments:
            self.email += self.append_attachment(file) + CRLF
        self.email += BOUNDARY + "--" + CRLF
        self.email += '.' + CRLF
        return self.email

    def mime_message(self):
        return 'Content-Type: text/plain; charset="utf-8"\r\n' \
                      'MIME-Version: 1.0\r\n' \
                      'Content-Transfer-Encoding: 8bit\r\n\r\n' \
               + self.msg

    def fill_header(self):
        return UPPER_HEADER \
               + MIME_VERSION \
               + CRLF.join([self.sender, self.get_recievers(), self.subject]) \
               + CRLF

    def append_attachment(self, filename):
        header = BOUNDARY
        header += ATTACHMENT_TEMPLATE.format(filename)

        with open(filename, 'rb') as f:
            data = base64.b64encode(f.read())

        header += data.decode('utf8') + CRLF
        return header

    def parse_message(self, msg_lines):
        data = []
        for line in msg_lines:
            first_char = line[0]
            if first_char == '.':
                line = '.' + line
            data.append(line)
        return CRLF.join(data) + CRLF

    def get_recievers(self):
        header = "To: <"
        for receiver in self.receivers:
            header += receiver + '>, <'
        return header[:-3]
