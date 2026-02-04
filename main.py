import click
from EC2 import create_instance, list_instances, manage_instance
from S3 import create_bucket, upload_file_bucket, list_buckets
from Route53 import create_hosted_zone, manage_hosted_records, list_hosted_zones
@click.group()
def cli():
    """Platform Engineering CLI - Resource Management Tool"""
    pass

@cli.group(name="ec2")
def ec2_group():
    """Manage EC2 instances"""
    pass

@ec2_group.command(name="create")
@click.option('--name', default='', help="Name of the instance")
@click.option('--type', default='', help='Type of EC2 instance')
@click.option('--ami', default='', help='EC2 AMI latest Ubuntu or latest Amazon Linux')
@click.option('--count', default=1, help='Number of instances to create')
def create_ec2(name, type, ami, count):
    create_instance(name, type, ami, count)

@ec2_group.command(name="manage")
@click.option('--name', default='', help="Name of the instance")
@click.option('--action', default='', help='start or stop instance')
def manage_ec2(name, action):
    manage_instance(name, action)
    
@ec2_group.command(name="list")
def list_ec2():
    list_instances()

@cli.group(name="s3")
def s3_group():
    """Manage S3 buckets"""
    pass

@s3_group.command(name="create")
@click.option('--name', default='', help="Name of the S3 bucket")
@click.option('--access', help='Access level: private or public') 
def create_s3(name, access):
    create_bucket(name, access) 

@s3_group.command(name="upload_file")
@click.option('--name', default='', help="Name of the S3 bucket")
@click.option('--file_path', default='', help="Path to the file to upload")
def upload_file_s3(name, file_path):
    upload_file_bucket(name, file_path)

@s3_group.command(name="list")
def list_s3():
    list_buckets()   
    
@cli.group(name="route53")  
def route53_group():
    """Manage Route53 DNS"""
    pass

@route53_group.command(name="create_zone")
@click.option('--domain', default='', help="Domain name for the hosted zone")
def create_route53_zone(domain):
    create_hosted_zone(domain)

@route53_group.command(name="manage_records")
@click.option('--domain', default='', help="Domain name for the hosted zone")
@click.option('--ip_address', default='', help="IP address for the record")
@click.option('--action', default='', help='Create, update, or delete DNS records')
def manage_route53_records(domain, ip_address, action):
    manage_hosted_records(domain, ip_address, action)
    
@route53_group.command(name="list")
def list_route53_zones():
      list_hosted_zones() 
        
if __name__ == '__main__':
    cli()