# Intelligent EBS Volume Optimization Using Lambda, CloudWatch, SNS, DynamoDB & Step Functions

---

# Project Description

Intelligent EBS Volume Optimization is a serverless AWS automation project designed to automatically identify and optimize Amazon EBS volumes. The solution scans EBS volumes, identifies volumes using the older `gp2` volume type with the tag `AutoConvert=true`, and automatically converts eligible volumes to the more efficient `gp3` volume type.

The workflow uses Amazon EventBridge, AWS Step Functions, AWS Lambda, Amazon DynamoDB, Amazon SNS, Amazon CloudWatch, and AWS IAM. EventBridge triggers the workflow on a schedule, while Step Functions orchestrates the complete optimization process. Lambda functions perform volume filtering, conversion, verification, logging, and notification tasks.

The project also maintains an audit trail in DynamoDB and sends an SNS notification after the optimization process is completed successfully. CloudWatch Logs provide visibility into Lambda execution and help monitor and troubleshoot the workflow.

---

# Prerequisites

Before implementing the project, ensure that the following requirements are available:

- AWS account
- AWS Management Console access
- Basic knowledge of AWS services
- Basic knowledge of Python
- Basic knowledge of IAM
- Basic knowledge of Amazon EC2 and EBS
- Basic understanding of serverless architecture

---

# Architecture Diagram

<img width="1536" height="1024" alt="Architecture Diagram" src="https://github.com/user-attachments/assets/1b13276e-26f6-453d-b986-9943713109fc" />

---

# AWS Permissions

The IAM roles used by the project should follow the principle of least privilege and provide only the permissions required by each AWS service.

The project requires access to:

- Amazon EC2
- Amazon EBS
- AWS Lambda
- AWS Step Functions
- Amazon EventBridge
- Amazon DynamoDB
- Amazon SNS
- Amazon CloudWatch
- AWS IAM

Lambda functions require permissions for:

- Describing EBS volumes
- Modifying EBS volumes
- Checking EBS volume modification status
- Writing CloudWatch Logs
- Writing records to DynamoDB
- Publishing messages to SNS

Step Functions requires permission to invoke the required Lambda functions.

EventBridge requires permission to start the Step Functions state machine.

---

# Technologies Used

| Technology | Purpose |
|------------|---------|
| Amazon EC2 | Provides the test environment and attached EBS volume |
| Amazon EBS | Storage volume targeted for optimization |
| AWS Lambda | Performs filtering, conversion, verification, logging, and notification |
| AWS Step Functions | Orchestrates the complete optimization workflow |
| Amazon EventBridge | Triggers the workflow on a schedule |
| Amazon DynamoDB | Stores optimization history and audit records |
| Amazon SNS | Sends optimization result notifications |
| Amazon CloudWatch | Provides Lambda logs and monitoring |
| AWS IAM | Provides controlled access to AWS resources |
| Python | Lambda function development |
| Boto3 | AWS SDK for Python |

---

# Installation Steps

This project uses AWS managed services and does not require local software installation. The installation phase prepares the AWS resources required by the automation workflow.

## Step 1: Prepare the AWS Account

Sign in to the AWS Management Console.

Select the project region:

Region:
us-east-1

Verify access to the following services:

- Amazon EC2
- Amazon EBS
- AWS Lambda
- AWS Step Functions
- Amazon EventBridge
- Amazon DynamoDB
- Amazon SNS
- Amazon CloudWatch
- AWS IAM

---

# Step 2: Create the EC2 Instance

Navigate to:

EC2 → Instances → Launch Instance

Launch a Linux-based EC2 instance.

Example configuration:

Instance Type:
t3.micro


Region:
us-east-1

- Ensure that the instance uses Amazon EBS storage.

- Launch the instance and verify that it is in the Running state.

- The EC2 instance provides the EBS volume used for the optimization test.

---

 # Step 3: Prepare the EBS Volume

Navigate to:

EC2 → Elastic Block Store → Volumes

Select the EBS volume attached to the EC2 instance.

Verify that the volume type is:

Volume Type:
gp2

Record the Volume ID.

Example:

Volume ID:
vol-005cf3aa1e84e4838

Select:

Actions → Manage tags

Add:

Key:
AutoConvert


Value:
true

The Lambda filtering function uses this tag to identify volumes eligible for automatic conversion.

A volume is eligible only when both conditions are satisfied:

Volume Type = gp2
AND
AutoConvert = true

---

# Step 4: Create DynamoDB Table

Navigate to:

DynamoDB → Tables → Create table

Create:

Table Name:
EBS-Optimization-Logs

Configure:

Partition Key:
VolumeId


Data Type:
String

Create the table and verify that its status is Active.

The table is used to maintain an audit trail of EBS optimization operations.

---

# Step 5: Create SNS Topic

Navigate to:

Amazon SNS → Topics → Create topic

