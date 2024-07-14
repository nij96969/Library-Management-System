import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config

def send_otp(email, otp):
    msg = MIMEMultipart()
    msg['From'] = Config.MAIL_USERNAME
    msg['To'] = email
    msg['Subject'] = "Your OTP for Login"
    
    body = f"Your OTP is: {otp}"
    msg.attach(MIMEText(body, 'plain'))
    
    server = smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT)
    server.starttls()
    server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
    text = msg.as_string()
    server.sendmail(Config.MAIL_USERNAME, email, text)
    server.quit()

def verify_otp(stored_otp, user_otp):
    return stored_otp == user_otp