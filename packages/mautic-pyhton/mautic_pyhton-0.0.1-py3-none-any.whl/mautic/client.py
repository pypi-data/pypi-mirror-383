import base64
from .contact import Contact
import requests
from .segment import Segment

class Client(object):
    """
    A client for Mautic API
    """

    auth_header = None
    base_url = None
    version = None
    verify = False

    def __init__(self,  base_url ):        
        self.base_url = base_url + "/api/"

    def basic_auth(self, username, password):
        encoded_credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
        self.auth_header =  { "Authorization": f"Basic {encoded_credentials}" }
        return self
    
    def get_response(self, method, endpoint, data={}):
        url = self.base_url + endpoint
        response = requests.request(
            method, 
            url, 
            headers= {**self.auth_header, **{
                "Accept": "application/json"
            }}, 
            json=data,
            verify=self.verify
            )

        response.raise_for_status()
        return response.json()


    def generateQueryStringForWheres(self, fitlers):
        return "&".join(
            [f"where[{i}][col]={f['col']}&where[{i}][expr]={f['expr']}&where[{i}][val]={f['val']}" for i, f in enumerate(fitlers)]
        )
    @property
    def contact(self):
        return Contact(self)
    @property
    def segment(self):
        return Segment(self)
    def get(self, endpoint, params=None):
        url = endpoint
        whereString = ""
        where = params.pop("where", None)
        if where is not None:
            whereString = self.generateQueryStringForWheres(where)
        url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])
        url += whereString
        return self.get_response("GET", url)
    
    def create(self, endpoint, data=None):
        return self.get_response("POST", endpoint, data)
    
    def post(self, endpoint, data=None):
        return self.get_response("POST", endpoint, data)
    
    def patch(self, endpoint, data=None):
        return self.get_response("PATCH", endpoint, data)
    def put(self, endpoint, data=None):
        return self.get_response("PUT", endpoint, data)
    
    def delete(self, endpoint, data=None):
        return self.get_response("DELETE", endpoint, data)