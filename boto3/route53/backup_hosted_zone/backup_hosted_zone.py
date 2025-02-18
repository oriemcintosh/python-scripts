# This program is written to backup all records from a hosted zone in Route 53

import boto3
import json
import os

def backup_route53_records(hosted_zone_id):
    """
    Function to list record sets in a Route 53 Hosted Zone and save to a file.
    """
    
    # Select SSO profile for Boto3 client
    profile_name = os.environ['AWS_PROFILE']

    # Set SSO profile for Boto3 client
    session = boto3.Session(profile_name=profile_name)

    # Create Route 53 client
    route53 = boto3.client('route53')
    
    try:
        # Get all record sets
        paginator = route53.get_paginator('list_resource_record_sets')
        record_sets = []
        
        for page in paginator.paginate(HostedZoneId=hosted_zone_id):
            record_sets.extend(page['ResourceRecordSets'])

        # File name based on hosted zone ID
        file_name = f"route53_records_backup_{hosted_zone_id}.json"
        
        # Save to file
        with open(file_name, 'w') as f:
            json.dump({'ResourceRecordSets': record_sets}, f, indent=2)
            
        print(f"Successfully backed up {len(record_sets)} records to {file_name}")
        
    except Exception as e:
        print(f"Error backing up records: {str(e)}")

# Usage
hosted_zone_id = os.getenv('HOSTED_ZONE_ID')
backup_route53_records(hosted_zone_id)