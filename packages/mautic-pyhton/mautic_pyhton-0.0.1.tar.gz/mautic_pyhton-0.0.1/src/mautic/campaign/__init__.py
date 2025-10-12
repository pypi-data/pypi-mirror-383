class Campaign:
       def __init__(self, client):
              self.client = client

       def __str__(self):
              return ''

       def __repr__(self):
              return ''
       
       def addContact(self, campaignId, contactId, **kwargs):
              return self.client.create(f"campaigns/{campaignId}/contact/{contactId}/add", {"contactId": contactId})
       
       def removeContact(self, campaignId, contactId, **kwargs):
              return self.client.create(f"campaigns/{campaignId}/contacts/{contactId}/remove")