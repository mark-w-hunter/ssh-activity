#!/usr/bin/env python3

# ssh_activity: Check ssh activity
# author: Mark W. Hunter
# https://github.com/mark-w-hunter/ssh-activity
#
# The MIT License (MIT)
#
# Copyright (c) 2020 Mark W. Hunter
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Check for ssh activity and return results."""
import socket
import smtplib
import sys


class SSHCheck:
    """Class for checking ssh activity."""
    def __init__(self):
        self.filepath = "/var/log/auth.log"  # location of authentication log

    def check_failed(self):
        """Check log for failed ssh attempts and return result."""
        failed_attempts = ["Failed ssh attempts:"]
        header_line = "-" * len(failed_attempts[0])
        failed_attempts.append(header_line)
        with open(self.filepath) as authlog:
            for line in authlog:
                # relies on rsyslog high precision timestamps
                if "preauth" in line and "user" in line:
                    fields = line.strip().split()
                    attempt = fields[0] + " " + fields[7] + " " + fields[8]
                    failed_attempts.append(attempt)
        failed_attempts.append("")
        return failed_attempts

    def check_success(self):
        """Check log for successful ssh logins and return result."""
        successful_logins = ["Successful ssh logins:"]
        header_line = "-" * len(successful_logins[0])
        successful_logins.append(header_line)
        with open(self.filepath) as authlog:
            for line in authlog:
                if "Accepted" in line:
                    fields = line.strip().split()
                    login = fields[0] + " " + fields[6] + " " + fields[8]
                    successful_logins.append(login)
        successful_logins.append("")
        return successful_logins


class SSHReport:
    """Class for providing ssh activity results."""
    def __init__(self):
        self.smtp_server = "localhost"
        self.smtp_port = 25
        self.sender_email = "username@localhost"  # replace with sender email
        self.receiver_email = "username@localhost"  # replace with receiver email
        self.subject = "Subject: ssh activity\n\n"
        self.header = "Host: " + socket.gethostname() + "\n\n"

    def email_ssh_report(self, results):
        """Send email report of ssh activity."""
        body = self.header
        try:
            smtp_server = smtplib.SMTP(self.smtp_server, self.smtp_port)
        except ConnectionRefusedError:
            print("Error: No SMTP server available.")
            sys.exit(1)
        for instance in results:
            body += instance + "\n"
        message = self.subject + body
        if results:
            smtp_server.sendmail(self.sender_email, self.receiver_email, message)

    def print_ssh_report(self, results):
        """Print report of ssh activity."""
        body = self.header
        for instance in results:
            body += instance + "\n"
        print(body)


def main():
    """Run main program."""
    ssh_check = SSHCheck()
    ssh_failed = ssh_check.check_failed()
    ssh_success = ssh_check.check_success()
    ssh_activity = ssh_failed + ssh_success
    ssh_report = SSHReport()
    ssh_report.print_ssh_report(ssh_activity)
    # ssh_report.email_ssh_report(ssh_activity)


if __name__ == "__main__":
    main()
