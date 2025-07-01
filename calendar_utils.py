import os 
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from datetime import datetime, timedelta

SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events'
]

def get_calendar_service():
    creds = None

    if os.path.exists('token.json'):
        print("load token.json")
        creds = Credentials.from_authorized_user_file('token.json',SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refresh tokens.")
            creds.refresh(Request())
        
        else:
            print("Open browser for login.")
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json',SCOPES)
            creds = flow.run_local_server(port=0)
        
        print("saving tokens")
        with open('token.json','w') as token:
            token.write(creds.to_json())
    
    print("connected to calendar")
    return build('calendar','v3',credentials=creds)

def calendar_check_availability(start_time,end_time):
    service = get_calendar_service()

    body = {
        "timeMin": start_time.isoformat() + "Z",
        "timeMax": end_time.isoformat() + "Z",
        "timeZone": "Asia/Kolkata",
        "items": [{"id":"primary"}]
    }

    events_result = service.freebusy().query(body = body).execute()
    busy_times = events_result["calendars"]["primary"]["busy"]

    if not busy_times:
        return True
    
    else:
        return False
    
def book_event(summary,start_time,end_time):
    service = get_calendar_service()

    event = {
        'summary': summary,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'Asia/Kolkata',
        },
        'end': {
            'dateTime':end_time.isoformat(),
            'timeZone': 'Asia/Kolkata',
        }
    }

    event = service.events().insert(calendarId = 'primary', body = event).execute()
    return event.get('htmlLink')

# if __name__ == '__main__':
#     get_calendar_service()