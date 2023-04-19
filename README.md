# Hubspot_automations

This is under development but doing the core job of:
- Fetching the attendees details from Eventbrite and creating a contact in Hubspot (Hubspot_eventbrite.py)
- Fetiching the attendees details and creating a unique deal for every sign up instance by that is unique on Name, Email and date_attending (Eventbrite_hb_deal.py)
- Associating the deal and contact based on email

You need to set up a .env file locally with following token variables
- hubspot_token1 - Your hubspot private app token
- eventbrite_token1 - Your eventbrite API key
- eb_events_series_id - Series ID of the event you want to fetch the attendees from Eventbrite.
- eb_organization_id - Organization ID under which events are announced on Eventbrite.
