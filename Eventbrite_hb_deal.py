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

events = [obj for obj in events if obj.get("series_id") == os.getenv("eb_events_series_id")]
current_date = datetime.today().date()

events = [obj for obj in events if obj.get("series_id") == "511371103737"]
current_date = datetime.today().date()

# Set your Hubspot API endpoint and credentials
hubspot_url = "https://api.hubapi.com/contacts/v1/contact"
hubspot_deals_url = "https://api.hubapi.com/deals/v1/deal"
hubspot_token = os.getenv("hubspot_token1")
hubspot_headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {hubspot_token}"
}

# Get existing deals from Hubspot pipeline
pipeline_id = "default"
existing_deals = []
deals_url = f"{hubspot_deals_url}/paged?properties=dealname&properties=email&properties=dealstage&properties=date_attending&properties=dealtype&properties=hubspot_owner_id&properties=hs_lastmodifieddate&q=dealstage.pipeline={pipeline_id}"
params = {"limit": 100}
while True:
    response = requests.get(deals_url, headers=hubspot_headers, params=params)
    if response.status_code == 200:
        deals = response.json()["deals"]
        for deal in deals:
            deal_name = deal["properties"]["dealname"]["value"]
            deal_email = deal["properties"]["email"]["value"]
            deal_date = deal["properties"]["date_attending"]["value"]
            deal_id = deal["dealId"]
            existing_deals.append({"name": deal_name, "email": deal_email, "date": deal_date, "deal_id": deal_id})

        if not response.json()["hasMore"]:
            break
        else:
            params["offset"] = response.json()["offset"]
    else:
        print(f"Error retrieving deals: {response.text}")
        break

# Store the details of each existing deal
existing_deal_details = set()
for deal in existing_deals:
    deal_name = deal["name"]
    deal_email = deal["email"]
    deal_date = deal["date"]
    keyvalue = ""
    keyvalue += str(deal_name).replace(" ", "") + str(deal_email) + str(deal_date)
    if keyvalue in existing_deal_details:
        print("I found a duplicate", keyvalue)
    else:
        existing_deal_details.add(keyvalue)

# Create a new deal for each attendee if it doesn't already exist in Hubspot
# attendees = []
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

        # existing_deal_details[(deal_name, deal_email, deal_date)] = deal["deal_id"]

        # Create a new deal for each attendee if it doesn't already exist in Hubspot
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
            keyvalue = ""
            keyvalue += str(name).replace(" ", "") + str(email) + str(unix_timestamp)
            if keyvalue in existing_deal_details:
                print(f"Deal already exists for attendee {name} ({email})")
            else:
                # print(keyvalue)
                # Create the new deal
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
                        {
                            "name": "eventid",
                            "value": event_id
                        },
                        {
                            "value": "newbusiness",
                            "name": "dealtype"
                        }
                    ]
                }
                response = requests.post(hubspot_deals_url, headers=hubspot_headers, data=json.dumps(deal_payload))
                if response.status_code == 200:
                    print(f"Deal created for attendee {name} ({email})")
                else:
                    print(f"Error creating deal for attendee {name} ({email}): {response.text}")
                    print(response.content)

