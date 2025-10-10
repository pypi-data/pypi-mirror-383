# TokenResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**access_token** | **str** | The generated token. | [optional] 
**expires_in** | **float** | The number of seconds until the token expires. | [optional] 
**jti** | **str** | A globally unique identifier for the token. | [optional] 
**scope** | **str** | A space-delimited list of scopes that the token can be used to access. | [optional] 
**token_type** | **str** | The type of token that was generated, i.e., &#x60;bearer&#x60;. | [optional] 

## Example

```python
from zuora_sdk.models.token_response import TokenResponse

# TODO update the JSON string below
json = "{}"
# create an instance of TokenResponse from a JSON string
token_response_instance = TokenResponse.from_json(json)
# print the JSON string representation of the object
print(TokenResponse.to_json())

# convert the object into a dict
token_response_dict = token_response_instance.to_dict()
# create an instance of TokenResponse from a dict
token_response_from_dict = TokenResponse.from_dict(token_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


