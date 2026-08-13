# Intelligent EBS Volume Optimization Using Lambda, CloudWatch, SNS, DynamoDB & Step Functions

---

# Project Description

Intelligent EBS Volume Optimization is a serverless AWS automation project designed to automatically identify and optimize Amazon EBS volumes. The solution scans EBS volumes, identifies volumes using the older gp2 volume type with the tag `AutoConvert=true`, and automatically converts them to the more efficient gp3 volume type.

The workflow is completely automated using Amazon EventBridge, AWS Step Functions, AWS Lambda, Amazon DynamoDB, Amazon SNS, Amazon CloudWatch, and IAM. Step Functions orchestrates the complete workflow, while Lambda functions perform volume filtering, modification, verification, logging, and notification tasks.

The project also maintains an audit trail in DynamoDB and sends an SNS notification after the volume optimization process is completed. CloudWatch Logs are used to monitor Lambda execution and troubleshoot errors.

---

# Objective

The main objective of this project is to build a serverless automation pipeline that:

* Identifies EBS volumes using gp2
* Filters volumes using the `AutoConvert=true` tag
* Converts eligible gp2 volumes to gp3
* Verifies the modification status
* Stores conversion history in DynamoDB
* Sends notifications through SNS
* Uses Step Functions to orchestrate the workflow
* Uses EventBridge for scheduled execution
* Uses CloudWatch for monitoring and logging
* Implements IAM-based access control

---

# Prerequisites

Before implementing the project, the following requirements are needed:

* AWS account
* AWS Management Console access
* Basic knowledge of AWS services
* Basic knowledge of Python
* Basic knowledge of IAM
* Basic knowledge of Amazon EC2 and EBS
* Basic understanding of serverless architecture
  
---

# Architectural Diagram


<img width="1536" height="1024" alt="ChatGPT Image Aug 13, 2026, 06_47_57 PM" src="https://github.com/user-attachments/assets/1b13276e-26f6-453d-b986-9943713109fc" />

---

# AWS Permissions

The IAM roles used by the project should have only the permissions required for their specific tasks.

Required service access includes:

* Amazon EC2
* AWS Lambda
* Amazon EventBridge
* AWS Step Functions
* Amazon DynamoDB
* Amazon SNS
* Amazon CloudWatch
* IAM

---

# Technologies Used

| AWS Service        | Purpose                                |
| ------------------ | -------------------------------------- |
| Amazon EC2         | Hosts the EBS volumes                  |
| Amazon EBS         | Target storage volumes                 |
| AWS Lambda         | Executes optimization logic            |
| AWS Step Functions | Orchestrates the workflow              |
| Amazon EventBridge | Triggers the workflow on schedule      |
| Amazon DynamoDB    | Stores conversion history              |
| Amazon SNS         | Sends optimization notifications       |
| Amazon CloudWatch  | Stores Lambda logs and monitoring data |
| AWS IAM            | Provides secure access control         |
| Python             | Lambda automation code                 |
| Boto3              | AWS SDK for Python                     |

---

# Installation Steps

## Step 1: Create an EC2 Instance

Open the AWS Management Console and navigate to:

**EC2 → Instances → Launch Instance**

Launch a Linux-based EC2 instance.

Example configuration:

```text
Instance Type:
t3.micro

Region:
us-east-1
```

The EC2 instance will provide the EBS volume that will be used for testing.

---

## Step 2: Identify the EBS Volume

Navigate to:

**EC2 → Elastic Block Store → Volumes**

Select the EBS volume attached to the EC2 instance.

Check the current volume type.

For this project, the source volume should be:

```text
Volume Type:
gp2
```

Record the Volume ID.

Example:

```text
Volume ID:
vol-xxxxxxxxxxxxxxxxx
```

---

## Step 3: Add the AutoConvert Tag

Select the EBS volume and choose:

**Actions → Manage tags**

Add the following tag:

```text
Key:
AutoConvert

Value:
true
```

The Lambda function will use this tag to determine whether the volume is eligible for automatic conversion.

Only volumes satisfying both conditions should be modified:

```text
Volume Type = gp2
AND
AutoConvert = true
```

---

# Step 4: Create DynamoDB Table

Navigate to:

**AWS Console → DynamoDB → Tables → Create table**

Create a table named:

```text
EBS-Optimization-Logs
```

