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
        response = requests.get(events_url.format(organization_id=organization_id), headers=headers,
                                params={"continuation": continuation})
    else:
        break
events = [obj for obj in events if obj.get("series_id") == "511371103737"]
current_date = datetime.today().date()

# Set your Hubspot API endpoint and credentials
hubspot_url = "https://api.hubapi.com/contacts/v1/contact"
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
            email = attendee["profile"]["email"]
            phone = attendee["profile"]["cell_phone"]
            unique_id = attendee["id"]
            attendee_event_date = datetime.strptime(event["start"]["local"], '%Y-%m-%dT%H:%M:%S').date()
            #print(f"- {first_name} {last_name} ({email}) ({phone}) Date: {attendee_event_date} and id: {unique_id}")

                    # Check if the contact exists in Hubspot
            contact_payload = {
                "properties": [
                    {
                        "property": "email",
                        "value": email
                    },
                    {
                        "property": "firstname",
                        "value": first_name
                    },
                    {
                        "property": "lastname",
                        "value": last_name
                    },
                    {
                        "property": "phone",
                        "value": phone
                    }
                ]
            }

            response = requests.post(hubspot_url, headers=hubspot_headers, json=contact_payload)

            if response.status_code == 200:
                print(f"Contact {first_name} {last_name} ({email}) has been updated in Hubspot.")
            else:
                print(f"Error updating contact {first_name} {last_name} ({email}) in Hubspot.")
                print(response.content)

        else:
            # Contact does not exist, create a new one
            contact_payload = {
                "properties": [
                    {
                        "property": "email",
                        "value": email
                    },
                    {
                        "property": "firstname",
                        "value": first_name
                    },
                    {
                        "property": "lastname",
                        "value": last_name
                    },
                    {
                        "property": "phone",
                        "value": phone
                    }
                ]
            }

            response = requests.post(hubspot_url, headers=hubspot_headers, json=contact_payload)

            if response.status_code == 200:
                print(f"Contact {first_name} {last_name} ({email}) has been created in Hubspot.")
            else:
                print(f"Error creating contact {first_name} {last_name} ({email}) in Hubspot.")
                print(response.content)
