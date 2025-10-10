"""msgraph lib"""
#  @author  Sungwon Um
#  @version 0.0.4

import requests
import json
from datetime import datetime
from urllib.parse import urlencode, quote_plus


class MSGraphServiceClient:
    __token_url = None
    __token_data = None
    __token_value = None
    __token_expires_on = 0
        
    @property
    def api_base(self):
        return 'https://graph.microsoft.com'
    
    def __init__(self, config):
        tenant_id = config.get('tenant_id', None)
        client_id = config.get('client_id', None)
        client_secret = config.get('client_secret', None)
        
        self.__token_url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/token'
        self.__token_data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'resource': self.api_base,
            'scope':self.api_base,
        }
        
    def __get_token(self):
        current_ts = datetime.now().timestamp()
        is_expired = current_ts > self.__token_expires_on
        if is_expired and self.__token_url:
            token_data_json = requests.post(self.__token_url, data=self.__token_data).json()
            self.__token_value = token_data_json.get('access_token')
            self.__token_expires_on = int(token_data_json.get('expires_on', 0)) - 10
        return self.__token_value

    def get_data_raw(self, resource, params={}, headers={}, version="v1.0"):
        if resource.startswith(self.api_base):
            api_url = resource
        else:
            api_url = f'{self.api_base}/{version}/{resource}'
        req_headers = {
            'Authorization': f'Bearer {self.__get_token()}',
            'Content-type': 'application/json'
        }
        req_headers.update(headers)
        return requests.get(api_url, params=params, headers=req_headers)
    
    def get_data(self, resource, params={}, headers={}, version="v1.0"):
        return json.loads(self.get_data_raw(resource, params, headers, version).text)
    
    def __execute_raw(self, method, resource, data={}, headers={}, version="v1.0", files=None):
        if resource.startswith(self.api_base):
            api_url = resource
        else:
            api_url = f'{self.api_base}/{version}/{resource}'        
        req_headers = {
            'Authorization': f'Bearer {self.__get_token()}',
            'Content-type': 'application/json'
        }
        req_headers.update(headers)
        try:
            execute_method = getattr(requests, method)
            return execute_method(api_url, data=json.dumps(data), files=files, headers=req_headers)
        except:
            pass
        return None
        
    def post_data_raw(self, resource, data={}, headers={}, version="v1.0", files=None):
        return self.__execute_raw("post", resource, data, headers, version, files)
    
    def put_data_raw(self, resource, data={}, headers={}, version="v1.0", files=None):
        return self.__execute_raw("put", resource, data, headers, version, files)
    
    def patch_data_raw(self, resource, data={}, headers={}, version="v1.0", files=None):
        return self.__execute_raw("patch", resource, data, headers, version, files)

    def delete_data_raw(self, resource, data={}, headers={}, version="v1.0", files=None):
        return self.__execute_raw("delete", resource, data, headers, version, files)
    
    def __execute(self, method, resource, data={}, headers={}, version="v1.0", files=None):
        try:
            return json.loads(self.__execute_raw(method, resource, data, headers, version, files).text)
        except:
            pass
        return {}

    def post_data(self, resource, data={}, headers={}, version="v1.0", files=None):
        return self.__execute("post", resource, data, headers, version, files)
    
    def put_data(self, resource, data={}, headers={}, version="v1.0", files=None):
        return self.__execute("put", resource, data, headers, version, files)
    
    def patch_data(self, resource, data={}, headers={}, version="v1.0", files=None):
        return self.__execute("patch", resource, data, headers, version, files)

    def delete_data(self, resource, data={}, headers={}, version="v1.0", files=None):
        return self.__execute("delete", resource, data, headers, version, files)
