# Python Boto3 script to create IAM user access keys and store it in Secrets 
# Manager. The script checks if the user has existing access keys, creates new
# ones if necessary, based on how old the keys are. The keys are then stored
# in AWS Secrets Manager. The assumption is that there is already an IAM user
# created and there is a Secrets Manager secret to store the keys.
# This was originally used along with Terraform as a helper script to manage
# IAM user access keys for a user that was created using Terraform and a
# Secrets Manager secret that was also created using Terraform.

import boto3
import os
from datetime import datetime, timedelta

# Initialize Boto3 clients
iam_client = boto3.client('iam')
secrets_manager_client = boto3.client('secretsmanager')

# Get environment variables
iam_user_name = os.getenv('IAM_USER_NAME')
secret_name = os.getenv('SECRET_NAME')

def get_user_access_keys(user_name):
    response = iam_client.list_access_keys(UserName=user_name)
    return response['AccessKeyMetadata']

def create_access_key(user_name):
    response = iam_client.create_access_key(UserName=user_name)
    return response['AccessKey']

def store_secret(access_key_id, secret_access_key, secret_name):
    secret_value = {
        'AccessKeyId': access_key_id,
        'SecretAccessKey': secret_access_key
    }
    secrets_manager_client.put_secret_value(
        SecretId=secret_name,
        SecretString=str(secret_value)
    )

def main():
    # Get the current date
    current_date = datetime.utcnow()

    # Get the user's access keys
    access_keys = get_user_access_keys(iam_user_name)

    # Check if the user has any access keys
    if not access_keys:
        # Create new access keys
        new_access_key = create_access_key(iam_user_name)
        store_secret(new_access_key['AccessKeyId'], new_access_key['SecretAccessKey'], secret_name)
        print(f"New access keys created and stored in Secrets Manager for user {iam_user_name}")
    elif any((current_date - key['CreateDate']) > timedelta(days=90) for key in access_keys):
        # Create new access keys
        new_access_key = create_access_key(iam_user_name)
        store_secret(new_access_key['AccessKeyId'], new_access_key['SecretAccessKey'], secret_name)
        print(f"New access keys created and stored in Secrets Manager for user {iam_user_name}")
        # Optionally, you can delete the old access keys
        for key in access_keys:
            if (current_date - key['CreateDate']) > timedelta(days=90):
                iam_client.delete_access_key(
                    UserName=iam_user_name,
                    AccessKeyId=key['AccessKeyId']
                )
                print(f"Old access key {key['AccessKeyId']} deleted for user {iam_user_name}")
    else:
        print(f"No action needed for user {iam_user_name} as the access keys are less than 90 days old")

if __name__ == "__main__":
    main()