Use:

```text
Partition Key:
VolumeId

Data Type:
String
```

The table will store the history of optimized EBS volumes.

Example record:

```text
VolumeId:
vol-005cf3aa1e84e4838

InstanceId:
i-xxxxxxxxxxxxxxxxx

VolumeType:
gp2

Size:
8

Region:
us-east-1

Timestamp:
2026-08-13T12:00:00
```

---

# Step 5: Create SNS Topic

Navigate to:

**Amazon SNS → Topics → Create topic**

Select:

```text
Type:
Standard
```

Create the topic:

```text
EBS-Volume-Optimization-Notifications
```

---

## Step 6: Create SNS Subscription

Open the SNS topic and create a subscription.

Example:

```text
Protocol:
Email

Endpoint:
your-email@example.com
```

Confirm the subscription from the confirmation email sent by AWS SNS.

The SNS topic will be used to notify the user after an EBS volume is converted.

---

# Step 7: Create IAM Role for Lambda

Navigate to:

**IAM → Roles → Create role**

Select:

```text
Trusted Entity:
AWS Service

Use Case:
Lambda
```

The Lambda role should have permissions required to:

* Describe EBS volumes
* Modify EBS volumes
* Describe volume modifications
* Write CloudWatch logs
* Write records to DynamoDB
* Publish messages to SNS

For production environments, use resource-scoped permissions instead of broad permissions such as `AdministratorAccess`.

---

# Step 8: Create Filter Lambda

Navigate to:

**AWS Lambda → Functions → Create function**

Create a Python Lambda function.

Example:

```text
Function Name:
EBS-Filter-Volumes

Runtime:
Python 3.x
```

The function scans EBS volumes and identifies volumes that satisfy:

```text
VolumeType = gp2
AutoConvert = true
```

Example logic:

```python
import boto3

ec2 = boto3.client("ec2")


def lambda_handler(event, context):

    response = ec2.describe_volumes()

    eligible_volumes = []

    for volume in response["Volumes"]:

        volume_type = volume["VolumeType"]

        tags = {
            tag["Key"]: tag["Value"]
            for tag in volume.get("Tags", [])
        }

        auto_convert = tags.get("AutoConvert")

        if volume_type == "gp2" and auto_convert == "true":

            eligible_volumes.append({
                "VolumeId": volume["VolumeId"],
                "VolumeType": volume_type,
                "Size": volume["Size"],
                "Region": boto3.session.Session().region_name
            })

    print("Eligible volumes:", eligible_volumes)

    return {
        "Volumes": eligible_volumes
    }
```

The function returns the list of eligible volumes to Step Functions.

---

# Step 9: Create Conversion Lambda

Create another Lambda function:

```text
Function Name:
EBS-Convert-Volume
```

The function receives the Volume ID and converts the volume from `gp2` to `gp3`.

Example:

```python
import boto3

ec2 = boto3.client("ec2")


def lambda_handler(event, context):

    volume_id = event["VolumeId"]

    print(f"Checking volume: {volume_id}")

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

    print(f"Converting {volume_id} from gp2 to gp3")

    ec2.modify_volume(
        VolumeId=volume_id,
        VolumeType="gp3"
    )

    return {
        "VolumeId": volume_id,
        "PreviousType": "gp2",
        "NewType": "gp3",
        "Status": "MODIFICATION_STARTED"
    }
```

---

# Step 10: Verify Volume Modification

Create a Lambda function for verification:

```text
Function Name:
EBS-Verify-Volume
```

The function uses:

```python
ec2.describe_volume_modifications()
```

to check whether the conversion has completed.

Example verification logic:

```python
import boto3

ec2 = boto3.client("ec2")


def lambda_handler(event, context):

    volume_id = event["VolumeId"]

    response = ec2.describe_volume_modifications(
        VolumeIds=[volume_id]
    )

    modification = response["VolumesModifications"][0]

    state = modification["ModificationState"]

    print(f"Volume: {volume_id}")
    print(f"Modification State: {state}")

    return {
        "VolumeId": volume_id,
        "ModificationState": state
    }
```

Possible states include:

```text
modifying
optimizing
completed
failed
```

The Step Functions workflow can wait and check again if the modification is not yet complete.

---

# Step 11: Create DynamoDB Logging Lambda

Create:

