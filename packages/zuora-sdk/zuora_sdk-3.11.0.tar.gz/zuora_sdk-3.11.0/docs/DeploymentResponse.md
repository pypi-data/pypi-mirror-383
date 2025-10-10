# DeploymentResponse

Response when deployment is started.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Variable to hold the job ID. | 
**status** | **str** | Status of the Deployment Job. | 

## Example

```python
from zuora_sdk.models.deployment_response import DeploymentResponse

# TODO update the JSON string below
json = "{}"
# create an instance of DeploymentResponse from a JSON string
deployment_response_instance = DeploymentResponse.from_json(json)
# print the JSON string representation of the object
print(DeploymentResponse.to_json())

# convert the object into a dict
deployment_response_dict = deployment_response_instance.to_dict()
# create an instance of DeploymentResponse from a dict
deployment_response_from_dict = DeploymentResponse.from_dict(deployment_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


