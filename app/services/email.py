import smtplib

from email.mime.text import MIMEText

class EmailService:


    def send_template_email(self, to, subject, template, data = {}):
        smtplib.SMTP('localhost')