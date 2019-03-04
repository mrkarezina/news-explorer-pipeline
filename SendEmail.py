
#! /usr/bin/python

import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# me == my email address
# you == recipient's email address
you = "kristina.arezina@ocsbstudent.ca"
me = "marez1@ocdsb.ca"

# Create message container - the correct MIME type is multipart/alternative.
msg = MIMEMultipart('alternative')
msg['Subject'] = "Email Template"
msg['From'] = me
msg['To'] = you

# Create the body of the message (a plain-text and an HTML version).
text = "Hi!\nHow are you?\nDo you want to make an HTML / CSS email template:\nhttps://www.constantcontact.com/ca/email-templates"
html = """\
<html>
  <head></head>
  <body>
    <p>Hi!<br>
       How are you?<br>
       Do you want to make an HTML / CSS email template:\n <a href="https://www.constantcontact.com/ca/email-templates">link</a>. This email was sent using Python, and we'll be using this template to sent the personal curated reccomended reading.
    </p>
  </body>
</html>
"""

# Record the MIME types of both parts - text/plain and text/html.
part1 = MIMEText(text, 'plain')
part2 = MIMEText(html, 'html')

# Attach parts into message container.
# According to RFC 2046, the last part of a multipart message, in this case
# the HTML message, is best and preferred.
msg.attach(part1)
msg.attach(part2)


server = smtplib.SMTP('smtp.gmail.com:587')
server.starttls()
server.login('marez1@ocdsb.ca','6256142779')
server.sendmail(me, you, msg.as_string())
server.quit()