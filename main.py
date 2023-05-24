import pandas as pd
import string
from jinja2 import Template
import smtplib
from email.mime.text import MIMEText

def column_index_to_code(column_index):
    column_code_chars = []
    while column_index > -1:
        column_code_chars.append(string.ascii_uppercase[column_index % 26])
        column_index //= 26
        column_index -= 1
    return ''.join(column_code_chars[::-1])

def send_email(subject, body, sender, recipients, cc_recipients, password):
    msg = MIMEText(body, 'html')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    msg['Cc'] = ', '.join(cc_recipients)
    smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp_server.login(sender, password)
    smtp_server.sendmail(sender, recipients + cc_recipients, msg.as_string())
    smtp_server.quit()

def main():
    with open('template.html', 'r') as f:
        template = Template(f.read())

    df = pd.read_csv('sample_data.csv')

    htmls = []
    for _, row in df.iterrows():
        context = {}
        for column_index, item in enumerate(row):
            column_code = column_index_to_code(column_index) 
            context[column_code] = item
        html = template.render(context)
        htmls.append(html)
        
        subject = "Performance Review for {}".format(context["D"])
        body = html
        sender = "zhidongzhang.work@gmail.com"
        recipients = context["B"].split(",")
        cc_recipients = context["C"].split(",")
        password = "vgnnntyzmdnrepvq"
        send_email(subject, body, sender, recipients, cc_recipients, password)

if __name__ == "__main__":
    main()