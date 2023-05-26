import pandas as pd
import string
from jinja2 import Template
import smtplib
from email.mime.text import MIMEText
import argparse

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
    parser = argparse.ArgumentParser(description='PerfReviewEmailSender')
    parser.add_argument("-e", "--email", help="Sender email", default="zhidongzhang.work@gmail.com")
    parser.add_argument("-p", "--password", help="Sender email password", default="vgnnntyzmdnrepvq")
    parser.add_argument("-d", "--data", help="Employee performance data in csv", default="sample_data.csv")
    parser.add_argument("-t", "--template", help="An email template in html", default="template.html")
    parser.add_argument("-c", "--cc", help="CC Lists in csv", default="cc.csv")
    parser.add_argument("-y", "--year", help="Performance Review Year", default="2023")
    parser.add_argument("-m", "--month", help="Performance Review Month", default="Apirl")
    parser.add_argument("-n", "--name_column", help="The column code for name column", default="D")
    args = parser.parse_args()
    
    # Build CC Map
    cc_df = pd.read_csv(args.cc)
    name_to_recipients = {}
    name_to_cc_recipients = {}
    for _, row in cc_df.iterrows():
        name_to_recipients[row[0]] = row[1].split(",")
        name_to_cc_recipients[row[0]] = row[2].split(",")    

    with open(args.template, 'r') as f:
        template = Template(f.read())

    df = pd.read_csv(args.data)

    htmls = []
    for _, row in df.iterrows():
        context = {}
        for column_index, item in enumerate(row):
            column_code = column_index_to_code(column_index) 
            context[column_code] = item
        context["month"] = args.month
        html = template.render(context)
        htmls.append(html)
        
        subject = "{} {} Statistics Task Review".format(args.year, args.month)
        body = html
        sender = args.email
        recipients = name_to_recipients[context[args.name_column]]
        cc_recipients = name_to_cc_recipients[context[args.name_column]]
        password = args.password
        send_email(subject, body, sender, recipients, cc_recipients, password)

if __name__ == "__main__":
    main()