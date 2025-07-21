# IAM User Access Key Creation & Rotation Script

This Python script automates the creation and rotation of AWS IAM user access keys, storing them securely in AWS Secrets Manager. It is designed to work alongside Terraform or IaC-managed IAM users and Secrets Manager secrets.

## Features

- Checks for existing IAM user access keys.
- Creates new access keys if none exist or if existing keys are older than 90 days.
- Stores new access keys in AWS Secrets Manager.
- Optionally deletes old access keys after rotation.

## Prerequisites

- Python 3.x
- [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) library installed (`pip install boto3`)
- Existing IAM user and Secrets Manager secret (can be provisioned via Terraform or other IaC)
- AWS credentials configured (via environment variables or AWS CLI profile)

## Environment Variables

Set the following environment variables before running the script:

- `IAM_USER_NAME`: The IAM user name to manage access keys for.
- `SECRET_NAME`: The name or ARN of the AWS Secrets Manager secret to store the access keys.

## Usage

1. Install dependencies:
    ```sh
    pip install boto3
    ```
2. Set environment variables:
    ```sh
    export IAM_USER_NAME=your_iam_user
    export SECRET_NAME=your_secret_name
    ```
3. Run the script:
    ```sh
    python3 iam_user_access_key_creation.py
    ```

## How It Works

- The script checks the IAM user's existing access keys.
- If no keys exist, it creates a new access key and stores it in Secrets Manager.
- If any key is older than 90 days, it creates a new key, stores it, and deletes the old key(s).
- If all keys are less than 90 days old, no action is taken.

## Notes

- Ensure the IAM user has permissions to manage access keys and update Secrets Manager.
- Use this script as part of your key rotation and security best practices.
