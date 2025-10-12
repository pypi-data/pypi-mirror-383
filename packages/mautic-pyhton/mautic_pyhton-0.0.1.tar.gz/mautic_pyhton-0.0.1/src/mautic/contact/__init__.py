class Contact:
       supported_expressions = [
              "eq",
              "neq",
              "lt",
              "lte",
              "gt",
              "gte"
       ]
       def __init__(self, client):
              self.client = client

       def __str__(self):
              return ''
       

       def __repr__(self):
              return ''
       
       def get(self, **kwargs):
              valid_params = {
                  "search": None,
                  "searchcommand": None,
                  "start": None,
                  "limit": None,
                  "orderBy": None,
                  "orderByDir": None,
                  "publishedOnly": None,
                  "minimal": None,
              }
              new_params = {k: v for k, v in kwargs.items() if k in valid_params and v is not None}

              if kwargs.get("where") is not None:
                  new_params["where"] = kwargs.get("where")

              return self.client.get("contacts", new_params)
       
       def getById(self, id, **kwargs):
              return self.client.get(f"contacts/{id}", kwargs)
       def create(self, data, **kwargs):
              data = {k: v for k, v in data.items() if v is not None}
              return self.client.create("contacts/new", data)

       def createBatch(self, data, **kwargs):
              data = [ { k: v for k, v in item.items() if v is not None} for item in data ]
              return self.client.create("contacts/batch/new", data)
       
       def update(self, id, data, **kwargs):
              data = {k: v for k, v in data.items() if v is not None}
              return self.client.patch(f"contacts/{id}/edit", data)
       
       def updateBatch(self, data, **kwargs):
              data = [ { k: v for k, v in item.items() if v is not None} for item in data ]
              return self.client.patch(" contacts/batch/edit", data)
       
       def delete(self, id, **kwargs):
              return self.client.delete(f"contacts/batch/delete?id={id}")
       
       def deleteBatch(self, data, **kwargs):
              return self.client.delete(f"contacts/batch/delete?ids={','.join(map(str, data))}")