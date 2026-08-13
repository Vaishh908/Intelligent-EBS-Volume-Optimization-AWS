import boto3
from datetime import datetime, timezone

dynamodb = boto3.resource("dynamodb")

TABLE_NAME = "EBS-Optimization-Logs"
table = dynamodb.Table(TABLE_NAME)


def lambda_handler(event, context):
    """
    Store the optimization result in DynamoDB.
    """
    volume_id = event["VolumeId"]

    item = {
        "VolumeId": volume_id,
        "InstanceId": event.get("InstanceId", "N/A"),
        "VolumeType": event.get("PreviousType", "gp2"),
        "NewVolumeType": event.get("NewType", "gp3"),
        "Size": event.get("Size", 0),
        "Region": event.get(
            "Region",
            boto3.session.Session().region_name
        ),
        "Timestamp": datetime.now(timezone.utc).isoformat(),
        "Status": event.get("Status", "COMPLETED")
    }

    table.put_item(Item=item)

    print(f"Optimization logged successfully: {item}")

    return {
        "VolumeId": volume_id,
        "LogStatus": "SUCCESS",
        "Item": item
    }
