import os.path
import mysql.connector
import json

from email.utils import parsedate_to_datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import timezone

# Gmail API scope for read-only access
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def get_gmail_service():
    """
    Authenticate and return a Gmail API service object.
    """
    creds = None

    # Load existing credentials
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # Refresh or initiate new authentication if needed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save new credentials
        with open('token.json', 'w') as token_file:
            token_file.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)


def extract_headers(headers):
    """
    Extract 'From', 'Subject', 'Date' and 'To' from message headers.
    """
    desired = {'From': '', 'Subject': '', 'Date': '', 'To': ''}
    for header in headers:
        if header['name'] in desired:
            desired[header['name']] = header['value']
    return desired


def connect_db():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='password',
        database='EMAIL_MANAGER'
    )


def fetch_and_store_emails():
    """
    Fetch emails and prepare them for storing
    """
    service = get_gmail_service()
    db_conn = connect_db()
    results = service.users().messages().list(userId='me', maxResults=100).execute()
    messages = results.get('messages', [])

    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
        headers = extract_headers(msg_data['payload']['headers'])

        message_id = msg['id']
        sender = headers['From']
        subject = headers['Subject']
        receiver = headers['To']
        date_str = headers['Date']
        date = parsedate_to_datetime(date_str).astimezone(timezone.utc) if date_str else None
        # print(f"From: {sender} | Subject: {subject} | Date: {date_str} | message_id: {message_id}")

        email_data = {
            'id': message_id,  # Should use a custom uuid or something here
            'vendor_id': message_id,
            'sender': sender,
            'receiver': receiver,
            'subject': subject,
            'received_at': date,
            'raw_headers': headers,
        }
        # print(f"Inserting: ID={message_id}, From={sender}, To={receiver}, Subject={subject}, Date={date}")
        insert_email(db_conn, email_data)


def insert_email(db_conn, email_data):
    cursor = db_conn.cursor()
    query = """
        INSERT INTO emails (id, vendor_id, sender, receiver, subject, received_at, raw_headers)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            sender = VALUES(sender),
            subject = VALUES(subject),
            received_at = VALUES(received_at),
            raw_headers = VALUES(raw_headers)
    """
    cursor.execute(query, (
        email_data['id'],
        email_data['vendor_id'],
        email_data['sender'],
        email_data['receiver'],
        email_data['subject'],
        email_data['received_at'].strftime('%Y-%m-%d %H:%M:%S') if email_data['received_at'] else None,
        json.dumps(email_data['raw_headers'])

    ))
    db_conn.commit()
    cursor.close()

def fetch_emails():
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM emails"
    cursor.execute(query)
    rows = cursor.fetchall()

    emails = []
    for row in rows:
        # Optional: format or clean data
        email = {
            'id': row['id'],
            'vendor_id': row['vendor_id'],
            'sender': row['sender'],
            'receiver': row['receiver'],
            'subject': row['subject'],
            'received_at': row['received_at'].isoformat() if row['received_at'] else None,
            'raw_headers': row['raw_headers'],
            'current_folder': row['current_folder']
        }

        emails.append(email)

    cursor.close()
    conn.close()
    return emails

if __name__ == '__main__':
    fetch_and_store_emails()
