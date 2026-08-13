import boto3

ec2 = boto3.client("ec2")


def lambda_handler(event, context):
    """
    Convert one eligible EBS volume from gp2 to gp3.
    """
    volume_id = event["VolumeId"]

    response = ec2.describe_volumes(VolumeIds=[volume_id])
    volume = response["Volumes"][0]

    current_type = volume["VolumeType"]
    size = volume["Size"]

    print(f"Volume ID: {volume_id}")
    print(f"Current Type: {current_type}")
    print(f"Size: {size} GiB")

    if current_type != "gp2":
        return {
            "VolumeId": volume_id,
            "PreviousType": current_type,
            "NewType": current_type,
            "Size": size,
            "Status": "SKIPPED",
            "Message": "Volume is not gp2"
        }

    print(f"Starting conversion: {volume_id} gp2 -> gp3")

    ec2.modify_volume(
        VolumeId=volume_id,
        VolumeType="gp3"
    )

    return {
        "VolumeId": volume_id,
        "PreviousType": "gp2",
        "NewType": "gp3",
        "Size": size,
        "Region": boto3.session.Session().region_name,
        "Status": "MODIFICATION_STARTED"
    }
