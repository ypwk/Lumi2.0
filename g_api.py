from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle
import datetime

# Define the scopes for both Google Tasks and Google Calendar
SCOPES = [
    "https://www.googleapis.com/auth/tasks",
    "https://www.googleapis.com/auth/calendar.readonly",
]


def authenticate_google_services():
    creds = None
    # Check if token.pickle already exists (it contains the access and refresh tokens)
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return creds


def get_services():
    creds = authenticate_google_services()

    # Create service for Google Tasks
    tasks_service = build("tasks", "v1", credentials=creds)

    # Create service for Google Calendar
    calendar_service = build("calendar", "v3", credentials=creds)

    return tasks_service, calendar_service


def get_calendar_events(calendar_service):
    # Get the current time in ISO format
    now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time

    # Retrieve events from the primary calendar
    events_result = (
        calendar_service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    events = events_result.get("items", [])

    if not events:
        print("No upcoming events found.")
    else:
        print("Upcoming events:")
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(f"{start} - {event['summary']}")

    return events


def get_tasks(tasks_service):
    # Get all the task lists available in your account
    tasklists_result = tasks_service.tasklists().list().execute()
    tasklists = tasklists_result.get("items", [])

    # Display the available task lists
    if not tasklists:
        print("No task lists found.")
    else:
        print("Task lists:")
        for tasklist in tasklists:
            print(f"{tasklist['title']} (ID: {tasklist['id']})")
            tasks_result = tasks_service.tasks().list(tasklist=tasklist["id"]).execute()
            tasks = tasks_result.get("items", [])
            if not tasks:
                print("No tasks found.")
            else:
                print("Tasks:")
                for task in tasks:
                    print(f"- {task['title']} (Status: {task['status']})")

    return tasks


if __name__ == "__main__":
    # Get both services using the authenticated credentials
    tasks_service, calendar_service = get_services()

    # Get calendar events
    events = get_calendar_events(calendar_service)

    # Get tasks
    tasks = get_tasks(tasks_service)
