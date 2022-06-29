import smtplib
import os
import email.message
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

emailaddr = os.environ['email']
password = os.environ['pass']

def sendEmail(recip, subj, cont):
  s = smtplib.SMTP_SSL('smtp.gmail.com', 465)
  s.ehlo()
  try:
    s.login(emailaddr, password)
  except Exception as errorcode:
    print("Error logging in: " + str(errorcode))
  msg = email.message.EmailMessage()
  content = cont
  msg['from'] = "DRAT Learning Org."
  msg["to"] = recip
  msg["Subject"] = subj
  msg.set_content(content)
  s.send_message(msg)
  return True