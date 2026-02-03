import boto3
import click
import os

def create_bucket(name, access):
    """Create an S3 bucket with specified access level"""
    if access not in ['private', 'public']:
        click.secho("Invalid access level. Use 'private' or 'public'.", fg='red')
        return
    elif access == 'public':
        choise = click.prompt("Are you sure that the s3 will be public? (yes/no)", type=str)
        if choise.lower() == 'no':
            click.secho("Bucket creation aborted.", fg='yellow')
            return
        elif access != 'yes':
            click.secho("Invalid choice. Bucket creation aborted.", fg='red')
            return
    s3_client = boto3.client('s3', region_name='us-east-1')
    try:
        if access.lower() == 'public':
            acl = 'public-read'
        else:
            acl = 'private'
        
        s3_client.create_bucket(
            Bucket=name,
            ACL=acl,
            CreateBucketConfiguration={'LocationConstraint': 'us-east-1'}
        )
        click.secho(f" Created S3 bucket: {name} with {access} access", fg='green', bold=True)
        
    except Exception as e:
        click.secho(f" AWS Error: {e}", fg='red')
        


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
    """List all S3 buckets"""
    s3_client = boto3.client('s3', region_name='us-east-1')
    try:
        response = s3_client.list_buckets()
        buckets = response.get('Buckets', [])
        
        if not buckets:
            click.secho("No S3 buckets found.", fg='yellow')
            return
        
        click.secho("S3 Buckets:", fg='cyan', bold=True)
        for bucket in buckets:
            click.echo(f" - {bucket['Name']}")
            
    except Exception as e:
        click.secho(f"AWS Error: {e}", fg='red')               