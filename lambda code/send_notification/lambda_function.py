import os
import boto3

sns = boto3.client("sns")

TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN")


def lambda_handler(event, context):
    """
    Send the EBS optimization result through SNS.
    """
    if not TOPIC_ARN:
        raise ValueError("SNS_TOPIC_ARN environment variable is not configured")

    volume_id = event["VolumeId"]
    previous_type = event.get("PreviousType", "gp2")
    new_type = event.get("NewType", "gp3")
    status = event.get("Status", "COMPLETED")
    region = event.get(
        "Region",
        boto3.session.Session().region_name
    )
    progress = event.get("Progress", 100)

    subject = "EBS Volume Converted"

    message = f"""EBS Volume Optimization Result

Volume ID: {volume_id}
Region: {region}
Previous Type: {previous_type}
New Type: {new_type}
Status: {status}
Progress: {progress}%

The EBS volume optimization workflow has completed.
"""

    response = sns.publish(
        TopicArn=TOPIC_ARN,
        Subject=subject,
        Message=message
    )

    print(f"SNS notification sent. MessageId: {response['MessageId']}")

    return {
        "VolumeId": volume_id,
        "NotificationStatus": "SENT",
        "MessageId": response["MessageId"]
    }
