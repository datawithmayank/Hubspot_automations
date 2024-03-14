# Hubspot_automations

This is under development but doing the core job of:
- Fetching the attendee's details from Eventbrite and creating a contact in Hubspot (Hubspot_eventbrite.py)
- Fetching the attendee's details and creating a unique deal for every sign-up instance that is unique on Name, Email, and date_attending (Eventbrite_hb_deal.py)
- Associating the deal and contact based on email (deal_contact_association.py)

You need to set up a .env file locally with the following token variables
- hubspot_token1 - Your HubSpot private app token
- eventbrite_token1 - Your Eventbrite API key
- eb_events_series_id - Series ID of the event you want to fetch the attendees from Eventbrite.
- eb_organization_id - Organization ID under which events are announced on Eventbrite.