Select:

Type:
Standard

Create:

EBS-Volume-Optimization-Notifications

The topic is used to send optimization results.

---

# Step 6: Create SNS Email Subscription

Open:

EBS-Volume-Optimization-Notifications

Select:

Create subscription

Configure:

Protocol:
- Email


Endpoint:
your-email@example.com

Create the subscription.

- Open the confirmation email received from Amazon SNS and confirm the subscription.

- The confirmed subscription will receive the final optimization result.

---

# Step 7: Create IAM Roles

Create the required IAM roles for the Lambda functions and Step Functions.

For Lambda:

Trusted Entity:
- AWS Service


Use Case:
- Lambda

The Lambda execution role should provide only the required permissions for:

- EC2/EBS operations
- CloudWatch Logs
- DynamoDB
- SNS

For Step Functions, create or configure a role that allows the state machine to invoke the required Lambda functions.

For EventBridge, configure permission to start the Step Functions state machine.

Avoid using AdministratorAccess for the project.

---

# Step 8: Verify the Initial Environment

Before implementing the automation workflow, verify that the following resources are available:

- Resource	Configuration
- EC2 Instance	Linux t3.micro
- EBS Volume	gp2
- EBS Tag	AutoConvert=true
- DynamoDB Table	EBS-Optimization-Logs
- SNS Topic	EBS-Volume-Optimization-Notifications
- SNS Subscription	Confirmed
- IAM Roles	Lambda and Step Functions roles
- AWS Region	us-east-1

After completing the preparation steps, proceed to the implementation phase.

---

# Project Structure

````text
Intelligent-EBS-Volume-Optimization/
│
├── README.md
│
├── architecture/
│   └── architecture-diagram.png
│
├── lambda/
│   ├── filter_volumes/
│   │   └── lambda_function.py
│   │
│   ├── convert_volume/
│   │   └── lambda_function.py
│   │
│   ├── verify_volume/
│   │   └── lambda_function.py
│   │
│   ├── log_optimization/
│   │   └── lambda_function.py
│   │
│   └── send_notification/
│       └── lambda_function.py
│
├── step-functions/
│   └── state-machine.json
│
├── screenshots/
│   ├── 01-ec2-volume.png
│   ├── 02-volume-tag.png
│   ├── 03-dynamodb-table.png
│   ├── 04-sns-topic.png
│   ├── 05-lambda-functions.png
│   ├── 06-step-function.png
│   ├── 07-step-function-execution.png
│   ├── 08-cloudwatch-logs.png
│   ├── 09-dynamodb-log-entry.png
│   ├── 10-sns-notification.png
│   └── 11-gp3-volume.png
│
└── docs/
    └── technical-report.pdf
````

---

# Implementation Steps

# Step 1: Create the Filter Lambda

Navigate to:

AWS Lambda → Functions → Create function

Create:

Function Name:
EBS-Filter-Volumes


Runtime:
Python 3.x

The function scans EBS volumes and identifies volumes satisfying:

VolumeType = gp2
AutoConvert = true

Example:

import boto3


ec2 = boto3.client("ec2")




def lambda_handler(event, context):


    response = ec2.describe_volumes()


    eligible_volumes = []


    for volume in response["Volumes"]:


        tags = {
            tag["Key"]: tag["Value"]
            for tag in volume.get("Tags", [])
        }


        if (
            volume["VolumeType"] == "gp2"
            and tags.get("AutoConvert") == "true"
        ):


            eligible_volumes.append({
                "VolumeId": volume["VolumeId"],
                "PreviousType": volume["VolumeType"],
                "Size": volume["Size"],
                "Region": boto3.session.Session().region_name
            })


    print("Eligible volumes:", eligible_volumes)


    return {
        "Volumes": eligible_volumes
    }

The function returns the eligible volumes to Step Functions.

---

# Step 2: Create the Conversion Lambda

Create:

Function Name:
EBS-Convert-Volume

The function receives the Volume ID and starts the conversion from gp2 to gp3.

import boto3


ec2 = boto3.client("ec2")




def lambda_handler(event, context):


    volume_id = event["VolumeId"]


    response = ec2.describe_volumes(
        VolumeIds=[volume_id]
    )


    volume = response["Volumes"][0]


    current_type = volume["VolumeType"]
    size = volume["Size"]


    print(f"Volume ID: {volume_id}")
    print(f"Current Type: {current_type}")
    print(f"Size: {size} GB")


    if current_type != "gp2":
        return {
            "VolumeId": volume_id,
            "Status": "SKIPPED",
            "Message": "Volume is not gp2"
        }


    ec2.modify_volume(
        VolumeId=volume_id,
        VolumeType="gp3"
    )


    print(f"Conversion started for {volume_id}")


    return {
        "VolumeId": volume_id,
        "PreviousType": "gp2",
        "NewType": "gp3",
        "Size": size,
        "Status": "MODIFICATION_STARTED"
    }

 ---