```text
Function Name:
EBS-Log-Optimization
```

The function stores the conversion details in DynamoDB.

Example:

```python
import boto3
from datetime import datetime, timezone

dynamodb = boto3.resource("dynamodb")

table = dynamodb.Table("EBS-Optimization-Logs")


def lambda_handler(event, context):

    volume_id = event["VolumeId"]

    item = {
        "VolumeId": volume_id,
        "InstanceId": event.get("InstanceId", "N/A"),
        "VolumeType": event.get("PreviousType", "gp2"),
        "Size": event.get("Size", 0),
        "Region": boto3.session.Session().region_name,
        "Timestamp": datetime.now(timezone.utc).isoformat()
    }

    table.put_item(Item=item)

    print("Optimization logged:", item)

    return {
        "VolumeId": volume_id,
        "LogStatus": "SUCCESS"
    }
```

---

# Step 12: Create SNS Notification Lambda

Create:

```text
Function Name:
EBS-Send-Notification
```

The function publishes a message to the SNS topic.

Example:

```python
import boto3

sns = boto3.client("sns")

TOPIC_ARN = "YOUR_SNS_TOPIC_ARN"


def lambda_handler(event, context):

    volume_id = event["VolumeId"]
    status = event.get("Status", "SUCCESS")

    message = f"""
EBS Volume Optimization Result

Volume ID: {volume_id}

Previous Type: gp2

New Type: gp3

Status: {status}

Region: {boto3.session.Session().region_name}
"""

    sns.publish(
        TopicArn=TOPIC_ARN,
        Subject="EBS Volume Converted",
        Message=message
    )

    print("SNS notification sent")

    return {
        "VolumeId": volume_id,
        "NotificationStatus": "SENT"
    }
```

Replace:

```text
YOUR_SNS_TOPIC_ARN
```

with the ARN of your SNS topic.

---

# Step 13: Create Step Functions State Machine

Navigate to:

**AWS Step Functions → State machines → Create state machine**

Select:

```text
Workflow:
Standard
```

Step Functions will orchestrate the complete workflow.

The workflow can be structured as:

```text
Start
  |
  v
Filter Volumes
  |
  v
Check Eligible Volumes
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
  v
Log to DynamoDB
  |
  v
Send SNS Notification
  |
  v
Success
```

---

## Step 14: Configure Step Functions Workflow

A simplified Amazon States Language definition can be structured as follows:

```json
{
  "StartAt": "FilterVolumes",
  "States": {
    "FilterVolumes": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:REGION:ACCOUNT_ID:function:EBS-Filter-Volumes",
      "Next": "ConvertVolumes"
    },
    "ConvertVolumes": {
      "Type": "Map",
      "ItemsPath": "$.Volumes",
      "Iterator": {
        "StartAt": "ConvertVolume",
        "States": {
          "ConvertVolume": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:REGION:ACCOUNT_ID:function:EBS-Convert-Volume",
            "End": true
          }
        }
      },
      "Next": "LogOptimization"
    },
    "LogOptimization": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:REGION:ACCOUNT_ID:function:EBS-Log-Optimization",
      "Next": "SendNotification"
    },
    "SendNotification": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:REGION:ACCOUNT_ID:function:EBS-Send-Notification",
      "End": true
    }
  }
}
```

Replace:

```text
REGION
ACCOUNT_ID
```

with the appropriate AWS values.

---

# Step 15: Create EventBridge Scheduled Rule

Navigate to:

**Amazon EventBridge → Rules → Create rule**

Create a scheduled rule.

Example:

```text
Rule Name:
EBS-Optimization-Daily

Schedule:
Daily
```

Configure the Step Functions state machine as the target.

The workflow will then execute automatically according to the configured schedule.

---

# Step 16: Configure CloudWatch Logs

AWS Lambda automatically sends execution logs to Amazon CloudWatch when the Lambda execution role has the required logging permissions.

Navigate to:

**CloudWatch → Logs → Log groups**

Select the Lambda function log group.

Example:

```text
/aws/lambda/EBS-Filter-Volumes
/aws/lambda/EBS-Convert-Volume
/aws/lambda/EBS-Verify-Volume
/aws/lambda/EBS-Log-Optimization
/aws/lambda/EBS-Send-Notification
```

CloudWatch logs can be used to verify:

