import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

# Set the Hubspot API endpoint and credentials
hubspot_url = "https://api.hubapi.com/deals/v1/deal"
hubspot_token = os.getenv("hubspot_token1")
hubspot_headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {hubspot_token}"
}

# Get all the deals from Hubspot
deals_url = "https://api.hubapi.com/deals/v1/deal/paged"
deals = []
params = {"limit": 100}
while True:
    response = requests.get(deals_url, headers=hubspot_headers, params=params)
    if response.status_code == 200:
        deals = response.json()
        if not response.json()["hasMore"]:
            break
        else:
            params["offset"] = response.json()["offset"]
    else:
        print(f"Error retrieving deals: {response.text}")
        break

# Get all the contacts from Hubspot
contacts_url = "https://api.hubapi.com/contacts/v1/lists/all/contacts/all"
contacts = []
params = {"count": 100}
while True:
    response = requests.get(contacts_url, headers=hubspot_headers, params=params)
    if response.status_code == 200:
        contacts.extend(response.json()["contacts"])
        if not response.json()["has-more"]:
            break
        else:
            params["vidOffset"] = response.json()["vid-offset"]
    else:
        print(f"Error retrieving contacts: {response.text}")
        break

# Create a dictionary of contacts indexed by email
email_to_contact = {}
for contact in contacts:
    email = contact["identity-profiles"][0]["identities"][0]["value"]
    email_to_contact[email] = contact["vid"]

# Associate each deal with the corresponding contact using email property
# Associate each deal with the corresponding contact using email property
for deal in deals["deals"]:
    deal_id = deal["dealId"]
    deal_url = f"https://api.hubapi.com/deals/v1/deal/{deal_id}"
    response = requests.get(deal_url, headers=hubspot_headers)
    if response.status_code == 200:
        deal_properties = response.json()["properties"]
        deal_email = deal_properties.get("email", {}).get("value", "")
        if deal_email in email_to_contact:
            contact_id = email_to_contact[deal_email]
            associations_url = f"https://api.hubapi.com/crm/v4/objects/contacts/{contact_id}/associations/default/deals/{deal_id}"
            response = requests.put(associations_url, headers=hubspot_headers)
            if response.status_code == 200:
                print(f"Associated deal {deal_id} with email {deal_email} with contact {contact_id}")
            else:
                print(f"Error associating deal {deal_id} with email {deal_email} with contact {contact_id}")

        else:
            print(f"No contact found with email {deal_email} for deal {deal_id}")
    else:
        print(f"Error retrieving properties for deal {deal_id}: {response.text}")
