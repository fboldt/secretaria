import imaplib
import email
import smtplib, ssl
import dotenv
dotenv.load_dotenv()

EMAIL_ADRESS=dotenv.get_key('.env', 'EMAIL_ADRESS')
EMAIL_PASSWORD=dotenv.get_key('.env', 'EMAIL_PASSWORD')

def create_imap_connection():
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(EMAIL_ADRESS, EMAIL_PASSWORD)
    return mail

def fetch_emails(mail, query='ALL'):
    mail.select('inbox')
    _, response = mail.search(None, query)
    unread_msg_nums = response[0].split()
    emails = {}
    for e_id in unread_msg_nums:
        _, msg_data = mail.fetch(e_id, '(RFC822)')
        emails[e_id.decode()] = extract_email_info(msg_data)
    return emails

def extract_email_info(msg_data):
    msg = email.message_from_bytes(msg_data[0][1])
    return {
            'subject': msg['subject'],
            'from': msg['from'],
            'date': msg['date'],
            'content': extract_email_content(msg)
        }

def extract_email_content(msg):
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if content_type == "text/plain" and "attachment" not in content_disposition:
                return part.get_payload(decode=True).decode()
    else:
        return msg.get_payload(decode=True).decode()
    return ""

def print_emails(emails):
    if not emails:
        print("No email found.")
        return
    for e_id, data in emails.items():
        print_email_info(e_id, data)

def print_email_info(e_id, data):
    print(f"ID: {e_id}")
    print(f"From: {data['from']}")
    print(f"Subject: {data['subject']}")
    print(f"Date: {data['date']}")
    print(f"Content: {data['content']}")
    print('-' * 40)

def reply_emails(emails, reply_body):
    for e_id, data in emails.items():
        print_email_info(e_id, data)
        reply_email(reply_body, data)

def reply_email(reply_body, data):
    reply_msg = email.message.EmailMessage()
    reply_msg.set_content(reply_body)
    reply_msg['Subject'] = f"Re: {data['subject']}"
    reply_msg['From'] = EMAIL_ADRESS
    reply_msg['To'] = data['from']
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(EMAIL_ADRESS, EMAIL_PASSWORD)
        server.send_message(reply_msg)

if __name__ == "__main__":
    mail = create_imap_connection()
    emails = fetch_emails(mail, 'UNSEEN')
    reply_emails(emails, "Thank you for your email. I will get back to you shortly.")
    emails = fetch_emails(mail, 'ALL')
    print_emails(emails)
    mail.logout()