# Step 3: Create the Verification Lambda

Create:

Function Name:
EBS-Verify-Volume

The function checks the EBS modification status.

import boto3


ec2 = boto3.client("ec2")




def lambda_handler(event, context):


    volume_id = event["VolumeId"]


    response = ec2.describe_volume_modifications(
        VolumeIds=[volume_id]
    )


    modifications = response.get("VolumesModifications", [])


    if not modifications:
        return {
            "VolumeId": volume_id,
            "ModificationState": "unknown"
        }


    modification = modifications[0]


    state = modification["ModificationState"]


    print(f"Volume: {volume_id}")
    print(f"Modification State: {state}")


    return {
        "VolumeId": volume_id,
        "ModificationState": state,
        "PreviousType": event.get("PreviousType", "gp2"),
        "NewType": event.get("NewType", "gp3"),
        "Size": event.get("Size", 0)
    }

Possible modification states include:

modifying
optimizing
completed
failed

The Step Functions workflow waits and checks again until the modification reaches the required state.

---

# Step 4: Create the DynamoDB Logging Lambda

Create:

Function Name:
EBS-Log-Optimization

The function records the completed optimization in DynamoDB.

import boto3
from datetime import datetime, timezone


dynamodb = boto3.resource("dynamodb")


table = dynamodb.Table("EBS-Optimization-Logs")




def lambda_handler(event, context):


    volume_id = event["VolumeId"]


    item = {
        "VolumeId": volume_id,
        "InstanceId": event.get("InstanceId", "N/A"),
        "PreviousType": event.get("PreviousType", "gp2"),
        "NewType": event.get("NewType", "gp3"),
        "Size": event.get("Size", 0),
        "Region": boto3.session.Session().region_name,
        "Timestamp": datetime.now(timezone.utc).isoformat(),
        "Status": "COMPLETED"
    }


    table.put_item(Item=item)


    print("Optimization logged:", item)


    return {
        "VolumeId": volume_id,
        "LogStatus": "SUCCESS",
        "Status": "COMPLETED"
    }

---

# Step 5: Create the SNS Notification Lambda

Create:

Function Name:
EBS-Send-Notification

Configure the SNS topic ARN in the Lambda environment variable:

SNS_TOPIC_ARN

Example:

import boto3
import os


sns = boto3.client("sns")


TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]




def lambda_handler(event, context):


    volume_id = event["VolumeId"]


    message = f"""
EBS Volume Optimization Result


Volume ID: {volume_id}


Region: {boto3.session.Session().region_name}


Previous Type: {event.get("PreviousType", "gp2")}


New Type: {event.get("NewType", "gp3")}


Status: COMPLETED


The EBS volume optimization workflow has completed successfully.
"""


    sns.publish(
        TopicArn=TOPIC_ARN,
        Subject="EBS Volume Optimization Completed",
        Message=message
    )


    print("SNS notification sent")


    return {
        "VolumeId": volume_id,
        "NotificationStatus": "SENT"
    }

Using an environment variable avoids hard-coding the SNS topic ARN directly into the source code.

---

# Step 6: Create Step Functions State Machine

Navigate to:

AWS Step Functions → State machines → Create state machine

Select:

Workflow Type:
Standard

Step Functions coordinates the complete workflow.

The intended workflow is:

Start
  |
  v
Filter Volumes
  |
  v
Convert gp2 → gp3
  |
  v
Wait
  |
  v
Verify Modification
  |
  +---- modifying/optimizing ----+
  |                              |
  |                              v
  |                            Wait
  |                              |
  +------------------------------+
  |
  | completed
  v
Log to DynamoDB
  |
  v
Send SNS Notification
  |
  v
Success

---

# Step 7: Configure Step Functions Workflow

The state machine should contain the following logical states:

FilterVolumes
      ↓
ConvertVolumes
      ↓
WaitForModification
      ↓
VerifyVolume
      ↓
CheckModificationStatus
      ↓
LogOptimization
      ↓
SendNotification
      ↓
Success

The verification logic should ensure that:

ModificationState = completed

before the workflow continues to DynamoDB logging and SNS notification.

If the state is still:

modifying

or:

optimizing

the workflow should wait and verify again.

If the state is:

failed

the workflow should move to an error or failure state rather than sending a successful completion notification.

---

# Step 8: Create EventBridge Scheduled Rule

Navigate to:

Amazon EventBridge → Rules → Create rule

Create:

Rule Name:
EBS-Optimization-Daily

Configure a daily schedule.

Set the Step Functions state machine as the target.

EventBridge will automatically start the Step Functions workflow according to the configured schedule.

---

# Step 9: Configure CloudWatch Logs

AWS Lambda automatically sends execution logs to Amazon CloudWatch when the Lambda execution role includes the required logging permissions.

