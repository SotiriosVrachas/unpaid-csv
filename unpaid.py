#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Unpaid CSV.
A script for Hackerspace.gr to remind members of their late subscription fees.
"""

#    Copyright (C) 2016  Sotirios Vrachas <sotirio@vrachas.net>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from csv import reader
from datetime import date, datetime
from string import Template
from smtplib import SMTP
from email.mime.text import MIMEText
from email.header import Header
from email_template import SUBJECT, BODY
import config

TODAY = date.today()


def send_email(to_addr, subject, body):
    """Sends Email"""
    msg = MIMEText(body.encode('utf-8'), _charset='utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = config.EMAIL_FROM
    msg['To'] = to_addr
    if config.EMAIL_METHOD == 'smtp':
        server = SMTP(config.SMTP_SERVER)
        if config.SMTP_SECURETY == 'starttls':
            server.starttls()
        if config.SMTP_AUTH:
            server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
        server.sendmail(config.EMAIL_FROM, [to_addr], msg.as_string())
        server.quit()
    elif config.EMAIL_METHOD == 'sendmail':
        from subprocess import Popen, PIPE
        proc = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE)
        proc.communicate(msg.as_string())
    else:
        print(msg.as_string())


def subscription_due(last_paid):
    """Check if fees are due"""
    passed_days = (TODAY - last_paid).days
    if passed_days > config.INTERVAL_DAYS:
        return passed_days - config.INTERVAL_DAYS


def mail_loop(members):
    """Loop over members. Calls send_email if fees are due"""
    for member in members:
        last_paid = datetime.strptime(member[2], '%Y-%m-%d').date()
        days_due = subscription_due(last_paid)
        if days_due:
            name = member[0]
            to_addr = member[1]
            subject = Template(SUBJECT).substitute(name=name, to_addr=to_addr,
                                                   days_due=days_due,
                                                   last_paid=last_paid)
            body = Template(BODY).substitute(name=name, to_addr=to_addr,
                                             days_due=days_due,
                                             last_paid=last_paid)
            send_email(to_addr, subject, body)


with open(config.FILENAME, 'rt') as csvfile:
    MEMBERS = reader(csvfile, delimiter=',')
    mail_loop(MEMBERS)
