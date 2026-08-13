import boto3

ec2 = boto3.client("ec2")


def lambda_handler(event, context):
    """
    Check the EBS volume modification status.
    """
    volume_id = event["VolumeId"]

    response = ec2.describe_volume_modifications(
        VolumeIds=[volume_id]
    )

    modifications = response.get("VolumesModifications", [])

    if not modifications:
        return {
            "VolumeId": volume_id,
            "ModificationState": "NOT_FOUND",
            "Status": "ERROR"
        }

    modification = modifications[0]
    state = modification["ModificationState"]

    print(f"Volume ID: {volume_id}")
    print(f"Modification State: {state}")

    if state == "completed":
        status = "COMPLETED"
    elif state == "failed":
        status = "FAILED"
    else:
        status = "IN_PROGRESS"

    return {
        "VolumeId": volume_id,
        "ModificationState": state,
        "Status": status,
        "TargetType": modification.get("TargetVolumeType", "gp3"),
        "Progress": modification.get("Progress", 0)
    }
