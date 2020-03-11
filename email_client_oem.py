import smtplib, ssl
from email.message import EmailMessage
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
def send_email(recipient, content, subject="Olin Electric Motorsports Sponsorship Request", attachement="email_util/attachments/OEM_Sponsorship_Package_19-20.pdf"):
    port = 587
    me = 'olinelectricmotorsports@gmail.com'
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = me
    msg['To'] = recipient
    msg.set_content(content)

    if attachement:
        f = open(attachement, 'rb')
        pdf_data = f.read()
        msg.add_attachment(pdf_data, maintype = "application/pdf", subtype='pdf', filename='OEM_Sponsorship_Package_19-20.pdf')

    f = open('email_util/creds.txt', 'r')
    password = f.read()[:-1]

    context = ssl.create_default_context()

    with smtplib.SMTP("smtp.gmail.com", port) as server:
        server.starttls(context=context)
        server.login(me, password)
        server.send_message(msg)

if __name__ == "__main__":
    send_email('floatingbrick@gmail.com', 'lmao', 'hehexd', attachement=None)
    send_email('mailto:floatingbrick@gmail.com', 'lmao', 'hehexd', attachement=None)
    send_email('%2sldkfj23lakjf130r9e8fslkdjflskdjfe9220498t72480t7@gmail.com', 'lmao', 'hehexd', attachement=None)
