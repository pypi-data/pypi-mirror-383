# Installation

Use pip:

```
pip install py-msgraph
```
or

```
pip install git+https://github.com/shineum/py_msgraph.git
```


# Prerequisite
To use MS graph API, MS application is necessary and tenant_id, client_id and client_secret are prepared.
It is needed to assign the permissions in the MS application depending on the APIs.

Here are reference URLs.
```
# Set up a Tenant
https://learn.microsoft.com/en-us/azure/active-directory/develop/quickstart-create-new-tenant

# Register an application
https://learn.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app

# Graph API Permissions
https://learn.microsoft.com/en-us/graph/permissions-reference
```


# Getting Started
Initialize MSGraphServiceClient instance.

```
from py_msgraph import MSGraphServiceClient

config = {
    'tenant_id':      '<tentant_id>',
    'client_id':      '<client_id>',
    'client_secret':  '<client_secret>'
}

client: MSGraphServiceClient = MSGraphServiceClient(config)
```

# Usages

### Get data
To get data, use "get_data" method or "get_data_raw" method.

```
json_data = client.get_data('<api_name>', '<options - optional>', '<version: api version - optional>')
raw_response = client.get_data_raw('<api_name>', '<options - optional>', '<version: api version - optional>')
```

ex)
```
data = client.get_data('users', {'$filter': "userPrincipalName eq 'youremail@yourdomain.com'", '$select': 'id'})
print(data)

user_email = "youremail@yourdomain.com"
raw_response = client.get_data_raw(f"/users/{user_email}/photo/$value")
res_body = raw_response.content
```

### Post request
To send post request, use "post_data" method.

```
result = client.post_data('<api_name>', '<data: request body - optional>', '<headers: headers - optional>', '<version: api version - optional>', '<files: attachment - optional>')
```

ex)
```
user_id = "<user guid>"
group_id = "<group guid>"
req_body = {
    "@odata.id": f"https://graph.microsoft.com/v1.0/users/{user_id}"
}
result = client.post_data(f"groups/{group_id}/members/$ref", req_body)
print(result)
```

### Others
This library also support put, patch and delete methods.

```
result = client.put_data('<api_name>', '<data: request body - optional>', '<headers: headers - optional>', '<version: api version - optional>', '<files: attachment - optional>')

result = client.patch_data('<api_name>', '<data: request body - optional>', '<headers: headers - optional>', '<version: api version - optional>', '<files: attachment - optional>')

result = client.delete_data('<api_name>', '<data: request body - optional>', '<headers: headers - optional>', '<version: api version - optional>', '<files: attachment - optional>')
```