Navigate to:

CloudWatch → Logs → Log groups

Verify the Lambda log groups:

/aws/lambda/EBS-Filter-Volumes
/aws/lambda/EBS-Convert-Volume
/aws/lambda/EBS-Verify-Volume
/aws/lambda/EBS-Log-Optimization
/aws/lambda/EBS-Send-Notification

CloudWatch Logs can be used to verify:

Volume discovery
Current volume type
Conversion request
Modification status
DynamoDB logging
SNS notification
Errors

---

# Step 10: Test the Workflow

Before relying on the scheduled EventBridge rule, manually start the Step Functions execution.

Navigate to:

Step Functions → State Machines → EBS Volume Optimization

Select:

Start execution

Monitor each state.

Expected execution:

FilterVolumes
      ↓
ConvertVolumes
      ↓
WaitForModification
      ↓
VerifyVolume
      ↓
CheckModificationStatus
      ↓
LogOptimization
      ↓
SendNotification
      ↓
Success

The execution should finish with:

Status:
Succeeded

---

# Step 11: Verify EBS Conversion

Navigate to:

EC2 → Volumes

Select the optimized volume.

Verify:

Previous Type:
gp2


New Type:
gp3

The current volume type should be:

gp3

Example:

Volume ID:
vol-005cf3aa1e84e4838


Volume Type:
gp3

---

# Step 12: Verify DynamoDB Logs

Navigate to:

DynamoDB → EBS-Optimization-Logs → Explore table items

Verify that a record exists for the optimized volume.

Example:

VolumeId:
vol-005cf3aa1e84e4838


PreviousType:
gp2


NewType:
gp3


Size:
8


Region:
us-east-1


Status:
COMPLETED


Timestamp:
2026-08-13T...

This record provides an audit trail of the optimization operation.

---

# Step 13: Verify SNS Notification

Check the email subscription associated with the SNS topic.

A successful notification should contain:

EBS Volume Optimization Result


Volume ID: vol-005cf3aa1e84e4838


Region: us-east-1


Previous Type: gp2


New Type: gp3


Status: COMPLETED


The EBS volume optimization workflow has completed successfully.

---

# Step 14: Verify CloudWatch Logs

Open the CloudWatch log groups for the Lambda functions.

Verify messages similar to:

Checking volume: vol-005cf3aa1e84e4838


Current Type: gp2


Converting volume from gp2 to gp3


Modification State: completed


Optimization logged successfully


SNS notification sent

These logs confirm successful execution and provide information for troubleshooting.

---

# Results

The project successfully demonstrated an automated EBS volume optimization workflow using AWS serverless services. The system identified an EBS volume using the gp2 volume type and the AutoConvert=true tag and initiated its conversion to the gp3 volume type.

The Step Functions workflow coordinated the optimization process, including volume filtering, conversion, modification verification, DynamoDB logging, and SNS notification. The EBS volume was successfully converted from gp2 to gp3, and the workflow completed successfully.

The optimization activity was recorded in DynamoDB, providing an audit trail containing information such as the Volume ID, previous volume type, new volume type, size, Region, status, and timestamp. An SNS notification was also successfully generated after the optimization was completed. CloudWatch Logs provided execution details for monitoring and troubleshooting.

The successful test result was:

EBS Volume Optimization Result


Volume ID: vol-005cf3aa1e84e4838


Region: us-east-1


Previous Type: gp2


New Type: gp3


Status: COMPLETED


Progress: 100%

These results confirm that the automated EBS volume optimization workflow operated successfully from volume identification through final notification.

---

# Conclusion

The Intelligent EBS Volume Optimization project successfully demonstrated how AWS serverless services can be integrated to automate EBS storage optimization in a reliable and controlled manner. The solution automatically identified eligible gp2 EBS volumes using the AutoConvert=true tag and converted them to the more efficient gp3 volume type.

AWS Lambda performed the volume filtering, conversion, verification, logging, and notification tasks, while AWS Step Functions coordinated these operations into a structured workflow. Amazon EventBridge provided scheduled execution, DynamoDB maintained an audit trail of optimization activities, Amazon SNS delivered completion notifications, and Amazon CloudWatch provided monitoring and execution logs. AWS IAM provided controlled access to the required AWS resources.

The successful conversion of the EBS volume from gp2 to gp3, together with the successful Step Functions execution, DynamoDB audit record, SNS notification, and CloudWatch logs, demonstrated that the complete automation workflow operated as expected.

Overall, the project provided practical experience in serverless automation, event-driven architecture, AWS storage optimization, workflow orchestration, monitoring, notification systems, database logging, and IAM-based security. The solution demonstrates how repetitive infrastructure management tasks can be automated to reduce manual effort while maintaining visibility, auditability, reliability, and controlled access to cloud resources.
