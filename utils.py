from datetime import datetime
import json
from email.mime.text import MIMEText
import smtplib


# takes a text and prints it with the current time
def print_with_time(text):
    now = datetime.now()
    print(f'({now.hour:02}:{now.minute:02}:{now.second:02}) {str(text)}')


# takes an announcement dict and converts it into string
def ann_to_string(ann):
    string = ""
    string += ann["title"]+"\n\n"
    active_between = None
    for tab in ann["tabs"]:
        if "Tarihi" in tab:
            active_between = ann["tabs"][tab]
        else:
            string += tab+": "+ann["tabs"][tab]+"\n"

    if active_between != None:
        string += "Duyurunun aktif olduğu tarih aralığı: "+active_between+"\n"

    string += "\nGönderen: "+ann["sender"]+"\n"
    string += "Gönderildiği Tarih: "+ann["date"]
    return string


# compares two announcement objects and returns true if the tabs of both are the same
def compare_announcements(ann1, ann2):
    return ("\n".join([ann1["tabs"][tab] for tab in ann1["tabs"] if "Tarihi" not in tab])
            == "\n".join([ann2["tabs"][tab] for tab in ann2["tabs"] if "Tarihi" not in tab]))


# sends an email with the subject and message passed, in order for this function to work, the info.json file must be in the current working directory
def send_mail(subject, message):
    with open("info.json", "r", encoding="utf-8") as f:
        info = json.load(f)
    msg = MIMEText(message, 'plain', 'utf-8')
    msg['Subject'] = subject
    msg['From'] = info["email"]["username"]
    msg['To'] = ",".join(info["email"]["receivers"])
    server = smtplib.SMTP_SSL(info["email"]["host"], info["email"]["port"])
    server.ehlo()
    server.login(info["email"]["username"], info["email"]["password"])
    server.send_message(msg)
    server.quit()