* Volume discovery
* Current volume type
* Conversion request
* Modification status
* DynamoDB logging
* SNS notification
* Errors

---

# Step 17: Test the Workflow

Before relying on the scheduled EventBridge rule, manually start the Step Functions execution.

Navigate to:

**Step Functions → State Machines → EBS Volume Optimization**

Click:

**Start execution**

Monitor each state.

Expected workflow:

```text
FilterVolumes
      ↓
ConvertVolumes
      ↓
Wait / Verify
      ↓
LogOptimization
      ↓
SendNotification
      ↓
Success
```

---

# Step 18: Verify EBS Conversion

Navigate to:

**EC2 → Volumes**

Select the optimized volume.

Verify:

```text
Previous Type:
gp2

New Type:
gp3
```

The volume should now show:

```text
Volume Type:
gp3
```

---

# Step 19: Verify DynamoDB Logs

Navigate to:

**DynamoDB → EBS-Optimization-Logs → Explore table items**

Verify that a record exists for the converted volume.

Example:

```text
VolumeId:
vol-005cf3aa1e84e4838

VolumeType:
gp2

Size:
8

Region:
us-east-1

Timestamp:
2026-08-13T...
```

This provides an audit trail of the optimization operation.

---

# Step 20: Verify SNS Notification

Check the email subscription associated with the SNS topic.

A successful notification should contain information similar to:

```text
EBS Volume Optimization Result

Volume ID: vol-005cf3aa1e84e4838

Previous Type: gp2

New Type: gp3

Status: COMPLETED

Progress: 100%

The EBS volume optimization workflow has completed.
```

---

# Step 21: Verify CloudWatch Logs

Open the CloudWatch log group for the Lambda function.

Verify that the Lambda execution contains messages such as:

```text
Checking volume: vol-005cf3aa1e84e4838

Current Type: gp2

Converting volume from gp2 to gp3

Modification State: completed

SNS notification sent
```

This confirms that the Lambda functions executed successfully.

---

# Project Structure

```text
Intelligent-EBS-Volume-Optimization/
│
├── README.md
│
├── architecture/
│   └── architecture-diagram.png
│
├── lambda/
│   ├── filter_volumes/
│   │   ├── lambda_function.py
│   │   └── requirements.txt
│   │
│   ├── convert_volume/
│   │   ├── lambda_function.py
│   │   └── requirements.txt
│   │
│   ├── verify_volume/
│   │   ├── lambda_function.py
│   │   └── requirements.txt
│   │
│   ├── log_optimization/
│   │   ├── lambda_function.py
│   │   └── requirements.txt
│   │
│   └── send_notification/
│       ├── lambda_function.py
│       └── requirements.txt
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
```

# Results

The project successfully demonstrated an automated EBS volume optimization workflow using AWS serverless services. The system identified EBS volumes using the `gp2` volume type and the `AutoConvert=true` tag, then initiated their conversion to `gp3`.

The Step Functions workflow successfully orchestrated the filtering, conversion, verification, logging, and notification stages. The EBS volume modification completed successfully, and the volume type changed from `gp2` to `gp3`.

The optimization activity was recorded in DynamoDB with details such as Volume ID, previous volume type, size, Region, and timestamp. An SNS notification was also generated to communicate the result of the optimization process. CloudWatch Logs provided execution details for monitoring and troubleshooting.

Example successful result:

```text
EBS Volume Optimization Result

Volume ID: vol-005cf3aa1e84e4838

Region: us-east-1

Previous Type: gp2

New Type: gp3

Status: COMPLETED

Progress: 100%
```

---

# Conclusion

The Intelligent EBS Volume Optimization project successfully demonstrated how multiple AWS serverless services can be combined to create an automated cloud infrastructure optimization solution.

AWS Lambda performed the EBS volume filtering and modification logic, while Step Functions orchestrated the workflow. EventBridge provided scheduled execution, DynamoDB maintained an audit trail, SNS provided notifications, CloudWatch provided monitoring and logging, and IAM ensured controlled access to AWS resources.

The project provided practical experience with event-driven architecture, serverless automation, AWS storage optimization, workflow orchestration, monitoring, notifications, database logging, and security best practices.

Overall, the solution demonstrates how repetitive cloud infrastructure tasks can be automated while maintaining visibility, auditability, and controlled access.



