import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate

PORT = 465
CONTEXT = ssl.create_default_context()

class Mail:
    def __init__(self, user: str, pswd: str, rcpt_email: str):
        self.user = user
        self.pswd = pswd
        self.rcpt_email = rcpt_email
    
    def send_email(self, msg: MIMEMultipart):
        msg['Date'] = formatdate(localtime=True)
        
        with smtplib.SMTP_SSL('smtp.gmail.com', PORT, context=CONTEXT) as server:
            server.login(self.user, self.pswd)
            server.sendmail(self.user, self.rcpt_email, msg.as_string())