import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

send_from = 'weidongjackzhang@outlook.com'
#send_to = 'Matthew@thirdwavesa.co.za'
send_to = 'star1987lei@gmail.com'
subject = 'Hello, your csv!'
text = 'Your csv file was updated'
username = 'weidongjackzhang@outlook.com'
password = 'admin1987'
msg = MIMEMultipart()
msg['From'] = send_from
msg['To'] = send_to
msg['Date'] = formatdate(localtime=True)
msg['Subject'] = subject
msg.attach(MIMEText(text))

part = MIMEBase('application', "octet-stream")
part.set_payload(open("result.csv", "rb").read())
encoders.encode_base64(part)
part.add_header('Content-Disposition', 'attachment; filename="result.csv"')
msg.attach(part)

# context = ssl.SSLContext(ssl.PROTOCOL_SSLv3)
# SSL connection only working on Python 3+
smtp = smtplib.SMTP('smtp.live.com', 587)

smtp.starttls()
smtp.login(username, password)
smtp.sendmail(send_from, send_to, msg.as_string())
smtp.quit()
