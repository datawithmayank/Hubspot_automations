import requests
import json
from datetime import datetime
import os
from dotenv import load_dotenv

# Set your Eventbrite API endpoint and credentials
events_url = "https://www.eventbriteapi.com/v3/organizations/{organization_id}/events/"
dotenv_path = "C:\\Users\\Mayank\\Documents\\API\\Hubspot-Eventbrite\\keys_config.env"

load_dotenv(dotenv_path)

eventbrite_token = os.getenv("eventbrite_token1")

# Set the organization ID
organization_id = "246534986666"
headers = {
    "Authorization": f"Bearer {eventbrite_token}"
}
events = []
response = requests.get(events_url.format(organization_id=organization_id), headers=headers)
while response.status_code == 200:
    events.extend(response.json()["events"])
    if "pagination" in response.json() and "continuation" in response.json()["pagination"]:
        continuation = response.json()["pagination"]["continuation"]
        response = requests.get(events_url.format(organization_id=organization_id), headers=headers, params={"continuation": continuation})
    else:
        break
events = [obj for obj in events if obj.get("series_id") == "511371103737"]
current_date = datetime.today().date()
for event in events:
    # Extract the event ID and name
    event_date = datetime.strptime(event["start"]["local"], '%Y-%m-%dT%H:%M:%S').date()
    
    if event_date > current_date:
        event_id = event["id"]
        event_name = event["name"]["text"]
      #  print(f"Attendees for '{event_name} of event ID'{event_id} occuring on {event_date}':")

        
    # Send the GET request to retrieve the attendees from Eventbrite
    attendees_url = f"https://www.eventbriteapi.com/v3/events/{event_id}/attendees/"
    attendees = []
    response = requests.get(attendees_url, headers=headers)
    while response.status_code == 200:
        attendees.extend(response.json()["attendees"])
        if "pagination" in response.json() and "continuation" in response.json()["pagination"]:
            continuation = response.json()["pagination"]["continuation"]
            response = requests.get(attendees_url, headers=headers, params={"continuation": continuation})
        else:
            break
            
    for attendee in attendees:
        first_name = attendee["profile"]["first_name"]
        last_name = attendee["profile"]["last_name"]        
        email = attendee["profile"]["email"]
        phone = attendee["profile"]["cell_phone"]
        attendee_event_date = datetime.strptime(event["start"]["local"], '%Y-%m-%dT%H:%M:%S').date()
        print(f"- {first_name} {last_name} ({email}) ({phone}) - Event Date: {attendee_event_date}")
        