import boto3
import click
import os

def create_bucket(name, access):
    """Create an S3 bucket with specified access level"""
    if access not in ['private', 'public']:
        click.secho("Invalid access level. Use 'private' or 'public'.", fg='red')
        return
    if access == 'public':
        choise = click.prompt("Are you sure that the s3 will be public? (yes/no)", type=str)
        if choise.lower() != 'yes':
            click.secho("Bucket creation aborted.", fg='yellow')
            return
    s3_client = boto3.client('s3', region_name='us-east-1')
    try:
        acl = 'public-read' if access.lower() == 'public' else 'private'
        s3_client.create_bucket(
            Bucket=name,
            ACL=acl)

        s3_client.put_bucket_tagging(
            Bucket=name,
            Tagging={
                'TagSet': [
                    {'Key': 'CreatedBy', 'Value': 'platform-cli'},
                    {'Key': 'Owner', 'Value': 'yoavvaknin'}
                ]
            }
        )
        
        click.secho(f"Created S3 bucket: {name} with {access} access", fg='green', bold=True)
            
    except Exception as e:
        click.secho(f"AWS Error: {e}", fg='red')
        


def upload_file_bucket(bucket_name, file_path):
    """Upload a file to the specified S3 bucket"""
    s3_client = boto3.client('s3', region_name='us-east-1')
    object_name = os.path.basename(file_path)
    
    try:
        if not os.path.exists(file_path):
            click.secho(f"Error: File not found at {file_path}", fg='red')
            return
        click.echo(f"Uploading {object_name} to {bucket_name}...")
        s3_client.upload_file(file_path, bucket_name, object_name)
        click.secho(f"Successfully uploaded to S3!", fg='green', bold=True)
        
    except Exception as e:
        click.secho(f"AWS Error: {e}", fg='red') 
    
        
def list_buckets():
    """List S3 buckets created by the CLI"""
    s3_client = boto3.client('s3', region_name='us-east-1')
    found_managed_bucket = False
    
    try:
        response = s3_client.list_buckets()
        buckets = response.get('Buckets', [])
        if not buckets:
            click.secho("No S3 buckets found in your AWS account.", fg='yellow')
            return
        click.secho("Managed S3 Buckets:", fg='cyan', bold=True)

        for bucket in buckets:
            bucket_name = bucket['Name']
            try:
                tagging = s3_client.get_bucket_tagging(Bucket=bucket_name)
                tags = {tag['Key']: tag['Value'] for tag in tagging.get('TagSet', [])}
                
                if tags.get('CreatedBy') == 'platform-cli':
                    click.secho(f"{bucket_name} | Owner: {tags.get('Owner', 'unknown')}", fg='yellow')
                    found_managed_bucket = True 

            except s3_client.exceptions.ClientError as e:

                if e.response['Error']['Code'] == 'NoSuchTagSet':
                    continue
                else:
                    click.echo(f"Could not read tags for {bucket_name}: {e}")
        
        if not found_managed_bucket:
            click.secho("No S3 buckets found that were created by this CLI.", fg='yellow')

    except Exception as e:
        click.secho(f"AWS Error: {e}", fg='red')