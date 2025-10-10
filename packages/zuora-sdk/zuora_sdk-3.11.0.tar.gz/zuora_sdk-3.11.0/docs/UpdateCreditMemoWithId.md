# UpdateCreditMemoWithId


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**auto_apply_upon_posting** | **bool** | Whether the credit memo automatically applies to the invoice upon posting. | [optional] 
**comment** | **str** | Comments about the credit memo. | [optional] 
**effective_date** | **date** | The date when the credit memo takes effect. | [optional] 
**exclude_from_auto_apply_rules** | **bool** | Whether the credit memo is excluded from the rule of automatically applying unapplied credit memos to invoices and debit memos during payment runs. If you set this field to &#x60;true&#x60;, a payment run does not pick up this credit memo or apply it to other invoices or debit memos. | [optional] 
**items** | [**List[UpdateCreditMemoItem]**](UpdateCreditMemoItem.md) | Container for credit memo items. | [optional] 
**reason_code** | **str** | A code identifying the reason for the transaction. The value must be an existing reason code or empty. If you do not specify a value, Zuora uses the default reason code. | [optional] 
**transferred_to_accounting** | [**TransferredToAccountingStatus**](TransferredToAccountingStatus.md) |  | [optional] 
**integration_id__ns** | **str** | ID of the corresponding object in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**integration_status__ns** | **str** | Status of the credit memo&#39;s synchronization with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**origin__ns** | **str** | Origin of the corresponding object in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**sync_date__ns** | **str** | Date when the credit memo was synchronized with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**transaction__ns** | **str** | Related transaction in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**id** | **str** | The ID of the credit memo.  | [optional] 

## Example

```python
from zuora_sdk.models.update_credit_memo_with_id import UpdateCreditMemoWithId

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateCreditMemoWithId from a JSON string
update_credit_memo_with_id_instance = UpdateCreditMemoWithId.from_json(json)
# print the JSON string representation of the object
print(UpdateCreditMemoWithId.to_json())

# convert the object into a dict
update_credit_memo_with_id_dict = update_credit_memo_with_id_instance.to_dict()
# create an instance of UpdateCreditMemoWithId from a dict
update_credit_memo_with_id_from_dict = UpdateCreditMemoWithId.from_dict(update_credit_memo_with_id_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


