import os
import pickle
from pathlib import Path
from typing import List, Dict, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.utils import parsedate_to_datetime

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
TOKEN_PATH = Path.home() / ".orbyt" / "token.pickle"
CREDENTIALS_PATH = Path.home() / ".orbyt" / "credentials.json"


def authenticate():
    TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    creds = None
    
    if TOKEN_PATH.exists():
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_PATH.exists():
                raise FileNotFoundError(
                    f"credentials.json not found at {CREDENTIALS_PATH}\n"
                    "Download it from Google Cloud Console and place it there."
                )
            
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_PATH), SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        with open(TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)
    
    return creds


def get_service():
    creds = authenticate()
    return build('gmail', 'v1', credentials=creds)


def is_job_alert_or_newsletter(subject: str, sender: str) -> bool:
    """Filter out job alerts, newsletters, and automated notifications"""
    subject_lower = subject.lower()
    sender_lower = sender.lower()
    
    # Common job alert/newsletter patterns
    alert_patterns = [
        'job alert', 'new job', 'job match', 'job posting', 'job opportunity',
        'career alert', 'job notification', 'job digest', 'job newsletter',
        'hiring alert', 'job update', 'job feed', 'job board', 'job search',
        'cancellation notice', 'alert has been', 'job alert has been',
        'weekly digest', 'daily digest', 'job recommendations'
    ]
    
    # Common newsletter/automated sender domains
    newsletter_domains = [
        'glassdoor.com', 'indeed.com', 'linkedin.com', 'ziprecruiter.com',
        'monster.com', 'careerbuilder.com', 'dice.com', 'angel.co',
        'ycombinator.com', 'stackoverflow.com', 'github.com', 'redditmail.com',
        'swooped.com', 'hire.com', 'ashbyhq.com', 'toptal.com', 'mercor.com',
        'join-gauntlet.com', 'substack.com', 'majorleaguehacking.com'
    ]
    
    # Check subject patterns
    for pattern in alert_patterns:
        if pattern in subject_lower:
            return True
    
    # Check sender domains
    for domain in newsletter_domains:
        if domain in sender_lower:
            return True
    
    return False


def fetch_job_emails(max_results: int = 100) -> List[Dict]:
    service = get_service()
    
    # More specific query for actual applications and responses
    query = 'subject:(application OR interview OR offer OR rejection OR "thank you for applying" OR "application received" OR "next steps" OR "schedule" OR "congratulations" OR "regret")'
    
    results = service.users().messages().list(
        userId='me',
        q=query,
        maxResults=max_results
    ).execute()
    
    messages = results.get('messages', [])
    emails = []
    
    for message in messages:
        msg = service.users().messages().get(
            userId='me',
            id=message['id'],
            format='metadata',
            metadataHeaders=['Subject', 'From', 'Date']
        ).execute()
        
        headers = msg.get('payload', {}).get('headers', [])
        
        subject = ''
        sender = ''
        date = ''
        
        for header in headers:
            name = header.get('name', '')
            value = header.get('value', '')
            
            if name.lower() == 'subject':
                subject = value
            elif name.lower() == 'from':
                sender = value
            elif name.lower() == 'date':
                try:
                    dt = parsedate_to_datetime(value)
                    date = dt.date().isoformat()
                except Exception:
                    date = ''
        
        # Filter out job alerts and newsletters
        if not is_job_alert_or_newsletter(subject, sender):
            emails.append({
                'id': message['id'],
                'subject': subject,
                'sender': sender,
                'date': date
            })
    
    return emails

