import boto3

ec2 = boto3.client("ec2")


def lambda_handler(event, context):
    """
    Find EBS volumes that are:
      1. gp2
      2. Tagged AutoConvert=true
    """
    response = ec2.describe_volumes()

    eligible_volumes = []

    for volume in response.get("Volumes", []):
        tags = {
            tag["Key"]: tag["Value"]
            for tag in volume.get("Tags", [])
        }

        if volume.get("VolumeType") == "gp2" and tags.get("AutoConvert", "").lower() == "true":
            attachments = volume.get("Attachments", [])
            instance_id = attachments[0].get("InstanceId", "N/A") if attachments else "N/A"

            eligible_volumes.append({
                "VolumeId": volume["VolumeId"],
                "InstanceId": instance_id,
                "VolumeType": volume["VolumeType"],
                "Size": volume["Size"],
                "Region": boto3.session.Session().region_name
            })

    print(f"Eligible volumes found: {len(eligible_volumes)}")
    print(f"Eligible volumes: {eligible_volumes}")

    return {
        "Volumes": eligible_volumes,
        "Count": len(eligible_volumes)
    }
