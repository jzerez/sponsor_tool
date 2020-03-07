import smtplib, ssl
from email.message import EmailMessage
import imghdr
"""
working sending emails to localhost:4000 running local SMTP server
"""
# s = smtplib.SMTP('localhost:4000')
# msg = EmailMessage()
# msg['Subject'] = 'lol'
# me = 'floatingbrick@gmail.com'
# you = 'floatingbrick@gmail.com'
# msg['From'] = me
# msg['To'] = you
# s.send_message(msg)
# s.quit()

"""
sending encrypted emails to localhost:4000 running local SMTP server
"""

port = 587
me = 'floatingbrick@gmail.com'
you = 'floatingbrick@gmail.com'
msg = EmailMessage()
msg['Subject'] = 'test email'
msg['From'] = me
msg['To'] = you
msg.set_content(""" Hello there! Where are you going to be

tomorrow?

How about this

""")

f = open('attachments/nebula_glitchy.jpg', 'rb')
im_data = f.read()
msg.add_attachment(im_data, maintype='image',
                            subtype=imghdr.what(None, im_data),
                            filename="testimages")
f = open('attachments/ex.pdf', 'rb')
pdf_data = f.read()
msg.add_attachment(pdf_data, maintype = "application/pdf", subtype='pdf', filename='testpdf.pdf')
from creds import password

context = ssl.create_default_context()

with smtplib.SMTP("smtp.gmail.com", port) as server:
    server.starttls(context=context)
    server.login(me, password)
    server.send_message(msg)
