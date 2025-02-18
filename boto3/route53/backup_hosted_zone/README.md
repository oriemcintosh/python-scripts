# Backup Route 53 Records

This script was written for the purpose of making a local backup of records with AWS' Route53. This was done for the purpose of having a local file with all the records, just in case records were deleted, a hosted zone was deleted, or there was a migration planned for DNS providers.

## How to use / modify the script

1. Collect the Hosted Zone ID from Route53
2. Assign the Hosted Zone ID to a system environment variable (`HOSTED_ZONE_ID`), which the program will read.
3. Ensure you have valid credentials for for your AWS command line profile and set it to an environment variable (`AWS_PROFILE`) or set temporary credentials as environment variables to interact with your AWS account.
4. Ensure that you have `boto3` installed, preferably in a [virtual environment](https://docs.python.org/3/library/venv.html)
5. Execute script. Linux example: `python3 backup_hosted_zone.py`

> [!IMPORTANT]  
> If you use temporary credentials instead of a profile for your AWS configuration, ensure to comment out `line 16` of the script.

> [!TIP]
> I have a linux script for setting up temporary credentials from the AWS CLI if you are inputting them manually on Linux system. You can find it [here](https://github.com/oriemcintosh/bash-scripts/tree/main/aws-cli-temp-config).
