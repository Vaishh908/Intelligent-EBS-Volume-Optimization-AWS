# Technical Report

## Intelligent EBS Volume Optimization Using Lambda, CloudWatch, SNS, DynamoDB & Step Functions

## Each Component and Its Role

| AWS Component | Role in the Project |
|---|---|
| **Amazon EC2** | Provides the Linux-based test environment where the EBS volume is attached. It is used to create and test the storage optimization workflow. |
| **Amazon EBS** | Provides the storage volume that is optimized. The project identifies eligible **gp2** volumes tagged with `AutoConvert=true` and converts them to **gp3**. |
| **AWS Lambda** | Performs the main automation tasks. Lambda functions filter eligible volumes, initiate the gp2-to-gp3 conversion, verify the modification status, store optimization details, and send notifications. |
| **AWS Step Functions** | Orchestrates the complete workflow by executing the Lambda functions in the required sequence. It provides a structured process for filtering, conversion, verification, logging, and notification. |
| **Amazon EventBridge** | Automatically starts the Step Functions workflow according to a configured schedule, allowing the optimization process to run without manual intervention. |
| **Amazon DynamoDB** | Maintains an audit trail of the optimization process. It stores information such as Volume ID, previous volume type, volume size, Region, and timestamp. |
| **Amazon SNS** | Sends notifications about the optimization result to the configured email subscription. It informs the user when the workflow has completed. |
| **Amazon CloudWatch** | Collects and stores Lambda execution logs. It helps monitor the workflow, check execution details, identify errors, and troubleshoot problems. |
| **AWS IAM** | Provides secure access control for the AWS resources used by the project. IAM roles allow Lambda functions to access only the services and actions required for their tasks. |
| **Python** | Used to write the Lambda automation functions that perform EBS filtering, conversion, verification, logging, and notification operations. |
| **Boto3** | AWS SDK for Python used by the Lambda functions to communicate with AWS services such as EC2/EBS, DynamoDB, and SNS. |

### Component Interaction

The components work together in the following sequence:

```text
Amazon EventBridge
        ↓
AWS Step Functions
        ↓
AWS Lambda
        ↓
Amazon EBS
        ↓
EBS Volume Conversion
        ↓
Verification
        ↓
Amazon DynamoDB
        ↓
Amazon SNS
        ↓
Notification

Amazon CloudWatch → Monitoring & Logs
AWS IAM           → Secure Access Control
```

## Security Best Practices Used

### 1. IAM Roles

The project uses AWS IAM roles to provide secure access to AWS resources. Lambda functions use an IAM execution role instead of storing AWS access keys or credentials directly in the Python code.

The IAM role provides the permissions required for the Lambda functions to:

- Describe EBS volumes
- Modify EBS volumes
- Check EBS volume modification status
- Write logs to CloudWatch
- Store optimization records in DynamoDB
- Publish notifications through SNS

### 2. Least-Privilege Access

The project follows the principle of least privilege. Each Lambda function should receive only the permissions required to perform its specific task.

For example:

- The filter Lambda needs permission to describe EBS volumes.
- The conversion Lambda needs permission to describe and modify EBS volumes.
- The logging Lambda needs permission to write to the DynamoDB table.
- The notification Lambda needs permission to publish to the SNS topic.

This reduces the risk of unauthorized actions if a function is compromised.

### 3. Scoped Permissions

Permissions should be restricted to the specific resources used by the project wherever possible.

For example, DynamoDB access can be scoped to:

```text
EBS-Optimization-Logs
```

SNS publishing permission can be restricted to:

```text
EBS-Volume-Optimization-Notifications
```

This provides better control over AWS resources.

### 4. Controlled EBS Modification

The automation does not modify every EBS volume. A volume must satisfy both conditions:

```text
Volume Type = gp2
        AND
AutoConvert = true
```

This acts as an additional safety control and prevents unintended modification of unrelated EBS volumes.

### 5. No Hard-Coded AWS Credentials

AWS credentials should not be stored inside Lambda source code. Lambda obtains temporary credentials through its IAM execution role.

This is safer than placing access keys directly in Python files.

### 6. CloudWatch Logging and Monitoring

CloudWatch Logs provide visibility into Lambda execution. Logs can be used to identify:

- Which volumes were detected
- Which volumes were modified
- Modification status
- Errors during execution
- DynamoDB logging activity
- SNS notification activity

This supports security monitoring and troubleshooting.

### 7. Audit Trail

DynamoDB maintains records of optimization activities, including the Volume ID, previous volume type, size, Region, and timestamp.

This provides an audit trail that can be reviewed to determine what storage optimization operations were performed.

## Any Real-World Challenges Simulated and How They Were Handled

### 1. Preventing Unintended EBS Volume Modification

**Challenge:**  
The automation could accidentally modify EBS volumes that were not intended for optimization.

**How it was handled:**  
The Lambda function checks two conditions before conversion:

```text
Volume Type = gp2
AND
AutoConvert = true
```

Only volumes satisfying both conditions are selected for conversion.

### 2. EBS Modification Takes Time

**Challenge:**  
Changing an EBS volume from `gp2` to `gp3` is not necessarily completed immediately. The volume can remain in states such as `modifying` or `optimizing`.

**How it was handled:**  
A separate verification Lambda checks the EBS modification status using:

```text
describe_volume_modifications()
```

The workflow can wait and check the status again until the modification reaches `completed` or `failed`.

### 3. Workflow Failure Detection

**Challenge:**  
In a multi-step automation process, identifying where a failure occurred can be difficult.

**How it was handled:**  
AWS Step Functions separates the process into individual workflow states:

```text
Filter
   ↓
Convert
   ↓
Verify
   ↓
Log
   ↓
Notify
```

This makes it easier to identify the specific stage where an error occurs.

### 4. Maintaining an Audit Trail

**Challenge:**  
Manual tracking of which EBS volumes were optimized can be difficult, especially when automation runs repeatedly.

**How it was handled:**  
DynamoDB stores optimization information such as:

```text
Volume ID
Previous Volume Type
Size
Region
Timestamp
```

This provides a persistent record of the optimization activity.

### 5. Notification After Completion

**Challenge:**  
The user may not know whether the automated optimization completed successfully.

**How it was handled:**  
Amazon SNS sends an email notification after the workflow completes, providing information about the optimized volume and its status.

### 6. Troubleshooting Automation Errors

**Challenge:**  
Lambda functions may encounter errors such as permission problems, invalid volume IDs, or AWS API failures.

**How it was handled:**  
CloudWatch Logs capture Lambda execution details and error messages. These logs can be reviewed to identify and troubleshoot problems.

### 7. Avoiding Repeated Manual Execution

**Challenge:**  
Running the optimization process manually every time is inefficient.

**How it was handled:**  
Amazon EventBridge triggers the Step Functions workflow on a configured schedule, allowing the optimization process to run automatically.

### 8. Excessive AWS Permissions

**Challenge:**  
Giving Lambda administrator-level permissions creates unnecessary security risk.

**How it was handled:**  
IAM roles and scoped permissions are used so that each Lambda function receives only the permissions required for its particular operation.
