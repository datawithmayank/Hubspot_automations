# This one is working

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
organization_id = os.getenv("eb_organization_id")
headers = {
    "Authorization": f"Bearer {eventbrite_token}"
}
events = []
response = requests.get(events_url.format(organization_id=organization_id), headers=headers)
while response.status_code == 200:
    events.extend(response.json()["events"])
    if "pagination" in response.json() and "continuation" in response.json()["pagination"]:
        continuation = response.json()["pagination"]["continuation"]
        response = requests.get(events_url.format(organization_id=organization_id), headers=headers,
                                params={"continuation": continuation})
    else:
        break
events = [obj for obj in events if obj.get("series_id") == "511371103737"]
current_date = datetime.today().date()

# Set your Hubspot API endpoint and credentials
hubspot_url = "https://api.hubapi.com/deals/v1/deal"
hubspot_token = os.getenv("hubspot_token1")
hubspot_headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {hubspot_token}"
}

for event in events:
    # Extract the event ID and name
    event_date = datetime.strptime(event["start"]["local"], '%Y-%m-%dT%H:%M:%S').date()

    if event_date > current_date:
        event_id = event["id"]
        event_name = event["name"]["text"]

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
            name = attendee["profile"]["name"]
            email = attendee["profile"]["email"]
            phone = attendee["profile"]["cell_phone"]
            # Convert date string to datetime object in UTC
            date_string = event["start"]["utc"]
            date_object = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%SZ')
            date_object = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%SZ').replace(hour=date_object.hour, minute=0,
                                                                                       second=0, microsecond=0)
            # date_object = datetime.strptime(date_string, '%Y-%m-%d')
            unix_timestamp = int(date_object.timestamp() - 24 * 60 * 60) * 1000

            # Create a new deal for the attendee
            deal_payload = {
                "associations": {
                    "associatedVids": [],
                    "associatedCompanyIds": [],
                    "associatedDealIds": []
                },
                "properties": [
                    {
                        "name": "dealname",
                        "value": name
                    },
                    {
                        "name": "dealstage",
                        "value": "appointmentscheduled"
                    },
                    {
                        "name": "date_attending",
                        "value": unix_timestamp
                    },
                    {
                        "name": "email",
                        "value": email
                    },
                ]
            }
            response = requests.post(hubspot_url, headers=hubspot_headers, data=json.dumps(deal_payload))
            if response.status_code == 200:
                print(f"Deal created for attendee {name} ({email})")
            else:
                print(f"Error creating deal for attendee {name} ({email}): {response.text}")

