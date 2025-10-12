
class Segment:
       def __init__(self, client):
              self.client = client

       def __str__(self):
              return ''

       def __repr__(self):
              return ''
       
       def get(self, **kwargs):
              valid_params = {
                     "search": None,
                     "start": None,
                     "limit": None,
                     "orderBy": None,
                     "orderByDir": None,
                     "publishedonly": None,
              }
              new_params = {k: v for k, v in kwargs.items() if k in valid_params and v is not None}

              if kwargs.get("where") is not None:
                     new_params["where"] = kwargs.get("where")
              return self.client.get("segments", kwargs)
       
       def getById(self, id, **kwargs):
              return self.client.get(f"segments/{id}", kwargs)
       
       def create(self, data, **kwargs):
              return self.client.create("segments/new", data)
       
       def update(self, id, data, **kwargs):
              return self.client.patch(f"segments/{id}/edit", data)
       
       def delete(self, id, **kwargs):
              return self.client.delete(f"segments/{id}")
       

       def addContact(self, segmentId, contactId, **kwargs):
              return self.client.create(f"segments/{segmentId}/contact/{contactId}/add", {"contactId": contactId})
       
       def addContacts(self, segmentId, data, **kwargs):
              return self.client.create(f"segments/{segmentId}/contacts/add", data)

       def removeContact(self, segmentId, contactId, **kwargs):
              return self.client.create(f"segments/{segmentId}/contacts/{contactId}/remove")