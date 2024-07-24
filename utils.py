import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config

def send_otp(email, otp):
    msg = MIMEMultipart()
    msg['From'] = Config.SENDER_MAIL
    msg['To'] = email
    msg['Subject'] = "Your OTP for Login"
    
    body = f"Your OTP is: {otp}"
    
    msg.attach(MIMEText(body, 'plain'))
    
    server = smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT)
    server.starttls()
    server.login(Config.SENDER_MAIL, Config.SENDER_APP_PASSWORD)
    text = msg.as_string()
    server.sendmail(Config.SENDER_MAIL, email, text)
    server.quit()

def otp_verification(stored_otp, user_otp):
    return stored_otp == user_otp