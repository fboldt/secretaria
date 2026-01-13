import imaplib
import email
import dotenv
dotenv.load_dotenv()

EMAIL_ADRESS=dotenv.get_key('.env', 'EMAIL_ADRESS')
EMAIL_PASSWORD=dotenv.get_key('.env', 'EMAIL_PASSWORD')

def fetch_unread_emails():
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(EMAIL_ADRESS, EMAIL_PASSWORD)
    mail.select('inbox')

    status, response = mail.search(None, 'UNSEEN')
    print(f"Status: {status}, Response: {response}")
    unread_msg_nums = response[0].split()

    emails = {}

    for e_id in unread_msg_nums:
        status, msg_data = mail.fetch(e_id, '(RFC822)')
        msg = email.message_from_bytes(msg_data[0][1])

        subject = msg['subject']
        from_ = msg['from']
        date_ = msg['date']
        content_ = "\n" + extract_email_content(msg)

        emails[e_id.decode()] = {
            'subject': subject,
            'from': from_,
            'date': date_,
            'content': content_
        }

    mail.logout()
    return emails

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

def print_unread_emails(emails):
    if not emails:
        print("No unread emails found.")
        return
    for e_id, details in emails.items():
        print(f"ID: {e_id}")
        print(f"From: {details['from']}")
        print(f"Subject: {details['subject']}")
        print(f"Date: {details['date']}")
        print(f"Content: {details['content']}")
        print('-' * 40)

if __name__ == "__main__":
    unread_emails = fetch_unread_emails()
    print_unread_emails(unread_emails)
